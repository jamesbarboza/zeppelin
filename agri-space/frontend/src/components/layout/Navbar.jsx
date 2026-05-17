import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <Link to="/dashboard" className="navbar-brand">🌱 Agri-Space</Link>
      <div className="navbar-links">
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/plots/new">+ Add Plot</Link>
        {user?.role === 'admin' && <Link to="/admin">Admin</Link>}
        <button onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  )
}
