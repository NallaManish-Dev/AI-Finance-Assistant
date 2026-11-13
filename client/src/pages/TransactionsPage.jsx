import { useEffect, useState } from 'react'

import { useAuth } from '../context/AuthContext'
import { apiRequest } from '../services/api'

const categories = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Education', 'Other']
const emptyForm = { description: '', amount: '', date: new Date().toISOString().slice(0, 10), type: 'expense', category: 'Other' }

export default function TransactionsPage() {
  const { session } = useAuth()
  const [transactions, setTransactions] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [filters, setFilters] = useState({ search: '', type: '', category: '', start_date: '', end_date: '' })
  const [editingId, setEditingId] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [suggestion, setSuggestion] = useState('')

  const headers = { Authorization: `Bearer ${session.token}` }

  async function loadTransactions(activeFilters = filters) {
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams(Object.entries(activeFilters).filter(([, value]) => value))
      const data = await apiRequest(`/transactions?${params}`, { headers })
      setTransactions(data.transactions)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadTransactions() }, [])

  function updateForm(event) {
    setForm({ ...form, [event.target.name]: event.target.value })
  }

  async function suggestCategory() {
    if (!form.description.trim() || form.type !== 'expense') return
    try {
      const result = await apiRequest('/ml/predict-category', { method: 'POST', headers, body: JSON.stringify({ description: form.description }) })
      if (result.status === 'ok') {
        setForm({ ...form, category: result.predicted_category })
        setSuggestion(`Suggested ${result.predicted_category} (${Math.round(result.confidence * 100)}%). You can still change it.`)
      } else setSuggestion(result.message)
    } catch (requestError) { setSuggestion(requestError.message) }
  }

  async function saveTransaction(event) {
    event.preventDefault()
    setError('')
    try {
      const path = editingId ? `/transactions/${editingId}` : '/transactions'
      await apiRequest(path, {
        method: editingId ? 'PUT' : 'POST', headers, body: JSON.stringify({ ...form, amount: Number(form.amount) }),
      })
      setForm(emptyForm)
      setEditingId(null)
      loadTransactions()
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  function editTransaction(transaction) {
    setEditingId(transaction.id)
    setForm({ ...transaction, amount: String(transaction.amount) })
  }

  async function removeTransaction(id) {
    if (!window.confirm('Delete this transaction?')) return
    try {
      await apiRequest(`/transactions/${id}`, { method: 'DELETE', headers })
      loadTransactions()
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  function applyFilters(event) {
    event.preventDefault()
    loadTransactions(filters)
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <header><p className="text-sm font-medium text-violet-400">Transactions</p><h1 className="text-3xl font-bold">Your money activity</h1></header>
      <section className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <form className="rounded-xl border border-slate-800 bg-slate-900 p-5" onSubmit={saveTransaction}>
          <h2 className="text-lg font-semibold">{editingId ? 'Edit transaction' : 'Add transaction'}</h2>
          <div className="mt-4 space-y-3">
            <div><Field label="Description" name="description" value={form.description} onChange={updateForm} /><button type="button" className="mt-2 text-sm text-violet-300 disabled:text-slate-500" disabled={!form.description || form.type !== 'expense'} onClick={suggestCategory}>Suggest expense category</button>{suggestion && <p className="mt-1 text-xs text-slate-400">{suggestion}</p>}</div>
            <Field label="Amount" name="amount" type="number" min="0.01" step="0.01" value={form.amount} onChange={updateForm} />
            <Field label="Date" name="date" type="date" value={form.date} onChange={updateForm} />
            <Select label="Type" name="type" value={form.type} onChange={updateForm} options={['expense', 'income']} />
            <Select label="Category" name="category" value={form.category} onChange={updateForm} options={categories} />
          </div>
          <button className="mt-5 w-full rounded-lg bg-violet-600 px-4 py-2 font-semibold hover:bg-violet-500">{editingId ? 'Save changes' : 'Add transaction'}</button>
          {editingId && <button type="button" className="mt-3 w-full text-sm text-slate-400" onClick={() => { setEditingId(null); setForm(emptyForm) }}>Cancel edit</button>}
        </form>
        <section className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <form className="flex flex-wrap gap-3" onSubmit={applyFilters}>
            <input className="min-w-40 flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" placeholder="Search description" value={filters.search} onChange={(event) => setFilters({ ...filters, search: event.target.value })} />
            <Select name="type" value={filters.type} onChange={(event) => setFilters({ ...filters, type: event.target.value })} options={['', 'expense', 'income']} />
            <Select name="category" value={filters.category} onChange={(event) => setFilters({ ...filters, category: event.target.value })} options={['', ...categories]} />
            <input aria-label="Start date" className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" type="date" value={filters.start_date} onChange={(event) => setFilters({ ...filters, start_date: event.target.value })} />
            <input aria-label="End date" className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" type="date" value={filters.end_date} onChange={(event) => setFilters({ ...filters, end_date: event.target.value })} />
            <button className="rounded-lg border border-violet-400 px-4 py-2 text-violet-200">Filter</button>
          </form>
          {error && <p className="mt-4 rounded bg-rose-500/10 p-3 text-sm text-rose-300">{error}</p>}
          <div className="mt-5 overflow-x-auto">
            <table className="w-full text-left text-sm"><thead className="border-b border-slate-800 text-slate-400"><tr><th className="pb-3">Description</th><th className="pb-3">Date</th><th className="pb-3">Category</th><th className="pb-3">Amount</th><th className="pb-3" /></tr></thead>
              <tbody>{loading ? <tr><td colSpan="5" className="py-6 text-slate-400">Loading transactions…</td></tr> : transactions.length === 0 ? <tr><td colSpan="5" className="py-6 text-slate-400">No transactions found.</td></tr> : transactions.map((transaction) => <tr className="border-b border-slate-800/70" key={transaction.id}><td className="py-3">{transaction.description}</td><td>{transaction.date}</td><td>{transaction.category}</td><td className={transaction.type === 'income' ? 'text-emerald-400' : 'text-rose-300'}>{transaction.type === 'income' ? '+' : '-'}₹{transaction.amount.toFixed(2)}</td><td className="space-x-3 whitespace-nowrap"><button className="text-violet-300" onClick={() => editTransaction(transaction)}>Edit</button><button className="text-rose-300" onClick={() => removeTransaction(transaction.id)}>Delete</button></td></tr>)}</tbody>
            </table>
          </div>
        </section>
      </section>
    </div>
  )
}

function Field({ label, ...props }) { return <label className="block text-sm text-slate-300">{label}<input className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white" required {...props} /></label> }
function Select({ label, name, value, onChange, options }) { return <label className="block text-sm text-slate-300">{label && `${label}`}<select className="mt-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white" name={name} value={value} onChange={onChange}>{options.map((option) => <option key={option} value={option}>{option || 'All'}</option>)}</select></label> }
