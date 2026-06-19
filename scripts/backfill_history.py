"""
backfill_history.py
Daily-close price history per holding -> data/prices/<ticker>.csv  (columns: date, close in USD).

Source: yfinance. Equities/ETFs use the holding's ticker directly; crypto maps its CoinGecko id to
the Yahoo "<SYM>-USD" pair. History starts at each security's listing (or ~7 years ago, whichever is
later). Cash is skipped.

Modes:
  (default / --full) : fetch ~7 years and overwrite each file.
  --update           : fetch the last ~10 days and append only dates not already stored
                       (cheap; used by the daily GitHub Action).
"""
from __future__ import annotations
import csv
import sys
import time
import datetime as dt
from pathlib import Path

import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PRICES = DATA / "prices"

# CoinGecko id (used for live prices) -> Yahoo Finance history symbol
CRYPTO_YF = {
    "bitcoin": "BTC-USD",
    "ethereum": "ETH-USD",
    "crypto-com-chain": "CRO-USD",
    "solana": "SOL-USD",
    "polkadot": "DOT-USD",
    "ripple": "XRP-USD",
}

YEARS = 7


def load_holdings() -> list[dict]:
    with (DATA / "holdings.csv").open() as f:
        return list(csv.DictReader(f))


def yf_symbol(h: dict) -> str | None:
    if (h.get("asset_class") or "").strip().lower() == "cash":
        return None
    src = (h.get("price_source") or "").strip().lower()
    if src == "coingecko":
        return CRYPTO_YF.get(h["ticker"])
    return (h.get("ticker") or "").strip() or None


def fetch_closes(symbol: str, *, start: str | None = None, period: str | None = None):
    """Return [(date_iso, close_float)] for a symbol, oldest first."""
    hist = yf.Ticker(symbol).history(start=start, period=period, auto_adjust=True)
    if hist.empty:
        return []
    return [(ts.date().isoformat(), round(float(c), 6)) for ts, c in hist["Close"].dropna().items()]


def read_existing(path: Path):
    if not path.exists():
        return []
    with path.open() as f:
        return [(r["date"], r["close"]) for r in csv.DictReader(f)]


def write_rows(path: Path, rows) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "close"])
        w.writerows(rows)


def main() -> None:
    update = "--update" in sys.argv
    PRICES.mkdir(parents=True, exist_ok=True)
    start = (dt.date.today() - dt.timedelta(days=365 * YEARS + 3)).isoformat()

    done: set[str] = set()
    for h in load_holdings():
        key = (h.get("ticker") or "").strip()
        sym = yf_symbol(h)
        if not sym or key in done:
            continue
        done.add(key)
        path = PRICES / f"{key}.csv"
        try:
            if update and path.exists():
                existing = read_existing(path)
                have = {d for d, _ in existing}
                new = [(d, str(c)) for d, c in fetch_closes(sym, period="10d") if d not in have]
                if new:
                    rows = sorted(existing + new, key=lambda r: r[0])
                    write_rows(path, rows)
                    print(f"[update] {key}: +{len(new)} -> {len(rows)} rows")
                else:
                    print(f"[update] {key}: up to date")
            else:
                rows = [(d, str(c)) for d, c in fetch_closes(sym, start=start)]
                if rows:
                    write_rows(path, rows)
                    print(f"[full] {key} ({sym}): {len(rows)} rows {rows[0][0]}..{rows[-1][0]}")
                else:
                    print(f"[warn] {key} ({sym}): no history returned")
        except Exception as e:  # noqa: BLE001
            print(f"[error] {key} ({sym}): {e}")
        time.sleep(0.2)


if __name__ == "__main__":
    main()
