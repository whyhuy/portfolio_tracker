"""
sync_crypto.py
Pull READ-ONLY crypto balances from exchanges via ccxt (one library, many exchanges).

Supports Kraken + Gemini now; add Crypto.com Exchange ('cryptocom') if you use it.
Keys come from environment variables (.env locally, GitHub Secrets in CI).

SECURITY: use read-only keys only. This script never trades or withdraws.

Working skeleton — verify against your real keys in Claude Code (phase 2).
"""
from __future__ import annotations
import os
import ccxt
from dotenv import load_dotenv

load_dotenv()

# exchange id -> (env key name, env secret name)
EXCHANGES = {
    "kraken":   ("KRAKEN_API_KEY", "KRAKEN_API_SECRET"),
    "gemini":   ("GEMINI_API_KEY", "GEMINI_API_SECRET"),
    "cryptocom": ("CRYPTOCOM_API_KEY", "CRYPTOCOM_API_SECRET"),
}


def fetch_exchange_balances(exchange_id: str) -> dict[str, float]:
    """Return {ASSET: amount} of non-zero balances for one exchange."""
    key_env, secret_env = EXCHANGES[exchange_id]
    api_key, secret = os.getenv(key_env), os.getenv(secret_env)
    if not api_key or not secret:
        print(f"[skip] {exchange_id}: no keys set")
        return {}

    klass = getattr(ccxt, exchange_id)
    client = klass({"apiKey": api_key, "secret": secret, "enableRateLimit": True})
    balance = client.fetch_balance()
    totals = balance.get("total", {})
    return {asset: float(amt) for asset, amt in totals.items() if amt and float(amt) > 0}


def sync_all(exchange_ids: list[str]) -> dict[str, dict[str, float]]:
    """Return {exchange_id: {ASSET: amount}}."""
    out: dict[str, dict[str, float]] = {}
    for ex in exchange_ids:
        if ex not in EXCHANGES:
            print(f"[warn] unknown exchange '{ex}' — skipping")
            continue
        try:
            out[ex] = fetch_exchange_balances(ex)
        except Exception as e:  # noqa: BLE001
            print(f"[error] {ex}: {e}")
            out[ex] = {}
    return out


# TODO (Claude Code): map exchange asset tickers (BTC, ETH, ...) to CoinGecko ids
#   so prices can be fetched. A small dict or CoinGecko's /coins/list will do.

if __name__ == "__main__":
    from pprint import pprint
    pprint(sync_all(["kraken", "gemini"]))
