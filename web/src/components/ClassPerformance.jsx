import { money, percent, plClass, prettyClass } from '../lib/format'
import { colorFor } from '../lib/palette'

// Scoreboard: unrealised return of each sub-portfolio (direct asset classes + each managed fund),
// sorted best-to-worst with a diverging bar so the leaders and laggards stand out.
export default function ClassPerformance({ positions, funds, ccy, fx }) {
  const byClass = {}
  positions.forEach((p) => {
    const g = (byClass[p.asset_class] ||= { value: 0, cost: 0 })
    g.value += p.value_base
    g.cost += p.cost_base || 0
  })

  const rows = [
    ...Object.entries(byClass).map(([cls, g]) => ({
      key: cls,
      name: prettyClass(cls),
      color: colorFor(cls),
      value: g.value,
      gain: g.value - g.cost,
      pct: g.cost ? ((g.value - g.cost) / g.cost) * 100 : null,
    })),
    ...funds.map((f) => ({
      key: f.name,
      name: f.name,
      color: '#a78bfa',
      value: f.value,
      gain: f.gain_loss,
      pct: f.gain_loss_pct,
      fund: true,
    })),
  ].sort((a, b) => (b.pct ?? -Infinity) - (a.pct ?? -Infinity))

  const maxAbs = Math.max(...rows.map((r) => Math.abs(r.pct || 0)), 1)

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <div className="text-sm font-medium text-slate-300">Performance by asset class</div>
      <p className="mt-1 text-xs text-slate-500">Unrealised return on cost, by sub-portfolio.</p>
      <div className="mt-4 space-y-3">
        {rows.map((r) => {
          const w = Math.min(50, (Math.abs(r.pct || 0) / maxAbs) * 50)
          return (
            <div
              key={r.key}
              className="grid grid-cols-[7.5rem_1fr_5.5rem] items-center gap-3 sm:grid-cols-[12rem_1fr_7rem]"
            >
              <div className="flex min-w-0 items-center gap-2">
                <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: r.color }} />
                <span className="truncate text-sm text-slate-200">{r.name}</span>
                {r.fund && (
                  <span className="hidden shrink-0 rounded bg-indigo-500/15 px-1 text-[9px] uppercase tracking-wide text-indigo-300 sm:inline">
                    fund
                  </span>
                )}
              </div>

              <div className="relative h-2.5 rounded-full bg-white/5">
                <div className="absolute left-1/2 top-0 h-full w-px bg-white/15" />
                {r.pct != null &&
                  (r.pct >= 0 ? (
                    <div className="absolute top-0 h-full rounded-full" style={{ left: '50%', width: `${w}%`, background: '#34d399' }} />
                  ) : (
                    <div className="absolute top-0 h-full rounded-full" style={{ right: '50%', width: `${w}%`, background: '#f87171' }} />
                  ))}
              </div>

              <div className="text-right">
                <div className={`tnum text-sm font-semibold ${plClass(r.gain)}`}>{percent(r.pct)}</div>
                <div className="tnum text-xs text-slate-500">{money(r.gain, ccy, fx, { sign: true })}</div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
