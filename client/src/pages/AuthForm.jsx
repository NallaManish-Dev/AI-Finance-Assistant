import { useState } from 'react'

import { useAuth } from '../context/AuthContext'
import { apiRequest } from '../services/api'

export default function AuthForm({ mode, onModeChange }) {
  const { login } = useAuth()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const isRegistering = mode === 'register'

  function updateField(event) {
    setForm({ ...form, [event.target.name]: event.target.value })
  }

  async function submit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isRegistering) {
        await apiRequest('/auth/register', { method: 'POST', body: JSON.stringify(form) })
      }
      await login({ email: form.email, password: form.password })
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="w-full max-w-md rounded-2xl border border-violet-400/20 bg-slate-900/90 p-8 shadow-2xl shadow-violet-950/30">
      <p className="text-sm font-medium text-violet-400">AI Finance Assistant</p>
      <h1 className="mt-2 text-3xl font-bold">{isRegistering ? 'Create your account' : 'Welcome back'}</h1>
      <p className="mt-2 text-sm text-slate-400">{isRegistering ? 'Start managing your personal finances.' : 'Sign in to continue.'}</p>
      <form className="mt-6 space-y-4" onSubmit={submit}>
        {isRegistering && <Input label="Name" name="name" value={form.name} onChange={updateField} />}
        <Input label="Email" name="email" type="email" value={form.email} onChange={updateField} />
        <Input label="Password" name="password" type="password" value={form.password} onChange={updateField} minLength="8" />
        {error && <p className="rounded-md bg-rose-500/10 p-3 text-sm text-rose-300">{error}</p>}
        <button className="w-full rounded-lg bg-violet-600 px-4 py-2.5 font-semibold hover:bg-violet-500 disabled:opacity-60" disabled={loading}>
          {loading ? 'Please wait…' : isRegistering ? 'Create account' : 'Log in'}
        </button>
      </form>
      <button className="mt-5 text-sm text-violet-300 hover:text-violet-200" onClick={() => onModeChange(isRegistering ? 'login' : 'register')}>
        {isRegistering ? 'Already have an account? Log in' : 'Need an account? Register'}
      </button>
    </section>
  )
}

function Input({ label, ...props }) {
  return (
    <label className="block text-sm font-medium text-slate-200">
      {label}
      <input className="mt-1.5 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none focus:border-violet-400" required {...props} />
    </label>
  )
}
