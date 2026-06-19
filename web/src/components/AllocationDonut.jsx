import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { money } from '../lib/format'

function DonutTip({ active, payload, ccy, fx, totalUSD }) {
  if (!active || !payload?.length) return null
  const p = payload[0]
  const pct = totalUSD ? ((p.value / totalUSD) * 100).toFixed(1) : '0'
  return (
    <div className="rounded-lg border border-white/10 bg-[#0b0e14] px-3 py-2 text-xs shadow-xl">
      <div className="font-medium text-slate-200">{p.name}</div>
      <div className="tnum text-slate-400">
        {money(p.value, ccy, fx)} · {pct}%
      </div>
    </div>
  )
}

export default function AllocationDonut({ title, slices, ccy, fx, totalUSD }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <div className="text-sm font-medium text-slate-300">{title}</div>
      <div className="mt-3 flex items-center gap-5">
        <div className="relative h-40 w-40 shrink-0">
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={slices}
                dataKey="value"
                nameKey="name"
                innerRadius={50}
                outerRadius={72}
                paddingAngle={2}
                stroke="none"
              >
                {slices.map((s, i) => (
                  <Cell key={i} fill={s.color} />
                ))}
              </Pie>
              <Tooltip content={(props) => <DonutTip {...props} ccy={ccy} fx={fx} totalUSD={totalUSD} />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
            <div className="text-[10px] uppercase tracking-wider text-slate-500">Total</div>
            <div className="tnum text-sm font-semibold text-white">{money(totalUSD, ccy, fx, { compact: true })}</div>
          </div>
        </div>
        <ul className="flex-1 space-y-2">
          {slices.map((s, i) => {
            const pct = totalUSD ? (s.value / totalUSD) * 100 : 0
            return (
              <li key={i} className="flex items-center justify-between gap-2 text-sm">
                <span className="flex items-center gap-2 text-slate-300">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: s.color }} />
                  {s.name}
                </span>
                <span className="tnum text-slate-400">{pct.toFixed(1)}%</span>
              </li>
            )
          })}
        </ul>
      </div>
    </div>
  )
}
