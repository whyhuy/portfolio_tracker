# Deploy & Automate

The data layer (`scripts/`) and dashboard (`web/`) are ready. This wires up the free pieces:
- **GitHub Actions** — re-runs the Python daily and commits fresh data.
- **Vercel** — hosts the dashboard and redeploys on every commit.

Local git is already initialised and committed on `main` (`.env` is gitignored — your keys never leave your machine).

## 1. Create the GitHub repo — make it PRIVATE
`data/holdings.csv` and the snapshots hold your real positions, so keep the repo private.
1. github.com → **New repository** → name e.g. `portfolio-tracker` → **Private** → *Create repository*. Don't tick "Add a README/.gitignore" — we already have them.
2. Connect and push (or ask me to run these for you):
   ```bash
   git remote add origin https://github.com/<your-username>/portfolio-tracker.git
   git push -u origin main
   ```

## 2. Turn on the daily refresh (GitHub Actions)
- Workflow: `.github/workflows/update.yml` — runs 21:30 UTC daily, and on demand.
- **No secrets required** (crypto is entered manually; prices/FX are keyless).
- After pushing: repo → **Actions** tab → enable workflows → open *Update portfolio snapshot* → **Run workflow** to test. It should push a `snapshot: <date>` commit.

## 3. Deploy on Vercel (with the password gate)
1. vercel.com → **Sign up with GitHub** → **Add New… → Project** → import `portfolio_tracker`.
2. Set **Root Directory = `web`** (important). It auto-detects **Vite** (build `npm run build`, output `dist`).
3. **Before clicking Deploy**, open **Environment Variables** and add one:
   - **Key:** `SITE_PASSWORD`   **Value:** *(a password you choose)*
   The gate (`web/middleware.js`) is fail-closed — if this isn't set, the site returns 503 and serves nothing, so it can never leak.
4. **Deploy.** You get a URL like `portfolio-tracker-xxxx.vercel.app`. Opening it shows a browser login prompt — any username + that password. Every push (incl. the daily data commit) auto-redeploys.

## Access / privacy — password gate (implemented)
`web/middleware.js` is Vercel Routing (Edge) Middleware: it runs **before any file is served**, so it protects the page **and** the underlying `data/latest.json` behind HTTP Basic Auth. This is the free way to actually keep the contents private (a client-side lock screen would leave the JSON fetchable).
- Set **`SITE_PASSWORD`** in Vercel (step 3). Single shared password, any username. Fail-closed if unset.
- **Local dev is not gated** — the middleware only runs on Vercel; `npm run dev` stays open on localhost.
- Change the password anytime: edit the `SITE_PASSWORD` env var in Vercel → redeploy.
- True multi-user SSO would need Vercel's paid Deployment Protection.

## How it stays current
Actions (daily) commits new `data/latest.json` + `history.csv` → Vercel redeploys → dashboard shows the fresh snapshot. The value-over-time chart gains one point per day.
