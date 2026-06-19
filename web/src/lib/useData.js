import { useEffect, useState } from 'react'

function parseHistory(csv) {
  const lines = csv.trim().split(/\r?\n/)
  if (lines.length < 2) return []
  const header = lines[0].split(',')
  const dateI = header.indexOf('date')
  const valI = header.findIndex((h) => h.startsWith('total_'))
  return lines
    .slice(1)
    .map((l) => {
      const c = l.split(',')
      return { date: c[dateI], value: parseFloat(c[valI]) }
    })
    .filter((r) => r.date && !Number.isNaN(r.value))
}

export function useData() {
  const [state, setState] = useState({ loading: true, error: null, data: null, history: [] })

  useEffect(() => {
    let alive = true
    ;(async () => {
      try {
        const [dRes, hRes] = await Promise.all([
          fetch('data/latest.json', { cache: 'no-store' }),
          fetch('data/history.csv', { cache: 'no-store' }),
        ])
        if (!dRes.ok) throw new Error(`Could not load latest.json (${dRes.status})`)
        const data = await dRes.json()
        const history = hRes.ok ? parseHistory(await hRes.text()) : []
        if (alive) setState({ loading: false, error: null, data, history })
      } catch (e) {
        if (alive) setState({ loading: false, error: e.message, data: null, history: [] })
      }
    })()
    return () => {
      alive = false
    }
  }, [])

  return state
}
