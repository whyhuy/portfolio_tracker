import { money, percent, plClass, cleanName, symbolOf, prettyClass } from '../lib/format'
import { CLASS_BLURB, getDesc } from '../lib/descriptions'
import { colorFor } from '../lib/palette'

const CLASS_ORDER = ['equity', 'etf', 'crypto', 'cash']

// Direct holdings, grouped into asset-class sections with a type blurb and per-ticker context.
export default function Holdings({ positions, ccy, fx, title = 'Holdings' }) {
  const groups = {}
  positions.forEach((p) => {
    ;(groups[p.asset_class] ||= []).push(p)
  })
  const classes = [
    ...CLASS_ORDER.filter((c) => groups[c]?.length),
    ...Object.keys(groups).filter((c) => !CLASS_ORDER.includes(c)),
  ]

  return (
    <div className="space-y-5">
      {title && <h2 className="px-1 pt-2 text-sm font-semibold text-slate-300">{title}</h2>}
      {classes.map((cls) => {
        const rows = [...groups[cls]].sort((a, b) => b.value_base - a.value_base)
        const subtotal = rows.reduce((s, p) => s + p.value_base, 0)
        const subcost = rows.reduce((s, p) => s + (p.cost_base || 0), 0)
        const subgain = subtotal - subcost
        return (
          <section key={cls} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: colorFor(cls) }} />
                  <h3 className="text-base font-semibold text-white">{prettyClass(cls)}</h3>
                  <span className="text-xs text-slate-500">({rows.length})</span>
                </div>
                {CLASS_BLURB[cls] && <p className="mt-1 max-w-xl text-xs text-slate-500">{CLASS_BLURB[cls]}</p>}
              </div>
              <div className="text-right">
                <div className="tnum text-sm font-semibold text-white">{money(subtotal, ccy, fx)}</div>
                <div className={`tnum text-xs ${plClass(subgain)}`}>
                  {money(subgain, ccy, fx, { sign: true })} ({percent(subcost ? (subgain / subcost) * 100 : null)})
                </div>
              </div>
            </div>

            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b border-white/10 text-xs uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="px-2 py-1.5 text-left font-medium">Holding</th>
                    <th className="px-2 py-1.5 text-right font-medium">Value</th>
                    <th className="px-2 py-1.5 text-right font-medium">Cost</th>
                    <th className="px-2 py-1.5 text-right font-medium">Gain / Loss</th>
                    <th className="px-2 py-1.5 text-right font-medium">%</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((p) => {
                    const desc = getDesc(p.ticker)
                    return (
                      <tr key={p.ticker} className="border-b border-white/5 align-top last:border-0 hover:bg-white/[0.02]">
                        <td className="px-2 py-2.5">
                          <div className="font-semibold text-slate-100">
                            {symbolOf(p)}
                            <span className="ml-2 text-xs font-normal text-slate-500">{cleanName(p.label)}</span>
                          </div>
                          {desc && <div className="mt-0.5 max-w-md text-xs text-slate-500">{desc}</div>}
                        </td>
                        <td className="px-2 py-2.5 text-right tnum text-slate-100">{money(p.value_base, ccy, fx)}</td>
                        <td className="px-2 py-2.5 text-right tnum text-slate-400">
                          {p.cost_base != null ? money(p.cost_base, ccy, fx) : '—'}
                        </td>
                        <td className={`px-2 py-2.5 text-right tnum ${plClass(p.gain_loss)}`}>
                          {p.gain_loss != null ? money(p.gain_loss, ccy, fx, { sign: true }) : '—'}
                        </td>
                        <td className={`px-2 py-2.5 text-right tnum ${plClass(p.gain_loss)}`}>
                          {p.gain_loss_pct != null ? percent(p.gain_loss_pct) : '—'}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </section>
        )
      })}
    </div>
  )
}
