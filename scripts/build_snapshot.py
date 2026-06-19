"""
build_snapshot.py
The orchestrator. Combines manual holdings + live prices + crypto balances + FX into:
  - data/latest.json   (full current state, read by the dashboard)
  - data/history.csv    (one row per day -> day-on-day return)
  - data/snapshots/YYYY-MM-DD.json (archive)

Everything is normalised to the base currency (USD), with SGD + VND also computed.

Working skeleton — finish + test in Claude Code (phase 1). It runs end-to-end once
holdings.csv has real rows and (optionally) crypto keys are set.
"""
from __future__ import annotations
import csv
import json
import datetime as dt
from pathlib import Path

import fetch_prices as fp
import sync_crypto as sc

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SNAPSHOTS = DATA / "snapshots"


def _num(x) -> float:
    """Parse numbers that may contain $, commas or surrounding spaces. '' -> 0.0."""
    if x is None:
        return 0.0
    s = str(x).replace("$", "").replace(",", "").strip()
    return float(s) if s else 0.0


def _psource(h: dict) -> str:
    """Normalise price_source; blank defaults to yfinance (equities/ETFs)."""
    s = (h.get("price_source") or "").strip().lower()
    return s or "yfinance"


def load_config() -> dict:
    return json.loads((DATA / "config.json").read_text())


def load_holdings() -> list[dict]:
    with (DATA / "holdings.csv").open() as f:
        return list(csv.DictReader(f))


def to_base_ccy(amount: float, ccy: str, base: str, fx: dict[str, float]) -> float:
    """Convert `amount` in `ccy` to `base` using fx pairs keyed as BASE+QUOTE (e.g. USDSGD)."""
    if ccy == base:
        return amount
    # fx[f"{base}{ccy}"] = units of ccy per 1 base  -> divide to go ccy -> base
    pair = f"{base}{ccy}"
    if pair in fx and fx[pair]:
        return amount / fx[pair]
    raise ValueError(f"missing FX to convert {ccy}->{base} (need pair {pair})")


def build() -> dict:
    cfg = load_config()
    base = cfg["base_currency"]
    holdings = load_holdings()

    # --- prices ---
    eq_tickers = [h["ticker"] for h in holdings if _psource(h) == "yfinance"]
    cg_ids = [h["ticker"] for h in holdings if _psource(h) == "coingecko"]
    fx = fp.get_fx_rates(cfg["fx_pairs"])
    eq_prices = fp.get_equity_prices(eq_tickers)
    cg_prices = fp.get_crypto_prices(cg_ids, cfg.get("coingecko_vs_currency", "usd"))

    positions = []
    for h in holdings:
        qty = _num(h["quantity"])
        src = _psource(h)
        if src == "yfinance":
            price = eq_prices.get(h["ticker"])
            price_ccy = h.get("price_ccy") or base
            value = (price or 0) * qty
        elif src == "coingecko":
            price = cg_prices.get(h["ticker"])
            price_ccy = cfg.get("coingecko_vs_currency", "usd").upper()
            value = (price or 0) * qty
        elif src == "manual":
            price = _num(h["manual_price"])
            price_ccy = h.get("price_ccy") or h.get("cost_ccy") or base
            value = price * qty
        else:
            print(f"[warn] unknown price_source '{src}' for {h['ticker']}")
            continue

        value_base = to_base_ccy(value, price_ccy, base, fx)

        # --- cost basis + unrealised P&L (USD), Phase 2 ---
        # cost = unit_cost * quantity in the row's cost_ccy, converted to base via live FX.
        unit_cost = _num(h.get("unit_cost"))
        cost_ccy = (h.get("cost_ccy") or base).strip().upper() or base
        cost_base = to_base_ccy(unit_cost * qty, cost_ccy, base, fx)
        gain_loss = value_base - cost_base
        gain_loss_pct = (gain_loss / cost_base * 100) if cost_base else None

        positions.append({
            "ticker": h["ticker"],
            "label": h["label"],
            "asset_class": h["asset_class"],
            "platform": h["platform"],
            "quantity": qty,
            "price": price,
            "price_ccy": price_ccy,
            "value_base": round(value_base, 2),
            "cost_base": round(cost_base, 2),
            "gain_loss": round(gain_loss, 2),
            "gain_loss_pct": round(gain_loss_pct, 2) if gain_loss_pct is not None else None,
        })

    # --- crypto from exchanges (auto-sync): DORMANT while crypto_exchanges is empty ---
    # Manual CoinGecko-priced rows cover Kraken/Gemini/Crypto.com for now. To switch the
    # read-only ccxt sync back on, re-add exchange ids to config crypto_exchanges.
    exchanges = cfg.get("crypto_exchanges", [])
    if exchanges:
        # TODO: price each exchange asset (map ticker->coingecko id), convert to base,
        #   and append to `positions` with platform = exchange name.
        _ = sc.sync_all(exchanges)

    # --- totals + aggregate unrealised P&L (USD) ---
    total_base = round(sum(p["value_base"] for p in positions), 2)
    total_cost = round(sum(p["cost_base"] for p in positions), 2)
    total_gain_loss = round(total_base - total_cost, 2)
    total_gain_loss_pct = round(total_gain_loss / total_cost * 100, 2) if total_cost else None

    # multi-currency headline
    totals = {base: total_base}
    for disp in cfg["display_currencies"]:
        if disp == base:
            continue
        pair = f"{base}{disp}"
        totals[disp] = round(total_base * fx[pair], 2) if fx.get(pair) else None

    snapshot = {
        "as_of": dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
        "base_currency": base,
        "totals": totals,
        "pnl": {
            "base_currency": base,
            "total_cost": total_cost,
            "total_value": total_base,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_pct": total_gain_loss_pct,
        },
        "fx": fx,
        "positions": positions,
    }
    return snapshot


def write_outputs(snapshot: dict) -> None:
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    (DATA / "latest.json").write_text(json.dumps(snapshot, indent=2))
    today = dt.date.today().isoformat()
    (SNAPSHOTS / f"{today}.json").write_text(json.dumps(snapshot, indent=2))

    # append/overwrite today's row in history.csv
    hist = DATA / "history.csv"
    base = snapshot["base_currency"]
    row = {"date": today, f"total_{base}": snapshot["totals"][base]}
    rows = []
    if hist.exists():
        rows = [r for r in csv.DictReader(hist.open()) if r["date"] != today]
    rows.append(row)
    rows.sort(key=lambda r: r["date"])
    with hist.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", f"total_{base}"])
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    snap = build()
    write_outputs(snap)
    print(f"Total ({snap['base_currency']}): {snap['totals']}")
    print(f"Wrote {DATA/'latest.json'} and updated {DATA/'history.csv'}")
