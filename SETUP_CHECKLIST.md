# Setup Checklist — what you (Huy) need to do

Work top to bottom. Everything here is free. Tick each box as you go.
None of this requires writing code — Claude Code will do the building once the accounts and
keys exist.

## 1. Accounts (one-time, ~15 min)
- [ ] **GitHub account** — https://github.com/signup. This gives you the code repo, the free
      scheduler (Actions), and free hosting hooks. Note your username.
- [ ] **Vercel account** — https://vercel.com/signup. Sign up *with GitHub* (one click). This
      hosts the dashboard for free.

## 2. Install tools (one-time, ~15 min)
- [ ] **Python 3.11+** — https://www.python.org/downloads/ (tick "Add to PATH" on Windows).
- [ ] **Node.js LTS** — https://nodejs.org (needed for the React dashboard).
- [ ] **Git** — https://git-scm.com/downloads.
- [ ] **Claude Code** — install per Anthropic's docs, then run it inside this project folder.
- [ ] Quick check: in a terminal, `python --version`, `node --version`, `git --version` all
      return a version.

## 3. Get your read-only crypto API keys
Create keys with **read-only** permission only — no trading, no withdrawals.
- [ ] **Kraken** — Settings → API → Create key → enable only "Query Funds" / "Query Open Orders".
- [ ] **Gemini** — Settings → API → New key → scope "Auditor" (read-only).
- [ ] **Crypto.com** — *only if you use the Exchange (not the App)*: Exchange → Settings → API
      Keys → read-only. If you use the App, skip this and we'll track it manually.
- [ ] Paste each key/secret into a local file called `.env` (copy `.env.example` and fill it in).
      **Never share or commit this file.**

## 4. Fill in your holdings
- [ ] Open `data/holdings.csv` and replace the example rows with your real Syfe positions.
      - Syfe Trade individual stocks/ETFs → one row each, `price_source = yfinance`.
      - Syfe managed portfolios (Core, REIT+, etc.) → one row, `price_source = manual`, and put
        the current value in `manual_price` (read it off the Syfe app; update when you check).
- [ ] Confirm `data/config.json` looks right (base currency USD; SGD + VND displayed).

## 5. Hand off to Claude Code
Once 1–4 are done, open this folder in Claude Code and say:
> "Read PROJECT_PLAN.md. Start with phase 1 — get build_snapshot.py producing a correct
>  latest.json from my holdings and live prices, then we'll do crypto sync and the dashboard."

Claude Code will build and test the data layer, wire the crypto keys, turn on the daily
automation, then build and deploy the React dashboard.

## What I need from you to refine the plan further (optional, reply here)
- Are you on the Crypto.com **App** or **Exchange**? (Decides manual vs auto for that one.)
- Roughly how many positions total? (Tells me if the manual file is trivial or worth more
  automation.)
- Do you use **Syfe Trade** (self-directed tickers), **managed portfolios**, or both?
