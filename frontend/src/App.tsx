/**
 * Main application component.
 * 
 * Provides routing, error boundaries, and global layout.
 */

import React, { useState } from 'react'
import Dashboard from './pages/Dashboard'
import IncidentsPage from './pages/IncidentsPage'
import KnowledgePage from './pages/KnowledgePage'

/**
 * Simplified App shell.
 *
 * Uses internal state for navigation to avoid runtime router issues
 * that can cause a blank page during early development.
 */
const App: React.FC = () => {
  const [route, setRoute] = useState<'dashboard' | 'incidents' | 'knowledge'>('dashboard')

  const renderRoute = () => {
    switch (route) {
      case 'incidents':
        return <IncidentsPage />
      case 'knowledge':
        return <KnowledgePage />
      case 'dashboard':
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">AI-SRE Platform (Preview)</h1>
          <nav className="space-x-2">
            <button className="px-3 py-1 rounded bg-blue-500 text-white" onClick={() => setRoute('dashboard')}>Dashboard</button>
            <button className="px-3 py-1 rounded bg-gray-100" onClick={() => setRoute('incidents')}>Incidents</button>
            <button className="px-3 py-1 rounded bg-gray-100" onClick={() => setRoute('knowledge')}>Knowledge</button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        {renderRoute()}
      </main>
    </div>
  )
}

export default App
