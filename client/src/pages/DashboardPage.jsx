import { useEffect, useState } from 'react'
import { Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { useAuth } from '../context/AuthContext'
import { apiRequest } from '../services/api'

const colors = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#f43f5e', '#06b6d4']

export default function DashboardPage() {
  const { session } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    const headers = { Authorization: `Bearer ${session.token}` }
    Promise.all([apiRequest('/dashboard/summary', { headers }), apiRequest('/analytics/category-breakdown', { headers }), apiRequest('/analytics/monthly-trends', { headers }), apiRequest('/dashboard/recent-transactions', { headers })])
      .then(([summary, categories, trends, recent]) => setData({ summary, categories: categories.categories, trends: trends.trends, recent: recent.transactions }))
      .catch((requestError) => setError(requestError.message))
  }, [])
  if (error) return <p className="mx-auto max-w-6xl rounded bg-rose-500/10 p-4 text-rose-300">{error}</p>
  if (!data) return <p className="mx-auto max-w-6xl text-slate-400">Loading dashboard…</p>
  const { summary } = data
  return <div className="mx-auto max-w-6xl space-y-6"><header><p className="text-sm font-medium text-violet-400">Overview · {summary.month}</p><h1 className="text-3xl font-bold">Financial dashboard</h1></header><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><Card label="Balance" value={summary.balance} /><Card label="Income" value={summary.income} positive /><Card label="Expenses" value={summary.expenses} expense /><Card label="Budget remaining" value={summary.budget_remaining} empty={summary.budget_remaining === null} /></div>{summary.budget_total !== null && <section className="rounded-xl border border-slate-800 bg-slate-900 p-5"><div className="flex justify-between text-sm"><span>Monthly budget progress</span><span>₹{summary.expenses} of ₹{summary.budget_total}</span></div><div className="mt-2 h-2 overflow-hidden rounded bg-slate-800"><div className="h-full bg-violet-500" style={{ width: `${Math.min((summary.expenses / summary.budget_total) * 100, 100)}%` }} /></div></section>}<div className="grid gap-6 lg:grid-cols-2"><ChartCard title="Income and expenses"><ResponsiveContainer width="100%" height={260}><LineChart data={data.trends}><XAxis dataKey="month" /><YAxis /><Tooltip /><Line type="monotone" dataKey="income" stroke="#10b981" /><Line type="monotone" dataKey="expenses" stroke="#f43f5e" /></LineChart></ResponsiveContainer></ChartCard><ChartCard title="Expense categories">{data.categories.length ? <ResponsiveContainer width="100%" height={260}><PieChart><Pie data={data.categories} dataKey="amount" nameKey="category" outerRadius={90}>{data.categories.map((item, index) => <Cell key={item.category} fill={colors[index % colors.length]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer> : <p className="text-slate-400">No expense data for this month.</p>}</ChartCard></div><section className="rounded-xl border border-slate-800 bg-slate-900 p-5"><h2 className="font-semibold">Recent transactions</h2><div className="mt-4 space-y-3">{data.recent.length ? data.recent.map((item) => <div className="flex justify-between border-b border-slate-800 pb-3 text-sm" key={item.id}><span>{item.description} <span className="text-slate-500">· {item.category}</span></span><span className={item.type === 'income' ? 'text-emerald-400' : 'text-rose-300'}>{item.type === 'income' ? '+' : '-'}₹{item.amount}</span></div>) : <p className="text-slate-400">No transactions yet.</p>}</div></section></div>
}
function Card({ label, value, positive, expense, empty }) { return <section className="rounded-xl border border-slate-800 bg-slate-900 p-5"><p className="text-sm text-slate-400">{label}</p><p className={`mt-2 text-2xl font-bold ${positive ? 'text-emerald-400' : expense ? 'text-rose-300' : ''}`}>{empty ? 'No budget' : `₹${value}`}</p></section> }
function ChartCard({ title, children }) { return <section className="rounded-xl border border-slate-800 bg-slate-900 p-5"><h2 className="font-semibold">{title}</h2><div className="mt-4">{children}</div></section> }
