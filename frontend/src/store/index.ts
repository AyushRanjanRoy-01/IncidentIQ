/**
 * Zustand store for global state management.
 * 
 * Provides centralized state management for application.
 */

import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

interface AppState {
  user: {
    id: string | null
    name: string | null
    roles: string[]
  } | null
  theme: 'light' | 'dark'
  notifications: Array<{
    id: string
    message: string
    type: 'info' | 'success' | 'warning' | 'error'
    timestamp: Date
  }>
  setUser: (user: AppState['user']) => void
  setTheme: (theme: 'light' | 'dark') => void
  addNotification: (notification: Omit<AppState['notifications'][0], 'id' | 'timestamp'>) => void
  removeNotification: (id: string) => void
}

export const useAppStore = create<AppState>()(
  devtools(
    (set) => ({
      user: null,
      theme: 'light',
      notifications: [],

      setUser: (user) => set({ user }),

      setTheme: (theme) => {
        set({ theme })
        // TODO: Persist theme preference
        localStorage.setItem('theme', theme)
      },

      addNotification: (notification) =>
        set((state) => ({
          notifications: [
            ...state.notifications,
            {
              ...notification,
              id: Math.random().toString(36).substr(2, 9),
              timestamp: new Date(),
            },
          ],
        })),

      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),
    }),
    { name: 'AppStore' }
  )
)
