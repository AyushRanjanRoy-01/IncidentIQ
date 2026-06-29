import React, { useEffect, useState } from 'react'

import Dashboard from '@/pages/Dashboard'
import IncidentDetailPage from '@/pages/IncidentDetailPage'
import IncidentsPage from '@/pages/IncidentsPage'
import KnowledgePage from '@/pages/KnowledgePage'
import LoginPage from '@/pages/LoginPage'
import { useAuthStore } from '@/store'

type View = 'dashboard' | 'incidents' | 'knowledge'

const NavButton: React.FC<{ active: boolean; onClick: () => void; children: React.ReactNode }> = ({
  active,
  onClick,
  children,
}) => (
  <button
    onClick={onClick}
    className={`px-3 py-1.5 rounded text-sm font-medium ${
      active ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
    }`}
  >
    {children}
  </button>
)

const App: React.FC = () => {
  const { token, user, role, logout, bootstrap } = useAuthStore()
  const [view, setView] = useState<View>('dashboard')
  const [selectedIncident, setSelectedIncident] = useState<string | null>(null)

  useEffect(() => {
    void bootstrap()
  }, [bootstrap])

  if (!token) return <LoginPage />

  const openIncident = (id: string) => setSelectedIncident(id)
  const go = (v: View) => {
    setSelectedIncident(null)
    setView(v)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <h1 className="text-lg font-bold text-gray-900">IncidentIQ</h1>
            <nav className="flex gap-2">
              <NavButton
                active={view === 'dashboard' && !selectedIncident}
                onClick={() => go('dashboard')}
              >
                Dashboard
              </NavButton>
              <NavButton
                active={view === 'incidents' && !selectedIncident}
                onClick={() => go('incidents')}
              >
                Incidents
              </NavButton>
              <NavButton
                active={view === 'knowledge' && !selectedIncident}
                onClick={() => go('knowledge')}
              >
                Knowledge
              </NavButton>
            </nav>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-gray-600">
              {user?.username} <span className="text-gray-400">({role})</span>
            </span>
            <button className="text-gray-500 hover:text-gray-800" onClick={logout}>
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6">
        {selectedIncident ? (
          <IncidentDetailPage
            incidentId={selectedIncident}
            onBack={() => setSelectedIncident(null)}
          />
        ) : view === 'incidents' ? (
          <IncidentsPage onSelect={openIncident} />
        ) : view === 'knowledge' ? (
          <KnowledgePage />
        ) : (
          <Dashboard onSelect={openIncident} />
        )}
      </main>
    </div>
  )
}

export default App
