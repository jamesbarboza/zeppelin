import { createContext, useContext, useState, useEffect } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(undefined)  // undefined = loading, null = not authed

  useEffect(() => {
    client.post('/auth/refresh/')
      .then(() => client.get('/auth/me/'))
      .then(res => setUser(res.data))
      .catch(() => setUser(null))
  }, [])

  const login = async (email, password) => {
    await client.post('/auth/login/', { email, password })
    const res = await client.get('/auth/me/')
    setUser(res.data)
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
