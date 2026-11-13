import { useState } from 'react'

import { useAuth } from '../context/AuthContext'
import { apiRequest } from '../services/api'

const categories = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Education', 'Other']
const month = new Date().toISOString().slice(0, 7)

export default function BudgetsPage() {
  const { session } = useAuth()
  const [form, setForm] = useState({ month, total_budget: '', category_limits: {} })
  const [status, setStatus] = useState(null)
  const [error, setError] = useState('')
  const headers = { Authorization: `Bearer ${session.token}` }

  function setLimit(category, value) {
    setForm({ ...form, category_limits: { ...form.category_limits, [category]: value } })
  }

  async function submit(event) {
    event.preventDefault(); setError('')
    const category_limits = Object.fromEntries(Object.entries(form.category_limits).filter(([, value]) => value).map(([key, value]) => [key, Number(value)]))
    try {
      await apiRequest('/budgets', { method: 'POST', headers, body: JSON.stringify({ month: form.month, total_budget: Number(form.total_budget), category_limits }) })
      await loadStatus(form.month)
    } catch (requestError) { setError(requestError.message) }
  }

  async function loadStatus(selectedMonth = form.month) {
    setError('')
    try { setStatus(await apiRequest(`/budgets/status?month=${selectedMonth}`, { headers })) }
    catch (requestError) { setStatus(null); setError(requestError.message) }
  }

  return <div className="mx-auto max-w-5xl space-y-6">
    <header><p className="text-sm font-medium text-violet-400">Budgets</p><h1 className="text-3xl font-bold">Plan a monthly budget</h1></header>
    <div className="grid gap-6 lg:grid-cols-2">
      <form className="rounded-xl border border-slate-800 bg-slate-900 p-5" onSubmit={submit}>
        <label className="block text-sm text-slate-300">Month<input className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 p-2" type="month" value={form.month} onChange={(event) => setForm({ ...form, month: event.target.value })} required /></label>
        <label className="mt-3 block text-sm text-slate-300">Total budget<input className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 p-2" type="number" min="0.01" step="0.01" value={form.total_budget} onChange={(event) => setForm({ ...form, total_budget: event.target.value })} required /></label>
        <p className="mt-5 text-sm font-medium">Optional category limits</p>
        <div className="mt-2 grid grid-cols-2 gap-3">{categories.map((category) => <label className="text-xs text-slate-400" key={category}>{category}<input className="mt-1 w-full rounded border border-slate-700 bg-slate-950 p-2 text-sm text-white" type="number" min="0.01" step="0.01" value={form.category_limits[category] || ''} onChange={(event) => setLimit(category, event.target.value)} /></label>)}</div>
        <button className="mt-5 w-full rounded-lg bg-violet-600 py-2 font-semibold">Save budget</button>
      </form>
      <section className="rounded-xl border border-slate-800 bg-slate-900 p-5"><div className="flex gap-3"><button className="rounded-lg border border-violet-400 px-4 py-2 text-sm" onClick={() => loadStatus()}>View {form.month} status</button></div>
        {error && <p className="mt-4 rounded bg-rose-500/10 p-3 text-sm text-rose-300">{error}</p>}
        {status && <div className="mt-5 space-y-4"><div className="grid grid-cols-3 gap-3 text-center"><Metric label="Spent" value={status.total_spent} /><Metric label="Remaining" value={status.remaining} /><Metric label="Used" value={`${status.percentage_used}%`} /></div><div>{Object.entries(status.category_status).map(([category, item]) => <div className="mt-3" key={category}><div className="flex justify-between text-sm"><span>{category}</span><span>₹{item.spent} / ₹{item.limit}</span></div><div className="mt-1 h-2 overflow-hidden rounded bg-slate-800"><div className="h-full bg-violet-500" style={{ width: `${Math.min(item.percentage_used, 100)}%` }} /></div></div>)}</div></div>}
      </section>
    </div>
  </div>
}

function Metric({ label, value }) { return <div className="rounded-lg bg-slate-950 p-3"><p className="text-xs text-slate-400">{label}</p><p className="mt-1 font-semibold">{typeof value === 'number' ? `₹${value}` : value}</p></div> }
