import { useState } from 'react'
import { money, percent, plClass, cleanName, symbolOf } from '../lib/format'
import { colorFor } from '../lib/palette'

export default function Holdings({ positions, ccy, fx, totalUSD, title = 'Holdings' }) {
  const [sort, setSort] = useState({ key: 'value_base', dir: -1 })

  const rows = [...positions].sort((a, b) => {
    const av = a[sort.key]
    const bv = b[sort.key]
    if (typeof av === 'string') return sort.dir * av.localeCompare(bv)
    return sort.dir * ((av ?? 0) - (bv ?? 0))
  })

  const Head = ({ k, children, align = 'right' }) => (
    <th
      onClick={() => setSort((s) => ({ key: k, dir: s.key === k ? -s.dir : -1 }))}
      className={`cursor-pointer select-none px-3 py-2 font-medium hover:text-slate-200 ${
        align === 'left' ? 'text-left' : 'text-right'
      } ${sort.key === k ? 'text-slate-200' : ''}`}
    >
      {children}
      {sort.key === k ? (sort.dir < 0 ? ' ↓' : ' ↑') : ''}
    </th>
  )

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-2 sm:p-4">
      <div className="px-1 py-2 text-sm font-medium text-slate-300">
        {title} <span className="text-slate-500">({positions.length})</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="border-b border-white/10 text-xs uppercase tracking-wider text-slate-500">
            <tr>
              <Head k="label" align="left">Holding</Head>
              <Head k="value_base">Value</Head>
              <Head k="cost_base">Cost</Head>
              <Head k="gain_loss">Gain / Loss</Head>
              <Head k="gain_loss_pct">%</Head>
              <th className="hidden px-3 py-2 text-right font-medium sm:table-cell">Weight</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => {
              const weight = totalUSD ? (p.value_base / totalUSD) * 100 : 0
              return (
                <tr key={p.ticker} className="border-b border-white/5 last:border-0 hover:bg-white/[0.02]">
                  <td className="px-3 py-2.5">
                    <div className="flex items-center gap-2.5">
                      <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: colorFor(p.asset_class) }} />
                      <div className="min-w-0">
                        <div className="font-semibold text-slate-100">{symbolOf(p)}</div>
                        <div className="truncate text-xs text-slate-500">
                          {cleanName(p.label)} · {p.platform || 'Unassigned'}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-2.5 text-right tnum text-slate-100">{money(p.value_base, ccy, fx)}</td>
                  <td className="px-3 py-2.5 text-right tnum text-slate-400">{money(p.cost_base, ccy, fx)}</td>
                  <td className={`px-3 py-2.5 text-right tnum ${plClass(p.gain_loss)}`}>
                    {money(p.gain_loss, ccy, fx, { sign: true })}
                  </td>
                  <td className={`px-3 py-2.5 text-right tnum ${plClass(p.gain_loss)}`}>{percent(p.gain_loss_pct)}</td>
                  <td className="hidden px-3 py-2.5 text-right sm:table-cell">
                    <div className="flex items-center justify-end gap-2">
                      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-white/10">
                        <div className="h-full rounded-full bg-indigo-400/70" style={{ width: `${Math.min(100, weight)}%` }} />
                      </div>
                      <span className="tnum w-10 text-xs text-slate-400">{weight.toFixed(1)}%</span>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
