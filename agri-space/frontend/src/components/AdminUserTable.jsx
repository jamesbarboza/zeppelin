import { useState } from 'react'
import { updateUser } from '../api/admin'

export default function AdminUserTable({ users, onUpdate }) {
  const [loadingId, setLoadingId] = useState(null)

  const toggleActive = async (user) => {
    setLoadingId(user.id)
    try {
      await updateUser(user.id, { is_active: !user.is_active })
      onUpdate()
    } finally {
      setLoadingId(null)
    }
  }

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
      <thead>
        <tr style={{ borderBottom: '2px solid #eee', textAlign: 'left' }}>
          <th style={{ padding: '8px 12px' }}>Email</th>
          <th style={{ padding: '8px 12px' }}>Farm</th>
          <th style={{ padding: '8px 12px' }}>Role</th>
          <th style={{ padding: '8px 12px' }}>Joined</th>
          <th style={{ padding: '8px 12px' }}>Status</th>
        </tr>
      </thead>
      <tbody>
        {users.map(user => (
          <tr key={user.id} style={{ borderBottom: '1px solid #f0f0f0' }}>
            <td style={{ padding: '8px 12px' }}>{user.email}</td>
            <td style={{ padding: '8px 12px', color: '#666' }}>{user.farm_name || '—'}</td>
            <td style={{ padding: '8px 12px' }}>
              <span style={{ padding: '2px 8px', borderRadius: 10, fontSize: 11,
                             background: user.role === 'admin' ? '#e8f5e9' : '#f3f3f3',
                             color: user.role === 'admin' ? '#2e7d32' : '#666' }}>
                {user.role}
              </span>
            </td>
            <td style={{ padding: '8px 12px', color: '#888' }}>
              {new Date(user.date_joined).toLocaleDateString()}
            </td>
            <td style={{ padding: '8px 12px' }}>
              <button onClick={() => toggleActive(user)} disabled={loadingId === user.id}
                style={{ padding: '4px 12px', borderRadius: 4, cursor: 'pointer', fontSize: 12,
                         background: user.is_active ? '#ffebee' : '#e8f5e9',
                         color: user.is_active ? '#c62828' : '#2e7d32',
                         border: `1px solid ${user.is_active ? '#ef9a9a' : '#a5d6a7'}` }}>
                {loadingId === user.id ? '...' : user.is_active ? 'Deactivate' : 'Activate'}
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
