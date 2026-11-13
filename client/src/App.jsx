import { useState } from 'react'

import { useAuth } from './context/AuthContext'
import AuthForm from './pages/AuthForm'
import AiPage from './pages/AiPage'
import BudgetsPage from './pages/BudgetsPage'
import DashboardPage from './pages/DashboardPage'
import TransactionsPage from './pages/TransactionsPage'

function App() {
  const { session, logout } = useAuth()
  const [mode, setMode] = useState('login')
  const [page, setPage] = useState('dashboard')

  if (session) {
    return (
      <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
        <header className="mx-auto mb-8 flex max-w-6xl items-center justify-between"><div><p className="text-sm text-violet-400">AI Finance Assistant</p><p className="text-sm text-slate-400">Signed in as {session.user.name}</p></div><div className="flex gap-2"><button className="rounded-lg border border-slate-700 px-3 py-2 text-sm" onClick={() => setPage('dashboard')}>Overview</button><button className="rounded-lg border border-slate-700 px-3 py-2 text-sm" onClick={() => setPage('transactions')}>Transactions</button><button className="rounded-lg border border-slate-700 px-3 py-2 text-sm" onClick={() => setPage('budgets')}>Budgets</button><button className="rounded-lg border border-slate-700 px-3 py-2 text-sm" onClick={() => setPage('ai')}>AI</button><button className="rounded-lg border border-slate-700 px-4 py-2 text-sm hover:border-violet-400" onClick={logout}>Log out</button></div></header>
        {page === 'dashboard' ? <DashboardPage /> : page === 'transactions' ? <TransactionsPage /> : page === 'budgets' ? <BudgetsPage /> : <AiPage />}
      </main>
    )
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-violet-950 via-slate-950 to-slate-950 px-6 py-12 text-slate-100">
      <AuthForm mode={mode} onModeChange={setMode} />
    </main>
  )
}

export default App
