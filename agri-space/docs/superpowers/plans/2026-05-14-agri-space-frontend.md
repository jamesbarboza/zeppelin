# Agri-Space Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the React SPA frontend for Agri-Space — map-based plot selection, recommendation dashboard, and admin panel.

**Architecture:** React 18 + Vite SPA. Leaflet.js for the interactive map with pin and polygon draw modes. Axios for API calls with credentials (httpOnly cookie auth). React Router for navigation. Recharts for admin analytics.

**Tech Stack:** React 18, Vite 5, React Router 6, Leaflet 1.9, react-leaflet 4, leaflet-draw, axios, recharts.

**Prerequisite:** Backend must be running on `http://localhost:8000` before testing any API calls.

---

## File Map

```
frontend/
  package.json
  vite.config.js
  index.html
  src/
    main.jsx
    App.jsx
    api/
      client.js                # axios instance (withCredentials: true)
      plots.js                 # listPlots, createPlot, updatePlot, deletePlot, listCropTags
      recommendations.js       # getRecommendations
      admin.js                 # listUsers, updateUser, getAnalytics
    context/
      AuthContext.jsx           # user state, login(), logout(), refresh on mount
    hooks/
      useRecommendations.js    # fetches + caches cards per plot id
    components/
      layout/
        Navbar.jsx             # nav links, logout button
        ProtectedRoute.jsx     # redirects to /login if not authenticated
      PlotMap.jsx              # Leaflet map, pin click + polygon draw, emits geometry
      RecommendationCard.jsx   # single status card (green/amber/red)
      RecommendationList.jsx   # loading state + list of RecommendationCards
      AdminUserTable.jsx       # sortable user table with activate/deactivate toggle
      AnalyticsCharts.jsx      # user growth + top crops bar chart (recharts)
    pages/
      Login.jsx                # login + register tabs
      Dashboard.jsx            # map + plot sidebar + recommendation panel
      NewPlot.jsx              # map draw flow, name + crop tag inputs, save
      PlotDetail.jsx           # plot info + RecommendationList
      EditPlot.jsx             # re-draw geometry or change crop tags
      Admin.jsx                # AdminUserTable + AnalyticsCharts
```

---

## Task 1: React + Vite Scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/api/client.js`

- [ ] **Step 1: Scaffold with Vite**

```bash
cd /path/to/agri-space
npm create vite@latest frontend -- --template react
cd frontend
npm install react-router-dom axios leaflet react-leaflet leaflet-draw recharts
npm install -D @vitejs/plugin-react
```

- [ ] **Step 2: Write `vite.config.js`**

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
```

The proxy means all `/api/*` calls from the React dev server go to Django, preserving cookies.

- [ ] **Step 3: Write `src/api/client.js`**

```js
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  withCredentials: true,  // send httpOnly cookies with every request
})

client.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401 && !err.config._retry) {
      err.config._retry = true
      try {
        await axios.post('/api/auth/refresh/', {}, { withCredentials: true })
        return client(err.config)
      } catch {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default client
```

- [ ] **Step 4: Write `src/api/plots.js`**

```js
import client from './client'

export const listPlots = () => client.get('/plots/').then(r => r.data)
export const getPlot = (id) => client.get(`/plots/${id}/`).then(r => r.data)
export const createPlot = (data) => client.post('/plots/', data).then(r => r.data)
export const updatePlot = (id, data) => client.patch(`/plots/${id}/`, data).then(r => r.data)
export const deletePlot = (id) => client.delete(`/plots/${id}/`)
export const listCropTags = () => client.get('/crop-tags/').then(r => r.data)
```

- [ ] **Step 5: Write `src/api/recommendations.js`**

```js
import client from './client'

export const getRecommendations = (plotId) =>
  client.get(`/plots/${plotId}/recommendations/`).then(r => r.data)
```

- [ ] **Step 6: Write `src/api/admin.js`**

```js
import client from './client'

export const listUsers = () => client.get('/admin/users/').then(r => r.data)
export const updateUser = (id, data) => client.patch(`/admin/users/${id}/`, data).then(r => r.data)
export const getAnalytics = () => client.get('/admin/analytics/').then(r => r.data)
```

- [ ] **Step 7: Verify dev server starts**

```bash
npm run dev
```

Expected: Vite server running at `http://localhost:5173`

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold React + Vite with axios client and API modules"
```

---

## Task 2: Auth Context + Protected Routes

**Files:**
- Create: `frontend/src/context/AuthContext.jsx`
- Create: `frontend/src/components/layout/ProtectedRoute.jsx`
- Create: `frontend/src/components/layout/Navbar.jsx`
- Create: `frontend/src/App.jsx`

- [ ] **Step 1: Write `src/context/AuthContext.jsx`**

```jsx
import { createContext, useContext, useState, useEffect } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(undefined)  // undefined = loading, null = not authed

  useEffect(() => {
    client.post('/auth/refresh/')
      .then(() => client.get('/plots/').then(() => setUser(true)))
      .catch(() => setUser(null))
  }, [])

  const login = async (email, password) => {
    await client.post('/auth/login/', { email, password })
    setUser(true)
  }

  const logout = async () => {
    await client.post('/auth/logout/').catch(() => {})
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
```

Note: Add `POST /api/auth/logout/` to the Django backend that clears the cookies:

```python
# Add to apps/users/views.py
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({'detail': 'Logged out.'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
```

```python
# Add to apps/users/urls.py
from .views import LogoutView
path('logout/', LogoutView.as_view()),
```

- [ ] **Step 2: Write `src/components/layout/ProtectedRoute.jsx`**

```jsx
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { user } = useAuth()
  if (user === undefined) return <div className="loading">Loading...</div>
  if (user === null) return <Navigate to="/login" replace />
  return children
}
```

- [ ] **Step 3: Write `src/components/layout/Navbar.jsx`**

```jsx
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function Navbar() {
  const { logout } = useAuth()
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
        <button onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  )
}
```

- [ ] **Step 4: Write `src/App.jsx`**

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/layout/ProtectedRoute'
import Navbar from './components/layout/Navbar'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import NewPlot from './pages/NewPlot'
import PlotDetail from './pages/PlotDetail'
import EditPlot from './pages/EditPlot'
import Admin from './pages/Admin'

function Layout({ children }) {
  return (
    <>
      <Navbar />
      <main className="main-content">{children}</main>
    </>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={
            <ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>
          } />
          <Route path="/plots/new" element={
            <ProtectedRoute><Layout><NewPlot /></Layout></ProtectedRoute>
          } />
          <Route path="/plots/:id" element={
            <ProtectedRoute><Layout><PlotDetail /></Layout></ProtectedRoute>
          } />
          <Route path="/plots/:id/edit" element={
            <ProtectedRoute><Layout><EditPlot /></Layout></ProtectedRoute>
          } />
          <Route path="/admin" element={
            <ProtectedRoute><Layout><Admin /></Layout></ProtectedRoute>
          } />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
```

- [ ] **Step 5: Write `src/main.jsx`**

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import 'leaflet/dist/leaflet.css'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

- [ ] **Step 6: Write `src/index.css`** (minimal base styles)

```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, sans-serif; background: #f5f5f5; color: #1a1a1a; }
.navbar { display: flex; align-items: center; justify-content: space-between;
          padding: 0 1.5rem; height: 56px; background: #1a3a2a; color: white; }
.navbar-brand { color: white; font-weight: bold; font-size: 1.1rem; text-decoration: none; }
.navbar-links { display: flex; gap: 1.5rem; align-items: center; }
.navbar-links a { color: #cce8d4; text-decoration: none; }
.navbar-links button { background: transparent; border: 1px solid #cce8d4; color: #cce8d4;
                        padding: 4px 12px; border-radius: 4px; cursor: pointer; }
.main-content { padding: 0; }
.loading { display: flex; align-items: center; justify-content: center; height: 80vh;
           font-size: 1rem; color: #666; }
```

- [ ] **Step 7: Commit**

```bash
git add frontend/src/
git commit -m "feat: add auth context, protected routes, and app routing"
```

---

## Task 3: Login Page

**Files:**
- Create: `frontend/src/pages/Login.jsx`

- [ ] **Step 1: Write `src/pages/Login.jsx`**

```jsx
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
```

- [ ] **Step 2: Verify in browser**

Start backend: `python manage.py runserver`
Start frontend: `npm run dev`
Open `http://localhost:5173` — should redirect to `/login`. Test login with `farmer@demo.com / farmer1234`. Should redirect to `/dashboard` (blank for now).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Login.jsx
git commit -m "feat: add login and register page"
```

---

## Task 4: Leaflet Map Component

**Files:**
- Create: `frontend/src/components/PlotMap.jsx`

- [ ] **Step 1: Fix Leaflet default marker icons**

Vite doesn't bundle Leaflet's default marker PNGs correctly. Add this workaround to `src/main.jsx` (before the App import):

```jsx
import L from 'leaflet'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({ iconUrl: markerIcon, shadowUrl: markerShadow })
```

- [ ] **Step 2: Write `src/components/PlotMap.jsx`**

```jsx
import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet-draw/dist/leaflet.draw.css'
import 'leaflet-draw'

export default function PlotMap({ onGeometryChange, existingGeometry = null, height = '50vh' }) {
  const mapRef = useRef(null)
  const mapInstanceRef = useRef(null)
  const drawnLayersRef = useRef(null)
  const [mode, setMode] = useState('pin')  // 'pin' | 'polygon'

  useEffect(() => {
    if (mapInstanceRef.current) return

    const map = L.map(mapRef.current).setView([-28.5, 24.5], 6)
    mapInstanceRef.current = map

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map)

    const drawnItems = new L.FeatureGroup()
    map.addLayer(drawnItems)
    drawnLayersRef.current = drawnItems

    if (existingGeometry) {
      const layer = L.geoJSON(existingGeometry)
      drawnItems.addLayer(layer)
      map.fitBounds(layer.getBounds())
    }

    map.on('click', (e) => {
      if (mode !== 'pin') return
      drawnItems.clearLayers()
      const marker = L.marker(e.latlng)
      drawnItems.addLayer(marker)
      onGeometryChange?.({
        type: 'Point',
        coordinates: [e.latlng.lng, e.latlng.lat]
      })
    })

    map.on(L.Draw.Event.CREATED, (e) => {
      drawnItems.clearLayers()
      drawnItems.addLayer(e.layer)
      onGeometryChange?.(e.layer.toGeoJSON().geometry)
    })

    return () => { map.remove(); mapInstanceRef.current = null }
  }, [])

  const activatePolygonDraw = () => {
    setMode('polygon')
    drawnLayersRef.current?.clearLayers()
    const drawControl = new L.Draw.Polygon(mapInstanceRef.current)
    drawControl.enable()
  }

  const switchToPin = () => {
    setMode('pin')
    drawnLayersRef.current?.clearLayers()
    onGeometryChange?.(null)
  }

  return (
    <div style={{ position: 'relative' }}>
      <div ref={mapRef} style={{ height, width: '100%' }} />
      <div style={{ position: 'absolute', top: 12, right: 12, zIndex: 1000, display: 'flex', gap: 8 }}>
        <button onClick={switchToPin}
          style={{ padding: '6px 14px', background: mode === 'pin' ? '#1a3a2a' : 'white',
                   color: mode === 'pin' ? 'white' : '#1a3a2a', border: '1px solid #1a3a2a',
                   borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}>
          📍 Pin
        </button>
        <button onClick={activatePolygonDraw}
          style={{ padding: '6px 14px', background: mode === 'polygon' ? '#1a3a2a' : 'white',
                   color: mode === 'polygon' ? 'white' : '#1a3a2a', border: '1px solid #1a3a2a',
                   borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}>
          ⬡ Draw Boundary
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/PlotMap.jsx frontend/src/main.jsx
git commit -m "feat: add Leaflet map component with pin and polygon draw modes"
```

---

## Task 5: New Plot Page

**Files:**
- Create: `frontend/src/pages/NewPlot.jsx`

- [ ] **Step 1: Write `src/pages/NewPlot.jsx`**

```jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import PlotMap from '../components/PlotMap'
import { createPlot, listCropTags } from '../api/plots'

export default function NewPlot() {
  const [geometry, setGeometry] = useState(null)
  const [name, setName] = useState('')
  const [cropTags, setCropTags] = useState([])
  const [selectedTags, setSelectedTags] = useState([])
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    listCropTags().then(setCropTags)
  }, [])

  const toggleTag = (id) => {
    setSelectedTags(prev => prev.includes(id) ? prev.filter(t => t !== id) : [...prev, id])
  }

  const handleSave = async () => {
    if (!name.trim()) return setError('Plot name is required.')
    if (!geometry) return setError('Click the map to set a location, or draw a boundary.')
    setSaving(true)
    try {
      const plot = await createPlot({ name: name.trim(), geometry, crop_tag_ids: selectedTags })
      navigate(`/plots/${plot.id}`)
    } catch {
      setError('Failed to save plot. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <PlotMap onGeometryChange={setGeometry} height="50vh" />
      <div style={{ padding: '1.5rem', maxWidth: 640, margin: '0 auto' }}>
        <h2 style={{ marginBottom: '1rem' }}>New Plot</h2>
        <label style={{ display: 'block', marginBottom: 6, fontWeight: 600 }}>Plot Name</label>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. North Field"
          style={{ width: '100%', padding: '8px 12px', marginBottom: 16, border: '1px solid #ddd', borderRadius: 4 }} />
        <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>Crops (optional)</label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
          {cropTags.map(tag => (
            <button key={tag.id} onClick={() => toggleTag(tag.id)}
              style={{ padding: '4px 12px', borderRadius: 20, cursor: 'pointer',
                       background: selectedTags.includes(tag.id) ? '#1a3a2a' : 'white',
                       color: selectedTags.includes(tag.id) ? 'white' : '#1a3a2a',
                       border: '1px solid #1a3a2a' }}>
              {tag.name}
            </button>
          ))}
        </div>
        {geometry && (
          <p style={{ color: '#2e7d32', marginBottom: 12, fontSize: 14 }}>
            ✓ Location set ({geometry.type === 'Point' ? 'pin' : 'polygon boundary'})
          </p>
        )}
        {error && <p style={{ color: '#c0392b', marginBottom: 12, fontSize: 14 }}>{error}</p>}
        <button onClick={handleSave} disabled={saving}
          style={{ padding: '10px 24px', background: '#1a3a2a', color: 'white',
                   border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}>
          {saving ? 'Saving...' : 'Save Plot'}
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify in browser**

Open `http://localhost:5173/plots/new`, click the map to set a pin, fill in a name, press Save. Should redirect to `/plots/:id`.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/NewPlot.jsx
git commit -m "feat: add new plot page with map, crop tag selection, and save"
```

---

## Task 6: Recommendation Components + Plot Detail

**Files:**
- Create: `frontend/src/components/RecommendationCard.jsx`
- Create: `frontend/src/components/RecommendationList.jsx`
- Create: `frontend/src/hooks/useRecommendations.js`
- Create: `frontend/src/pages/PlotDetail.jsx`

- [ ] **Step 1: Write `src/components/RecommendationCard.jsx`**

```jsx
const STATUS_CONFIG = {
  green:  { bg: '#e8f5e9', border: '#43a047', icon: '🟢', label: 'Good' },
  amber:  { bg: '#fff8e1', border: '#f9a825', icon: '🟡', label: 'Caution' },
  red:    { bg: '#ffebee', border: '#e53935', icon: '🔴', label: 'Hold' },
}

const ACTIVITY_LABELS = {
  spray: '🌿 Spray', irrigate: '💧 Irrigate', plant: '🌱 Plant', harvest: '🌾 Harvest'
}

export default function RecommendationCard({ card }) {
  const cfg = STATUS_CONFIG[card.status] ?? STATUS_CONFIG.amber

  return (
    <div style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, borderLeft: `4px solid ${cfg.border}`,
                  borderRadius: 8, padding: '1rem 1.25rem', marginBottom: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#666', textTransform: 'uppercase',
                        marginBottom: 4 }}>
            {ACTIVITY_LABELS[card.activity] ?? card.activity}
          </div>
          <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>{card.title}</div>
          <div style={{ fontSize: 13, color: '#555' }}>{card.reason}</div>
        </div>
        <span style={{ fontSize: 22, marginLeft: 12 }}>{cfg.icon}</span>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Write `src/hooks/useRecommendations.js`**

```js
import { useState, useEffect } from 'react'
import { getRecommendations } from '../api/recommendations'

export default function useRecommendations(plotId) {
  const [cards, setCards] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!plotId) return
    setLoading(true)
    getRecommendations(plotId)
      .then(data => { setCards(data); setLoading(false) })
      .catch(() => { setError('Could not load recommendations.'); setLoading(false) })
  }, [plotId])

  return { cards, loading, error }
}
```

- [ ] **Step 3: Write `src/components/RecommendationList.jsx`**

```jsx
import RecommendationCard from './RecommendationCard'
import useRecommendations from '../hooks/useRecommendations'

export default function RecommendationList({ plotId }) {
  const { cards, loading, error } = useRecommendations(plotId)

  if (loading) return (
    <div style={{ padding: '2rem', textAlign: 'center', color: '#888' }}>
      Analyzing weather conditions...
    </div>
  )
  if (error) return <p style={{ color: '#c0392b', padding: '1rem' }}>{error}</p>

  const sorted = [...cards].sort((a, b) => {
    const order = { red: 0, amber: 1, green: 2 }
    return (order[a.status] ?? 3) - (order[b.status] ?? 3)
  })

  return (
    <div>
      <h3 style={{ marginBottom: '1rem', fontSize: 14, fontWeight: 600,
                   textTransform: 'uppercase', color: '#666', letterSpacing: '0.05em' }}>
        Today's Recommendations
      </h3>
      {sorted.map((card, i) => <RecommendationCard key={i} card={card} />)}
    </div>
  )
}
```

- [ ] **Step 4: Write `src/pages/PlotDetail.jsx`**

```jsx
import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import PlotMap from '../components/PlotMap'
import RecommendationList from '../components/RecommendationList'
import { getPlot, deletePlot } from '../api/plots'

export default function PlotDetail() {
  const { id } = useParams()
  const [plot, setPlot] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    getPlot(id).then(setPlot)
  }, [id])

  const handleDelete = async () => {
    if (!confirm(`Delete "${plot.name}"?`)) return
    await deletePlot(id)
    navigate('/dashboard')
  }

  if (!plot) return <div className="loading">Loading plot...</div>

  return (
    <div>
      <PlotMap existingGeometry={plot.geometry} height="40vh" />
      <div style={{ padding: '1.5rem', maxWidth: 640, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
          <div>
            <h2>{plot.name}</h2>
            <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
              {plot.crop_tags.map(t => t.name).join(', ') || 'No crops tagged'}
              {plot.area_hectares ? ` · ${plot.area_hectares.toFixed(1)} ha` : ''}
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <Link to={`/plots/${id}/edit`}
              style={{ padding: '6px 16px', border: '1px solid #1a3a2a', color: '#1a3a2a',
                       borderRadius: 4, textDecoration: 'none', fontSize: 14 }}>
              Edit
            </Link>
            <button onClick={handleDelete}
              style={{ padding: '6px 16px', background: '#c0392b', color: 'white',
                       border: 'none', borderRadius: 4, cursor: 'pointer', fontSize: 14 }}>
              Delete
            </button>
          </div>
        </div>
        <RecommendationList plotId={id} />
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Verify in browser**

Navigate to a saved plot's URL. Map should show the existing geometry. Recommendation cards should load (may take a few seconds on first load — LLM call). Cards should be ordered red → amber → green.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/ frontend/src/hooks/ frontend/src/pages/PlotDetail.jsx
git commit -m "feat: add recommendation cards, hook, and plot detail page"
```

---

## Task 7: Dashboard + Edit Plot

**Files:**
- Create: `frontend/src/pages/Dashboard.jsx`
- Create: `frontend/src/pages/EditPlot.jsx`

- [ ] **Step 1: Write `src/pages/Dashboard.jsx`**

```jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import PlotMap from '../components/PlotMap'
import RecommendationList from '../components/RecommendationList'
import { listPlots } from '../api/plots'

export default function Dashboard() {
  const [plots, setPlots] = useState([])
  const [selectedPlotId, setSelectedPlotId] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    listPlots().then(data => {
      setPlots(data)
      if (data.length > 0) setSelectedPlotId(data[0].id)
    })
  }, [])

  const selectedPlot = plots.find(p => p.id === selectedPlotId)

  return (
    <div>
      <PlotMap
        existingGeometry={selectedPlot?.geometry ?? null}
        height="45vh"
      />
      <div style={{ padding: '1.5rem', maxWidth: 800, margin: '0 auto' }}>
        {plots.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 0', color: '#666' }}>
            <p style={{ fontSize: 18, marginBottom: 12 }}>No plots yet.</p>
            <button onClick={() => navigate('/plots/new')}
              style={{ padding: '10px 24px', background: '#1a3a2a', color: 'white',
                       border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}>
              + Add Your First Plot
            </button>
          </div>
        ) : (
          <>
            <div style={{ display: 'flex', gap: 8, marginBottom: '1.5rem', flexWrap: 'wrap' }}>
              {plots.map(p => (
                <button key={p.id} onClick={() => setSelectedPlotId(p.id)}
                  style={{ padding: '6px 16px', borderRadius: 20, cursor: 'pointer',
                           background: selectedPlotId === p.id ? '#1a3a2a' : 'white',
                           color: selectedPlotId === p.id ? 'white' : '#1a3a2a',
                           border: '1px solid #1a3a2a', fontWeight: selectedPlotId === p.id ? 'bold' : 'normal' }}>
                  {p.name}
                </button>
              ))}
              <button onClick={() => navigate('/plots/new')}
                style={{ padding: '6px 16px', borderRadius: 20, cursor: 'pointer',
                         background: 'transparent', color: '#666', border: '1px dashed #ccc' }}>
                + Add Plot
              </button>
            </div>
            {selectedPlotId && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div>
                    <h2 style={{ fontSize: 18 }}>{selectedPlot?.name}</h2>
                    <p style={{ fontSize: 13, color: '#888' }}>
                      {selectedPlot?.crop_tags?.map(t => t.name).join(', ') || 'No crops tagged'}
                    </p>
                  </div>
                  <button onClick={() => navigate(`/plots/${selectedPlotId}`)}
                    style={{ padding: '6px 14px', border: '1px solid #1a3a2a', color: '#1a3a2a',
                             background: 'transparent', borderRadius: 4, cursor: 'pointer', fontSize: 13 }}>
                    View Full Detail →
                  </button>
                </div>
                <RecommendationList plotId={selectedPlotId} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Write `src/pages/EditPlot.jsx`**

```jsx
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import PlotMap from '../components/PlotMap'
import { getPlot, updatePlot, listCropTags } from '../api/plots'

export default function EditPlot() {
  const { id } = useParams()
  const [plot, setPlot] = useState(null)
  const [geometry, setGeometry] = useState(null)
  const [name, setName] = useState('')
  const [cropTags, setCropTags] = useState([])
  const [selectedTags, setSelectedTags] = useState([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([getPlot(id), listCropTags()]).then(([p, tags]) => {
      setPlot(p)
      setName(p.name)
      setGeometry(p.geometry)
      setSelectedTags(p.crop_tags.map(t => t.id))
      setCropTags(tags)
    })
  }, [id])

  const toggleTag = (tagId) => {
    setSelectedTags(prev => prev.includes(tagId) ? prev.filter(t => t !== tagId) : [...prev, tagId])
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await updatePlot(id, { name: name.trim(), geometry, crop_tag_ids: selectedTags })
      navigate(`/plots/${id}`)
    } catch {
      setError('Failed to save changes.')
    } finally {
      setSaving(false)
    }
  }

  if (!plot) return <div className="loading">Loading...</div>

  return (
    <div>
      <PlotMap onGeometryChange={setGeometry} existingGeometry={plot.geometry} height="45vh" />
      <div style={{ padding: '1.5rem', maxWidth: 640, margin: '0 auto' }}>
        <h2 style={{ marginBottom: '1rem' }}>Edit Plot</h2>
        <label style={{ display: 'block', marginBottom: 6, fontWeight: 600 }}>Plot Name</label>
        <input value={name} onChange={e => setName(e.target.value)}
          style={{ width: '100%', padding: '8px 12px', marginBottom: 16, border: '1px solid #ddd', borderRadius: 4 }} />
        <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>Crops</label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
          {cropTags.map(tag => (
            <button key={tag.id} onClick={() => toggleTag(tag.id)}
              style={{ padding: '4px 12px', borderRadius: 20, cursor: 'pointer',
                       background: selectedTags.includes(tag.id) ? '#1a3a2a' : 'white',
                       color: selectedTags.includes(tag.id) ? 'white' : '#1a3a2a',
                       border: '1px solid #1a3a2a' }}>
              {tag.name}
            </button>
          ))}
        </div>
        {error && <p style={{ color: '#c0392b', marginBottom: 12 }}>{error}</p>}
        <div style={{ display: 'flex', gap: 12 }}>
          <button onClick={handleSave} disabled={saving}
            style={{ padding: '10px 24px', background: '#1a3a2a', color: 'white',
                     border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
          <button onClick={() => navigate(`/plots/${id}`)}
            style={{ padding: '10px 24px', background: 'white', color: '#666',
                     border: '1px solid #ccc', borderRadius: 4, cursor: 'pointer' }}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Verify in browser**

1. `/dashboard` — plots listed as tabs, switching tab shows recommendations for that plot
2. `/plots/:id/edit` — existing geometry shown on map, can redraw, save updates

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Dashboard.jsx frontend/src/pages/EditPlot.jsx
git commit -m "feat: add dashboard with plot switcher and edit plot page"
```

---

## Task 8: Admin Panel

**Files:**
- Create: `frontend/src/components/AdminUserTable.jsx`
- Create: `frontend/src/components/AnalyticsCharts.jsx`
- Create: `frontend/src/pages/Admin.jsx`

- [ ] **Step 1: Write `src/components/AdminUserTable.jsx`**

```jsx
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
```

- [ ] **Step 2: Write `src/components/AnalyticsCharts.jsx`**

```jsx
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
```

- [ ] **Step 3: Write `src/pages/Admin.jsx`**

```jsx
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
```

- [ ] **Step 4: Add admin link to Navbar for admin users**

Add to `src/components/layout/Navbar.jsx` — fetch current user role and show Admin link conditionally. Update `AuthContext.jsx` to store user details:

In `src/context/AuthContext.jsx`, change the user state to hold the user object:

```jsx
// Replace the useEffect in AuthContext.jsx:
useEffect(() => {
  client.post('/auth/refresh/')
    .then(() => client.get('/auth/me/'))  // Need to add this endpoint
    .then(res => setUser(res.data))
    .catch(() => setUser(null))
}, [])
```

Add `/auth/me/` endpoint to Django:

```python
# In apps/users/views.py
from .serializers import UserSerializer

class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)
```

```python
# In apps/users/urls.py
path('me/', MeView.as_view()),
```

Update `Navbar.jsx` to show admin link:

```jsx
// In Navbar.jsx, add inside navbar-links:
const { user, logout } = useAuth()
// ...
{user?.role === 'admin' && <Link to="/admin">Admin</Link>}
```

- [ ] **Step 5: Verify in browser**

1. Log in as `admin@agrispace.com / admin1234`
2. Navigate to `/admin` — should show stat cards, charts (empty if no snapshots yet), and user table
3. Run `python manage.py snapshot_analytics` in backend terminal to generate a snapshot
4. Refresh `/admin` — stat cards should populate

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/AdminUserTable.jsx \
        frontend/src/components/AnalyticsCharts.jsx \
        frontend/src/pages/Admin.jsx
git add frontend/src/context/AuthContext.jsx \
        frontend/src/components/layout/Navbar.jsx
git commit -m "feat: add admin panel with user management and analytics charts"
```

---

## Frontend Complete

Both plans are now done. Full system smoke test:

1. `cd backend && python manage.py runserver`
2. `cd frontend && npm run dev`
3. Register a new farmer at `http://localhost:5173`
4. Add a plot — drop a pin on any agricultural region
5. View recommendations — 4 LLM-generated cards load within ~3 seconds
6. Log in as admin — verify user list and run `python manage.py snapshot_analytics`
