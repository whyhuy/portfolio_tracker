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

## 3. Deploy on Vercel
1. vercel.com → **Sign up with GitHub** → **Add New… → Project** → import `portfolio-tracker`.
2. Set **Root Directory = `web`** (important). It auto-detects **Vite**; leave build `npm run build`, output `dist`.
3. **Deploy.** You get a URL like `portfolio-tracker-xxxx.vercel.app`. Every push (including the daily data commit) auto-redeploys.

## ⚠️ Access / privacy — decide before going live
A Vercel URL is **public by default** — anyone with the link can see your whole portfolio. A private GitHub repo does **not** make the site private. Free options:
- **Obscure URL** — simplest; security-by-obscurity (don't share the link).
- **Local only** — skip Vercel; run `cd web && npm run dev` when you want it.
- **App password gate** — deters casual viewing, but the data still ships in the JS bundle, so it's not real security.
Vercel's built-in password / SSO protection requires a **paid** plan.

## How it stays current
Actions (daily) commits new `data/latest.json` + `history.csv` → Vercel redeploys → dashboard shows the fresh snapshot. The value-over-time chart gains one point per day.
