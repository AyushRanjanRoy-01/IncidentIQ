import React, { useState } from 'react'

import { Button, Card } from '@/components/ui'
import { useAuthStore } from '@/store'

const LoginPage: React.FC = () => {
  const { login, loading, error } = useAuthStore()
  const [username, setUsername] = useState('operator')
  const [password, setPassword] = useState('operator123')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await login(username, password)
    } catch {
      /* error surfaced via store */
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-sm">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">IncidentIQ</h1>
          <p className="text-sm text-gray-500">AI-SRE Platform</p>
        </div>
        <Card>
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
              <input
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? 'Signing in…' : 'Sign in'}
            </Button>
            <p className="text-xs text-gray-400 text-center">
              Demo: operator / operator123 · admin / admin123 · viewer / viewer123
            </p>
          </form>
        </Card>
      </div>
    </div>
  )
}

export default LoginPage
