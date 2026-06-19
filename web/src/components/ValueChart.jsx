import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { money } from '../lib/format'

function LineTip({ active, payload, label, ccy, fx }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-white/10 bg-[#0b0e14] px-3 py-2 text-xs shadow-xl">
      <div className="text-slate-400">{label}</div>
      <div className="tnum font-medium text-slate-100">{money(payload[0].value, ccy, fx)}</div>
    </div>
  )
}

export default function ValueChart({ history, ccy, fx }) {
  const data = history.map((h) => ({ date: h.date, value: h.value }))
  const enough = data.length >= 2

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex items-center justify-between">
        <div className="text-sm font-medium text-slate-300">Portfolio value over time</div>
        <div className="text-xs text-slate-500">
          {data.length} day{data.length === 1 ? '' : 's'}
        </div>
      </div>
      <div className="relative mt-3 h-64">
        <ResponsiveContainer>
          <AreaChart data={data} margin={{ top: 10, right: 8, bottom: 0, left: 8 }}>
            <defs>
              <linearGradient id="valFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366f1" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} minTickGap={24} />
            <YAxis
              tick={{ fill: '#64748b', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={66}
              tickFormatter={(v) => money(v, ccy, fx, { compact: true })}
              domain={['auto', 'auto']}
            />
            <Tooltip content={(props) => <LineTip {...props} ccy={ccy} fx={fx} />} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#818cf8"
              strokeWidth={2}
              fill="url(#valFill)"
              dot={data.length < 8 ? { r: 3, fill: '#818cf8' } : false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
        {!enough && (
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
            <div className="rounded-lg border border-white/10 bg-black/40 px-3 py-1.5 text-xs text-slate-400 backdrop-blur">
              History builds as the tracker runs daily — {data.length} day{data.length === 1 ? '' : 's'} so far.
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
