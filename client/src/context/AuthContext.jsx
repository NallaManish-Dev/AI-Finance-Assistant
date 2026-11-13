import { createContext, useContext, useState } from 'react'

import { apiRequest } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    const saved = localStorage.getItem('finance_auth_session')
    return saved ? JSON.parse(saved) : null
  })

  async function login(credentials) {
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
    const nextSession = { token: data.access_token, user: data.user }
    localStorage.setItem('finance_auth_session', JSON.stringify(nextSession))
    setSession(nextSession)
  }

  async function logout() {
    if (session?.token) {
      await apiRequest('/auth/logout', {
        method: 'POST',
        headers: { Authorization: `Bearer ${session.token}` },
      })
    }
    localStorage.removeItem('finance_auth_session')
    setSession(null)
  }

  return <AuthContext.Provider value={{ session, login, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
