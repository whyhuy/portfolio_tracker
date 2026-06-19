# web/ — the dashboard (to be built in Claude Code)

This is where the React + Tailwind dashboard lives. It is intentionally empty for now — the
frontend is phase 4, built in Claude Code once the data layer produces a real `data/latest.json`.

## Scaffold command (run in Claude Code, phase 4)
```bash
cd web
npm create vite@latest . -- --template react
npm install
npm install tailwindcss recharts
```

## What it should do
- Read `../data/latest.json` (current state) and `../data/history.csv` (value over time).
- Render the design in PROJECT_PLAN.md → "Design direction":
  headline value + daily change, allocation donut, value-over-time line, per-holding rows
  with sparklines, USD/SGD/VND toggle, dark theme, card layout.
- Deploy free on Vercel (connect the GitHub repo; set the build dir to `web/`).

Keep it beautiful — reference Kubera / Copilot Money / Sharesight, not a spreadsheet.
