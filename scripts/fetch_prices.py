"""
fetch_prices.py
Fetch live-ish prices for manual holdings + FX rates.

Sources (all free):
- yfinance   : equities / ETFs (and FX pairs like USDSGD=X)
- CoinGecko  : crypto spot prices (no API key needed)

This is a working skeleton. Build/verify it in Claude Code (phase 1). TODOs mark the spots
most likely to need attention.
"""
from __future__ import annotations
import time
import requests
import yfinance as yf

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"


def _last_price_single(ticker: str) -> float | None:
    """Per-ticker price fallback. Avoids the bulk-download tz-cache lock that can
    silently drop tickers from yf.download when run multi-threaded."""
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="5d")
        if not hist.empty:
            return float(hist["Close"].dropna().iloc[-1])
        fi = tk.fast_info  # last resort
        px = fi.get("last_price") or fi.get("previous_close")
        return float(px) if px else None
    except Exception as e:  # noqa: BLE001
        print(f"[warn] single fetch failed for {ticker}: {e}")
        return None


def get_equity_prices(tickers: list[str]) -> dict[str, float]:
    """Latest price per ticker via yfinance. Returns {ticker: price_in_native_ccy}.

    Bulk-downloads first (fast), then fills any gaps one ticker at a time so a single
    flaky symbol or a tz-cache lock never drops a position from the snapshot.
    """
    prices: dict[str, float] = {}
    if not tickers:
        return prices
    # threads=False serialises the tz-cache access -> avoids "database is locked".
    try:
        data = yf.download(tickers, period="2d", progress=False, threads=False)
        close = data["Close"]
        for t in tickers:
            try:
                series = close[t] if hasattr(close, "columns") else close
                prices[t] = float(series.dropna().iloc[-1])
            except Exception:  # noqa: BLE001
                pass  # handled by the per-ticker fallback below
    except Exception as e:  # noqa: BLE001
        print(f"[warn] bulk download failed ({e}); falling back to per-ticker")

    missing = [t for t in tickers if t not in prices]
    for t in missing:
        px = _last_price_single(t)
        if px is not None:
            prices[t] = px
        else:
            print(f"[warn] no price for {t}")
    return prices


def get_crypto_prices(coingecko_ids: list[str], vs_currency: str = "usd") -> dict[str, float]:
    """Spot prices from CoinGecko. ids are CoinGecko ids e.g. 'bitcoin', 'ethereum'."""
    if not coingecko_ids:
        return {}
    params = {"ids": ",".join(coingecko_ids), "vs_currencies": vs_currency}
    r = requests.get(COINGECKO_URL, params=params, timeout=20)
    r.raise_for_status()
    raw = r.json()
    return {cid: float(v[vs_currency]) for cid, v in raw.items()}


def get_fx_rates(pairs: list[str]) -> dict[str, float]:
    """
    FX via yfinance. pairs like 'USDSGD' -> yfinance ticker 'USDSGD=X'.
    Returns {pair: rate} where rate is units of quote per 1 unit of base (USDSGD = SGD per USD).
    """
    rates: dict[str, float] = {}
    for pair in pairs:
        yf_ticker = f"{pair}=X"
        try:
            hist = yf.Ticker(yf_ticker).history(period="2d")
            rates[pair] = float(hist["Close"].dropna().iloc[-1])
        except Exception as e:  # noqa: BLE001
            print(f"[warn] no FX for {pair}: {e}")
        time.sleep(0.2)
    return rates


if __name__ == "__main__":
    print("equities:", get_equity_prices(["VOO", "AAPL"]))
    print("crypto:", get_crypto_prices(["bitcoin", "ethereum"]))
    print("fx:", get_fx_rates(["USDSGD", "USDVND"]))
