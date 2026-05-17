import { useState, useEffect, useCallback } from 'react'
import AdminUserTable from '../components/AdminUserTable'
import AnalyticsCharts from '../components/AnalyticsCharts'
import { listUsers, getAnalytics } from '../api/admin'

export default function Admin() {
  const [users, setUsers] = useState([])
  const [snapshots, setSnapshots] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = useCallback(() => {
    Promise.all([listUsers(), getAnalytics()])
      .then(([u, s]) => { setUsers(u); setSnapshots(s); setLoading(false) })
      .catch(() => { setError('Access denied or data unavailable.'); setLoading(false) })
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  if (loading) return <div className="loading">Loading admin panel...</div>
  if (error) return <div style={{ padding: '2rem', color: '#c0392b' }}>{error}</div>

  const latest = snapshots[0] ?? {}

  return (
    <div style={{ padding: '1.5rem', maxWidth: 1100, margin: '0 auto' }}>
      <h2 style={{ marginBottom: '1.5rem' }}>Admin Panel</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        {[
          ['Total Users', latest.total_users ?? 0],
          ['Active (7d)', latest.active_users_7d ?? 0],
          ['Total Plots', latest.total_plots ?? 0],
          ['LLM Calls Today', latest.recommendations_generated ?? 0],
        ].map(([label, value]) => (
          <div key={label} style={{ background: 'white', borderRadius: 8, padding: '1.25rem',
                                     boxShadow: '0 1px 4px rgba(0,0,0,0.07)' }}>
            <div style={{ fontSize: 12, color: '#888', textTransform: 'uppercase', marginBottom: 8 }}>{label}</div>
            <div style={{ fontSize: 28, fontWeight: 700, color: '#1a3a2a' }}>{value}</div>
          </div>
        ))}
      </div>
      <AnalyticsCharts snapshots={snapshots} />
      <div style={{ background: 'white', borderRadius: 8, padding: '1.25rem', marginTop: 24,
                    boxShadow: '0 1px 4px rgba(0,0,0,0.07)' }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: '#666', marginBottom: 16 }}>
          USERS ({users.length})
        </h3>
        <AdminUserTable users={users} onUpdate={fetchData} />
      </div>
    </div>
  )
}
