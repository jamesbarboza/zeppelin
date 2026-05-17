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
