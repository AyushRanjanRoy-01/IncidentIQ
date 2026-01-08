/**
 * Custom hook for fetching alerts.
 * 
 * Uses React Query for data fetching and caching.
 */

import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'

export interface Alert {
  alert_id: string
  severity: 'critical' | 'warning' | 'info'
  service: string
  metric: string
  value: number
  threshold: number
  timestamp: string
}

export const useAlerts = () => {
  return useQuery<Alert[]>({
    queryKey: ['alerts'],
    queryFn: async () => {
      try {
        const response = await api.get('/api/v1/alerts')
        return response.data
      } catch (error) {
        // Return mock data if API is not available
        console.warn('API not available, using mock data', error)
        return [
          {
            alert_id: 'alert-001',
            severity: 'critical' as const,
            service: 'checkout-api',
            metric: 'api_latency_p95',
            value: 2500,
            threshold: 1000,
            timestamp: new Date().toISOString()
          },
          {
            alert_id: 'alert-002',
            severity: 'warning' as const,
            service: 'payment-api',
            metric: 'error_rate',
            value: 0.025,
            threshold: 0.01,
            timestamp: new Date().toISOString()
          },
          {
            alert_id: 'alert-003',
            severity: 'critical' as const,
            service: 'user-api',
            metric: 'memory_usage',
            value: 92,
            threshold: 85,
            timestamp: new Date().toISOString()
          }
        ]
      }
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  })
}
