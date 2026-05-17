import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function AnalyticsCharts({ snapshots }) {
  const recent = [...snapshots].reverse().slice(-14)
  const latestSnap = snapshots[0] ?? {}
  const topCrops = latestSnap.top_crop_tags_json ?? []

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginTop: 24 }}>
      <div style={{ background: 'white', borderRadius: 8, padding: '1.25rem', boxShadow: '0 1px 4px rgba(0,0,0,0.07)' }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: '#666', marginBottom: 12 }}>USER GROWTH (14 DAYS)</h3>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={recent}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={d => d.slice(5)} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Bar dataKey="total_users" fill="#1a3a2a" name="Total Users" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ background: 'white', borderRadius: 8, padding: '1.25rem', boxShadow: '0 1px 4px rgba(0,0,0,0.07)' }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: '#666', marginBottom: 12 }}>TOP CROPS</h3>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={topCrops} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" tick={{ fontSize: 10 }} />
            <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={70} />
            <Tooltip />
            <Bar dataKey="plot_count" fill="#43a047" name="Plots" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
