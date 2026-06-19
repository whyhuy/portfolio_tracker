import { CURRENCIES } from '../lib/format'

export default function CurrencyToggle({ value, onChange }) {
  return (
    <div className="inline-flex rounded-xl border border-white/10 bg-white/5 p-0.5">
      {CURRENCIES.map((c) => (
        <button
          key={c}
          onClick={() => onChange(c)}
          className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
            value === c ? 'bg-white/10 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          {c}
        </button>
      ))}
    </div>
  )
}
