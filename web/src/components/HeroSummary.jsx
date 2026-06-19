import { money, percent, plClass } from '../lib/format'

export default function HeroSummary({ data, ccy, dayChange }) {
  const { totals, pnl, fx } = data
  const gl = pnl.total_gain_loss
  const up = gl >= 0

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-7 md:p-9">
      <div className="text-sm text-slate-400">Total portfolio value</div>
      <div className="mt-1.5 flex flex-wrap items-end gap-x-4 gap-y-3">
        <div className="text-5xl font-bold tracking-tight tnum text-white md:text-6xl">
          {money(totals.USD, ccy, fx)}
        </div>
        <div
          className={`mb-2 inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-semibold tnum ${
            up ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
          }`}
        >
          <span>{money(gl, ccy, fx, { sign: true })}</span>
          <span className="opacity-50">·</span>
          <span>{percent(pnl.total_gain_loss_pct)}</span>
          <span className="opacity-70">all-time</span>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-x-7 gap-y-1 text-sm text-slate-400 tnum">
        <span>Cost basis&nbsp;&nbsp;<span className="text-slate-200">{money(pnl.total_cost, ccy, fx)}</span></span>
        {dayChange && (
          <span>
            Today&nbsp;&nbsp;
            <span className={plClass(dayChange.abs)}>
              {money(dayChange.abs, ccy, fx, { sign: true })} ({percent(dayChange.pct)})
            </span>
          </span>
        )}
      </div>
    </section>
  )
}
