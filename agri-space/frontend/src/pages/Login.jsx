import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import client from '../api/client'

export default function Login() {
  const [tab, setTab] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [farmName, setFarmName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch {
      setError('Invalid email or password.')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await client.post('/auth/register/', { email, password, farm_name: farmName })
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.email?.[0] || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <div style={{ background: 'white', borderRadius: 8, padding: '2rem', width: 360, boxShadow: '0 2px 12px rgba(0,0,0,0.1)' }}>
        <h1 style={{ marginBottom: '1.5rem', color: '#1a3a2a' }}>🌱 Agri-Space</h1>
        <div style={{ display: 'flex', gap: 0, marginBottom: '1.5rem', borderBottom: '2px solid #eee' }}>
          {['login', 'register'].map(t => (
            <button key={t} onClick={() => setTab(t)}
              style={{ flex: 1, padding: '8px', background: 'transparent', border: 'none',
                       borderBottom: tab === t ? '2px solid #1a3a2a' : 'none', cursor: 'pointer',
                       fontWeight: tab === t ? 'bold' : 'normal', textTransform: 'capitalize' }}>
              {t}
            </button>
          ))}
        </div>
        <form onSubmit={tab === 'login' ? handleLogin : handleRegister}>
          <input value={email} onChange={e => setEmail(e.target.value)}
            placeholder="Email" type="email" required
            style={{ width: '100%', padding: '8px 12px', marginBottom: 12, border: '1px solid #ddd', borderRadius: 4 }} />
          {tab === 'register' && (
            <input value={farmName} onChange={e => setFarmName(e.target.value)}
              placeholder="Farm name (optional)"
              style={{ width: '100%', padding: '8px 12px', marginBottom: 12, border: '1px solid #ddd', borderRadius: 4 }} />
          )}
          <input value={password} onChange={e => setPassword(e.target.value)}
            placeholder="Password" type="password" required minLength={8}
            style={{ width: '100%', padding: '8px 12px', marginBottom: 12, border: '1px solid #ddd', borderRadius: 4 }} />
          {error && <p style={{ color: '#c0392b', fontSize: 13, marginBottom: 12 }}>{error}</p>}
          <button type="submit" disabled={loading}
            style={{ width: '100%', padding: '10px', background: '#1a3a2a', color: 'white',
                     border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}>
            {loading ? 'Please wait...' : tab === 'login' ? 'Login' : 'Create Account'}
          </button>
        </form>
      </div>
    </div>
  )
}
