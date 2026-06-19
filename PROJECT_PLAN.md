# Portfolio Tracker — Project Plan

A free, partially-automated, self-hosted dashboard that compiles Huy's investments across
platforms (Syfe equities/ETFs + Crypto.com / Kraken / Gemini crypto) into one beautiful view
and tracks day-to-day return.

## Decisions locked in
- **Presentation:** custom web app — React + Tailwind, hosted free on Vercel.
- **Base currency:** USD (headline). Also display SGD and VND.
- **Crypto:** entered manually for now (quantity + cost), priced **live via CoinGecko** —
  Kraken, Gemini and Crypto.com App all handled the same way. Read-only API auto-sync code is
  kept but dormant and can be switched on later. (Crypto.com App has no API regardless.)
- **Equities/ETFs:** Syfe has no public API → manual holdings file. Prices still auto-fetched.
- **Cost:** everything free. No paid data feeds, no paid hosting.

## Architecture (two layers)

```
                 ┌─────────────────────────────────────────┐
                 │  DATA LAYER  (Python, runs on schedule)   │
                 │                                           │
  holdings.csv ──┤  fetch_prices.py   → equity/ETF + FX      │
  (manual, Syfe) │  sync_crypto.py    → Kraken/Gemini (ccxt) │
                 │  build_snapshot.py → merge + normalise USD │
                 └───────────────┬───────────────────────────┘
                                 │ writes
                                 ▼
                    data/latest.json   (current state)
                    data/history.csv   (daily value log → returns)
                                 │ committed by GitHub Actions (free cron)
                                 ▼
                 ┌─────────────────────────────────────────┐
                 │  PRESENTATION LAYER  (React, on Vercel)   │
                 │  reads latest.json + history.csv          │
                 │  cards · allocation donut · value line ·  │
                 │  daily return · per-holding sparklines    │
                 └─────────────────────────────────────────┘
```

The magic that makes it free + automatic: **GitHub Actions** runs the Python on a daily cron,
commits the refreshed data files, and Vercel auto-redeploys the dashboard from the repo. No
server to run or pay for.

## Data model
- `data/holdings.csv` — manual positions (Syfe equities/ETFs, managed portfolios, any manual
  crypto). One row per position. `price_source` decides how it's priced.
- `data/config.json` — base currency, display currencies, FX pairs, exchange list.
- Crypto from exchanges is fetched live each run (not stored as holdings) and merged at build time.
- `data/latest.json` — full current snapshot the dashboard reads.
- `data/history.csv` — one row per day: total value (USD) + per-asset-class breakdown. This is
  what produces the day-on-day return.

## Gain/Loss (P&L) tracking — core requirement
Huy's main goal: effortlessly see how much each investment, and the book overall, is up or down.
For every position, compute in USD:
- **cost basis** = unit_cost × quantity (convert cost_ccy → USD via FX)
- **current value** (already computed)
- **unrealised gain/loss** = current value − cost basis, shown as both **$ and %**
Aggregate to total cost, total value, and total unrealised P&L ($ and %). Surface all of it in
`latest.json` and prominently in the dashboard (green/red), per position and overall.
Requires an accurate `unit_cost` on every row — keep cost figures clean (no $/commas).

## Build phases
1. **Data layer (do first, in Claude Code).** Get `build_snapshot.py` producing a correct
   `latest.json` from `holdings.csv` + live prices + FX. Test locally before anything else.
2. **Gain/Loss.** Compute per-position and total cost basis, value, and unrealised P&L ($ and %)
   in `build_snapshot.py`; expose in `latest.json`. (Crypto-API auto-sync deferred — manual rows
   priced via CoinGecko for now; see the Crypto note above.)
3. **Automation.** Turn on the GitHub Actions cron; confirm it commits a daily snapshot.
4. **Frontend.** Build the React + Tailwind dashboard against `latest.json`. This is where the
   "beautiful" work happens — see Design direction below.
5. **Deploy.** Push to Vercel (free), connect the repo, done.

## Design direction (the "beautiful" part)
Reference feel: Kubera, Copilot Money, Sharesight. Not a spreadsheet.
- Dark theme, generous spacing, card-based layout, strong typography.
- Headline: total value (USD) with the day's change in green/red and a small sparkline.
- Allocation donut (by asset class and by platform).
- Portfolio value line chart over time, with a daily-return strip beneath.
- Per-holding cards/rows with mini sparklines and gain/loss colour coding.
- Currency toggle: USD / SGD / VND.
- Chart libraries to consider: Recharts (simplest with React) or ApexCharts (richer).

## Security
- Exchange API keys are **read-only**. Never enable trading/withdrawal permissions.
- Keys live in a local `.env` (gitignored) and in GitHub repo **Secrets** for the Action.
- Never commit `.env` or any real key. `.env.example` shows the shape only.

## Honest limitations
- "Live" = refreshed on a schedule (daily is enough for daily-return tracking; can go hourly).
  The dashboard also fetches fresh prices on open so it feels current.
- Syfe and Crypto.com App stay manual until/unless an export or Exchange API is available.
- VND is a managed currency; FX rates are indicative.
