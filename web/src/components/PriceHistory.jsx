import { useEffect, useMemo, useState } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { money, symbolOf, cleanName, percent, plClass, prettyClass } from '../lib/format'

const RANGES = [
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
      const [date, close] = l.split(',')
      return { date, close: parseFloat(close) }
    })
    .filter((r) => r.date && !Number.isNaN(r.close))
}

function PriceTip({ active, payload, label, ccy, fx }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-white/10 bg-[#0b0e14] px-3 py-2 text-xs shadow-xl">
      <div className="text-slate-400">{label}</div>
      <div className="tnum font-medium text-slate-100">{money(payload[0].value, ccy, fx)}</div>
    </div>
  )
}

export default function PriceHistory({ positions, ccy, fx }) {
  const selectable = useMemo(() => positions.filter((p) => p.asset_class !== 'cash'), [positions])
  const groups = useMemo(() => {
    const g = {}
    selectable.forEach((p) => {
      const key = p.fund || prettyClass(p.asset_class)
      ;(g[key] ||= []).push(p)
    })
    return g
  }, [selectable])
  const defaultTicker = useMemo(
    () => [...selectable].sort((a, b) => b.value_base - a.value_base)[0]?.ticker,
    [selectable],
  )

  const [ticker, setTicker] = useState(defaultTicker)
  const [range, setRange] = useState('3Y')
  const [series, setSeries] = useState([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState(null)

  useEffect(() => {
    if (!ticker && defaultTicker) setTicker(defaultTicker)
  }, [defaultTicker, ticker])

  useEffect(() => {
    if (!ticker) return
    let alive = true
    setLoading(true)
    setErr(null)
    fetch(`data/prices/${encodeURIComponent(ticker)}.csv`, { cache: 'no-store' })
      .then((r) => {
        if (!r.ok) throw new Error(`no history (${r.status})`)
        return r.text()
      })
      .then((t) => alive && (setSeries(parseCsv(t)), setLoading(false)))
      .catch((e) => alive && (setErr(e.message), setSeries([]), setLoading(false)))
    return () => {
      alive = false
    }
  }, [ticker])

  const cutoff = useMemo(() => {
    const days = RANGES.find((r) => r.key === range)?.days ?? Infinity
    if (!Number.isFinite(days)) return null
    const d = new Date()
    d.setDate(d.getDate() - days)
    return d.toISOString().slice(0, 10)
  }, [range])

  const data = useMemo(() => (cutoff ? series.filter((r) => r.date >= cutoff) : series), [series, cutoff])
  const change = useMemo(() => {
    if (data.length < 2) return null
    const first = data[0].close
    const last = data[data.length - 1].close
    return { abs: last - first, pct: first ? ((last - first) / first) * 100 : null, last }
  }, [data])

  const up = (change?.abs ?? 0) >= 0
  const color = up ? '#34d399' : '#f87171'
  const pos = selectable.find((p) => p.ticker === ticker)

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-slate-300">Price history</span>
          <select
            value={ticker || ''}
            onChange={(e) => setTicker(e.target.value)}
            className="max-w-[16rem] rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-sm text-slate-200 outline-none"
          >
            {Object.entries(groups).map(([g, items]) => (
              <optgroup key={g} label={g}>
                {items.map((p) => (
                  <option key={p.ticker} value={p.ticker}>
                    {symbolOf(p)} — {cleanName(p.label)}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>
        <div className="inline-flex rounded-lg border border-white/10 bg-white/5 p-0.5">
          {RANGES.map((r) => (
            <button
              key={r.key}
              onClick={() => setRange(r.key)}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition ${
                range === r.key ? 'bg-white/10 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {r.key}
            </button>
          ))}
        </div>
      </div>

      {change && (
        <div className="mt-3 flex flex-wrap items-end gap-3">
          <div className="tnum text-2xl font-semibold text-white">{money(change.last, ccy, fx)}</div>
          <div className={`tnum mb-1 text-sm ${plClass(change.abs)}`}>
            {money(change.abs, ccy, fx, { sign: true })} ({percent(change.pct)})
            <span className="text-slate-500"> over {range === 'All' ? 'all time' : range}</span>
          </div>
          {pos && <div className="mb-1 text-xs text-slate-500">{cleanName(pos.label)}</div>}
        </div>
      )}

      <div className="mt-3 h-72">
        {loading ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">Loading…</div>
        ) : err || data.length === 0 ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">
            No price history for this holding yet.
          </div>
        ) : (
          <ResponsiveContainer>
            <AreaChart data={data} margin={{ top: 10, right: 8, bottom: 0, left: 8 }}>
              <defs>
                <linearGradient id="phFill" x1="0" y1="0" x2="0" y2="1">
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
                domain={['auto', 'auto']}
                tickFormatter={(v) => money(v, ccy, fx, { compact: true })}
              />
              <Tooltip content={(p) => <PriceTip {...p} ccy={ccy} fx={fx} />} />
              <Area type="monotone" dataKey="close" stroke={color} strokeWidth={1.5} fill="url(#phFill)" dot={false} isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
