# Portfolio Tracker

One dashboard for investments spread across Syfe (equities/ETFs) and Crypto.com / Kraken /
Gemini (crypto). Free, partially automated, self-hosted, and built to look good — not like a
spreadsheet.

- **Headline currency:** USD (also shows SGD + VND)
- **Data:** Python fetches prices/FX + crypto balances on a schedule (GitHub Actions, free)
- **Dashboard:** React + Tailwind, hosted free on Vercel

## Quick map
```
portfolio-tracker/
├── PROJECT_PLAN.md         ← architecture, phases, design direction (read this first)
├── SETUP_CHECKLIST.md      ← step-by-step setup for Huy (do this first)
├── data/
│   ├── holdings.csv        ← YOUR manual positions (Syfe). Edit this.
│   ├── config.json         ← base/display currencies, exchanges
│   ├── history.csv         ← daily value log (generated)
│   └── snapshots/          ← per-day snapshots (generated)
├── scripts/
│   ├── requirements.txt
│   ├── fetch_prices.py     ← equity/ETF prices + FX (yfinance, CoinGecko)
│   ├── sync_crypto.py      ← Kraken/Gemini read-only balances (ccxt)
│   └── build_snapshot.py   ← merges everything → data/latest.json + history.csv
├── .github/workflows/
│   └── update.yml          ← daily cron: run scripts, commit data
├── web/                    ← React dashboard (built in Claude Code)
├── .env.example            ← shape of API keys (copy to .env, never commit .env)
└── .gitignore
```

## Run the data layer locally
```bash
cd scripts
python -m pip install -r requirements.txt
python build_snapshot.py        # writes ../data/latest.json and appends ../data/history.csv
```

## Status
Scaffold only. The Python files are working skeletons with clear TODOs; the React dashboard is
not built yet. Continue in Claude Code following `PROJECT_PLAN.md`.

> Not financial advice — this is a personal tracking tool. Figures depend on free data sources
> and may be delayed or indicative.
