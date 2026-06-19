import { useMemo, useState } from 'react'
import { useData } from './lib/useData'
import { colorFor } from './lib/palette'
import { money, percent, plClass, prettyClass } from './lib/format'
import CurrencyToggle from './components/CurrencyToggle'
import HeroSummary from './components/HeroSummary'
import StatCard from './components/StatCard'
import AllocationDonut from './components/AllocationDonut'
import ValueChart from './components/ValueChart'
import PriceHistory from './components/PriceHistory'
import FundCard from './components/FundCard'
import Holdings from './components/Holdings'

function groupSlices(positions, key, useClassColor) {
  const map = new Map()
  positions.forEach((p) => {
    const k = p[key] || 'Unassigned'
    map.set(k, (map.get(k) || 0) + p.value_base)
  })
  return [...map.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([name, value], i) => ({
      name: prettyClass(name),
      value,
      color: useClassColor ? colorFor(name, i) : colorFor('_', i),
    }))
}

export default function App() {
  const { loading, error, data, history } = useData()
  const [ccy, setCcy] = useState('USD')

  const dayChange = useMemo(() => {
    if (history.length < 2) return null
    const last = history[history.length - 1].value
    const prev = history[history.length - 2].value
    return { abs: last - prev, pct: prev ? ((last - prev) / prev) * 100 : null }
  }, [history])

  const byClass = useMemo(() => (data ? groupSlices(data.positions, 'asset_class', true) : []), [data])
  const byPlatform = useMemo(() => (data ? groupSlices(data.positions, 'platform', false) : []), [data])
  const directPositions = useMemo(() => (data ? data.positions.filter((p) => !p.fund) : []), [data])

  if (loading) {
    return <Centered>Loading portfolio…</Centered>
  }
  if (error) {
    return (
      <Centered>
        <div className="text-rose-400">Couldn’t load data</div>
        <div className="mt-1 text-sm text-slate-500">{error}</div>
        <div className="mt-2 text-xs text-slate-600">Run the data layer, then <code>npm run sync:data</code>.</div>
      </Centered>
    )
  }

  const { totals, pnl, fx } = data
  const asOf = new Date(data.as_of)

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 md:py-10">
      <header className="mb-7 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-lg font-semibold tracking-tight text-white">Portfolio</h1>
          <p className="text-xs text-slate-500">
            As of {asOf.toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' })}
            {', '}
            {asOf.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
        <CurrencyToggle value={ccy} onChange={setCcy} />
      </header>

      <div className="space-y-5">
        <HeroSummary data={data} ccy={ccy} dayChange={dayChange} />

        <div className="grid grid-cols-2 gap-5 lg:grid-cols-4">
          <StatCard label="Total value" value={money(totals.USD, ccy, fx)} />
          <StatCard label="Cost basis" value={money(pnl.total_cost, ccy, fx)} />
          <StatCard
            label="Unrealised P&L"
            value={money(pnl.total_gain_loss, ccy, fx, { sign: true })}
            accent={plClass(pnl.total_gain_loss)}
          />
          <StatCard
            label="Return on cost"
            value={percent(pnl.total_gain_loss_pct)}
            accent={plClass(pnl.total_gain_loss)}
          />
        </div>

        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
          <AllocationDonut title="Allocation by asset class" slices={byClass} ccy={ccy} fx={fx} totalUSD={totals.USD} />
          <AllocationDonut title="Allocation by platform" slices={byPlatform} ccy={ccy} fx={fx} totalUSD={totals.USD} />
        </div>

        <ValueChart history={history} ccy={ccy} fx={fx} />

        <PriceHistory positions={data.positions} ccy={ccy} fx={fx} />

        {data.funds?.map((f) => (
          <FundCard
            key={f.name}
            fund={f}
            members={data.positions.filter((p) => p.fund === f.name)}
            ccy={ccy}
            fx={fx}
          />
        ))}

        <Holdings positions={directPositions} title="Direct holdings" ccy={ccy} fx={fx} totalUSD={totals.USD} />

        <footer className="pt-2 text-center text-xs text-slate-600">
          Prices via yfinance &amp; CoinGecko · FX USD→SGD {fx.USDSGD?.toFixed(4)}, USD→VND{' '}
          {fx.USDVND?.toLocaleString()} · indicative, not financial advice.
        </footer>
      </div>
    </div>
  )
}

function Centered({ children }) {
  return (
    <div className="flex min-h-screen items-center justify-center px-6 text-center">
      <div className="text-slate-300">{children}</div>
    </div>
  )
}
