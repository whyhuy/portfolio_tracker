import { money, percent, plClass, cleanName } from '../lib/format'
import { getDesc } from '../lib/descriptions'
import { colorFor } from '../lib/palette'

// A managed fund (e.g. Syfe Core Equity100): one cost/gain at the fund level, with its
// constituents priced live but shown value-only (no per-holding P&L).
export default function FundCard({ fund, members, ccy, fx }) {
  const rows = [...members].sort((a, b) => b.value_base - a.value_base)
  return (
    <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-semibold text-white">{fund.name}</h2>
            <span className="rounded bg-indigo-500/15 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-indigo-300">
              Managed fund
            </span>
          </div>
          <div className="mt-0.5 text-xs text-slate-500">
            {fund.holdings} holdings · cost {money(fund.cost, ccy, fx)}
          </div>
        </div>
        <div className="text-right">
          <div className="tnum text-xl font-semibold text-white">{money(fund.value, ccy, fx)}</div>
          <div className={`tnum text-sm font-medium ${plClass(fund.gain_loss)}`}>
            {money(fund.gain_loss, ccy, fx, { sign: true })} ({percent(fund.gain_loss_pct)})
          </div>
        </div>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="border-b border-white/10 text-xs uppercase tracking-wider text-slate-500">
            <tr>
              <th className="px-2 py-1.5 text-left font-medium">Holding</th>
              <th className="px-2 py-1.5 text-right font-medium">Weight</th>
              <th className="px-2 py-1.5 text-right font-medium">Value</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => {
              const w = fund.value ? (p.value_base / fund.value) * 100 : 0
              const code = (p.label.match(/\(([^)]+)\)\s*$/) || [])[1] || ''
              const desc = getDesc(p.ticker)
              return (
                <tr key={p.ticker} className="border-b border-white/5 align-top last:border-0">
                  <td className="px-2 py-2">
                    <div className="flex items-center gap-2">
                      <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: colorFor(p.asset_class) }} />
                      <span className="truncate text-slate-200">{cleanName(p.label)}</span>
                      {code && <span className="shrink-0 text-xs text-slate-500">{code}</span>}
                    </div>
                    {desc && <div className="mt-0.5 max-w-md text-xs text-slate-500">{desc}</div>}
                  </td>
                  <td className="px-2 py-2 text-right tnum text-slate-400">{w.toFixed(1)}%</td>
                  <td className="px-2 py-2 text-right tnum text-slate-200">{money(p.value_base, ccy, fx)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}
