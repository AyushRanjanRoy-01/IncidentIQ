/**
 * Global auth store (Zustand).
 *
 * Holds the JWT + current user, persisted to localStorage so a refresh keeps
 * the session. Exposes login/logout used by the app shell.
 */

import { create } from 'zustand'

import { AuthAPI, TOKEN_KEY } from '@/services/api'
import type { User } from '@/types'

interface AuthState {
  token: string | null
  user: User | null
  role: string | null
  loading: boolean
  error: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  bootstrap: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem(TOKEN_KEY),
  user: null,
  role: null,
  loading: false,
  error: null,

  login: async (username, password) => {
    set({ loading: true, error: null })
    try {
      const token = await AuthAPI.login(username, password)
      localStorage.setItem(TOKEN_KEY, token.access_token)
      const user = await AuthAPI.me()
      set({ token: token.access_token, user, role: token.role, loading: false })
    } catch (err) {
      set({ loading: false, error: 'Invalid username or password' })
      throw err
    }
  },

  logout: () => {
    localStorage.removeItem(TOKEN_KEY)
    set({ token: null, user: null, role: null })
  },

  bootstrap: async () => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) return
    try {
      const user = await AuthAPI.me()
      set({ token, user, role: user.role })
    } catch {
      localStorage.removeItem(TOKEN_KEY)
      set({ token: null, user: null, role: null })
    }
  },
}))
