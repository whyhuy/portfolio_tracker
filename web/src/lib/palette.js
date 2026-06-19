// Stable colours for asset classes; indexed fallback for platforms / anything else.
export const CLASS_COLORS = {
  crypto: '#f59e0b',
  equity: '#6366f1',
  etf: '#22d3ee',
}

export const FALLBACK = ['#6366f1', '#22d3ee', '#f59e0b', '#a78bfa', '#34d399', '#fb7185', '#60a5fa', '#f472b6']

export function colorFor(key, i = 0) {
  return CLASS_COLORS[key] || FALLBACK[i % FALLBACK.length]
}
