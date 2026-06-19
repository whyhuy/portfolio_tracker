export default function StatCard({ label, value, sub, accent }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <div className="text-xs uppercase tracking-wider text-slate-400">{label}</div>
      <div className={`mt-2 text-2xl font-semibold tnum ${accent || 'text-white'}`}>{value}</div>
      {sub && <div className={`mt-1 text-sm tnum ${accent || 'text-slate-500'}`}>{sub}</div>}
    </div>
  )
}
