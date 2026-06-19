export const CURRENCIES = ['USD', 'SGD', 'VND']

const CCY_META = {
  USD: { symbol: '$', locale: 'en-US', decimals: 2 },
  SGD: { symbol: 'S$', locale: 'en-SG', decimals: 2 },
  VND: { symbol: '₫', locale: 'vi-VN', decimals: 0 },
}

// All position/total figures are stored in USD; convert with the snapshot's live FX.
export function convert(usd, ccy, fx) {
  if (!ccy || ccy === 'USD') return usd
  const rate = fx?.[`USD${ccy}`]
  return rate ? usd * rate : usd
}

export function money(usd, ccy = 'USD', fx = {}, { compact = false, sign = false } = {}) {
  const meta = CCY_META[ccy] || CCY_META.USD
  const v = convert(usd, ccy, fx)
  const prefix = sign && v > 0 ? '+' : v < 0 ? '−' : ''
  const opts = compact
    ? { notation: 'compact', maximumFractionDigits: 1 }
    : { minimumFractionDigits: meta.decimals, maximumFractionDigits: meta.decimals }
  return `${prefix}${meta.symbol}${new Intl.NumberFormat(meta.locale, opts).format(Math.abs(v))}`
}

export function percent(p, { sign = true } = {}) {
  if (p === null || p === undefined || Number.isNaN(p)) return '—'
  const prefix = sign && p > 0 ? '+' : p < 0 ? '−' : ''
  return `${prefix}${Math.abs(p).toFixed(2)}%`
}

// Tailwind text colour by sign of a P&L figure.
export function plClass(v) {
  if (v > 0) return 'text-emerald-400'
  if (v < 0) return 'text-rose-400'
  return 'text-slate-400'
}

// "ORACLE CORPORATION (XNYS:ORCL)" -> "Oracle Corporation"; leaves mixed-case names alone.
export function cleanName(label) {
  let s = (label || '').replace(/\s*\([^)]*\)\s*$/, '').trim()
  // Title-case ALL-CAPS company names, but leave short acronyms/tickers (e.g. XRP) alone.
  if (s && s.length > 4 && s === s.toUpperCase() && /[A-Z]/.test(s)) {
    s = s.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase())
  }
  return s || label || ''
}

// Short symbol for a row: ticker for equities/ETFs, the (BTC)-style code for crypto.
export function symbolOf(p) {
  if (p.asset_class === 'crypto') {
    const m = (p.label || '').match(/\(([^)]+)\)\s*$/)
    if (m) return m[1]
    return (p.label || p.ticker || '').toUpperCase()
  }
  return (p.ticker || '').toUpperCase()
}

export function prettyClass(s) {
  if (s === 'etf') return 'ETF'
  if (!s) return 'Unassigned'
  return s.charAt(0).toUpperCase() + s.slice(1)
}
