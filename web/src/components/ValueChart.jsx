import { useEffect, useMemo, useState } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts'
import { money, percent, plClass } from '../lib/format'

const RANGES = [
  { key: '1M', days: 30 },
  { key: '3M', days: 91 },
  { key: 'YTD', days: 'ytd' },
  { key: '1Y', days: 365 },
  { key: '3Y', days: 365 * 3 },
  { key: 'All', days: Infinity },
]

function parseCsv(text) {
  return text
    .trim()
    .split(/\r?\n/)
    .slice(1)
    .map((l) => {
      const [date, v] = l.split(',')
      return { date, value: parseFloat(v) }
    })
    .filter((r) => r.date && !Number.isNaN(r.value))
}

function ValueTip({ active, payload, label, ccy, fx }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-white/10 bg-[#0b0e14] px-3 py-2 text-xs shadow-xl">
      <div className="text-slate-400">{label}</div>
      <div className="tnum font-medium text-slate-100">{money(payload[0].value, ccy, fx)}</div>
    </div>
  )
}

// Portfolio value reconstructed from price history x current holdings; cost line = current break-even.
export default function ValueChart({ costUSD, ccy, fx }) {
  const [series, setSeries] = useState([])
  const [range, setRange] = useState('1Y')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true
    fetch('data/portfolio_history.csv', { cache: 'no-store' })
      .then((r) => (r.ok ? r.text() : Promise.reject(new Error(String(r.status)))))
      .then((t) => alive && (setSeries(parseCsv(t)), setLoading(false)))
      .catch(() => alive && setLoading(false))
    return () => {
      alive = false
    }
  }, [])

  const cutoff = useMemo(() => {
    const cfg = RANGES.find((r) => r.key === range)?.days
    if (cfg === Infinity) return null
    if (cfg === 'ytd') return `${new Date().getFullYear()}-01-01`
    const d = new Date()
    d.setDate(d.getDate() - cfg)
    return d.toISOString().slice(0, 10)
  }, [range])

  const data = useMemo(() => (cutoff ? series.filter((r) => r.date >= cutoff) : series), [series, cutoff])
  const change = useMemo(() => {
    if (data.length < 2) return null
    const a = data[0].value
    const b = data[data.length - 1].value
    return { abs: b - a, pct: a ? ((b - a) / a) * 100 : null }
  }, [data])

  const yDomain = useMemo(() => {
    if (!data.length) return ['auto', 'auto']
    const vals = data.map((d) => d.value)
    let lo = Math.min(...vals)
    let hi = Math.max(...vals)
    if (costUSD != null) {
      lo = Math.min(lo, costUSD)
      hi = Math.max(hi, costUSD)
    }
    const pad = (hi - lo) * 0.08 || hi * 0.04
    return [Math.max(0, lo - pad), hi + pad]
  }, [data, costUSD])

  const color = '#818cf8'

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-slate-300">Portfolio value over time</span>
          {change && (
            <span className={`tnum text-xs ${plClass(change.abs)}`}>
              {money(change.abs, ccy, fx, { sign: true })} ({percent(change.pct)})
            </span>
          )}
        </div>
        <div className="inline-flex rounded-lg border border-white/10 bg-white/5 p-0.5">
          {RANGES.map((r) => (
            <button
              key={r.key}
              onClick={() => setRange(r.key)}
              className={`rounded-md px-2 py-1 text-xs font-medium transition ${
                range === r.key ? 'bg-white/10 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {r.key}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-3 h-72">
        {loading ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">Loading…</div>
        ) : data.length < 2 ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">Not enough history for this range.</div>
        ) : (
          <ResponsiveContainer>
            <AreaChart data={data} margin={{ top: 10, right: 8, bottom: 0, left: 8 }}>
              <defs>
                <linearGradient id="pvFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis
                dataKey="date"
                tick={{ fill: '#64748b', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                minTickGap={48}
                tickFormatter={(d) => (d || '').slice(0, 7)}
              />
              <YAxis
                tick={{ fill: '#64748b', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                width={64}
                domain={yDomain}
                tickFormatter={(v) => money(v, ccy, fx, { compact: true })}
              />
              <Tooltip content={(p) => <ValueTip {...p} ccy={ccy} fx={fx} />} />
              {costUSD != null && (
                <ReferenceLine
                  y={costUSD}
                  stroke="#f59e0b"
                  strokeDasharray="4 4"
                  strokeOpacity={0.75}
                  label={{
                    value: `Cost ${money(costUSD, ccy, fx, { compact: true })}`,
                    position: 'insideTopRight',
                    fill: '#f59e0b',
                    fontSize: 11,
                  }}
                />
              )}
              <Area type="monotone" dataKey="value" stroke={color} strokeWidth={2} fill="url(#pvFill)" dot={false} isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
