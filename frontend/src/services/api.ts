/**
 * API client.
 *
 * Centralised axios instance with bearer-token auth + typed endpoint helpers.
 * The base URL is relative by default so requests go through the Vite dev proxy
 * (dev) or the nginx reverse proxy (prod). Override with VITE_API_BASE_URL.
 */

import axios from 'axios'

import type {
  Alert,
  DashboardSummary,
  Incident,
  IncidentDetail,
  KnowledgeResult,
  Remediation,
  Token,
  User,
} from '@/types'

export const TOKEN_KEY = 'iq_token'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export const http = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
    }
    return Promise.reject(error)
  }
)

export const AuthAPI = {
  login: (username: string, password: string) =>
    http.post<Token>('/api/v1/auth/login', { username, password }).then((r) => r.data),
  me: () => http.get<User>('/api/v1/auth/me').then((r) => r.data),
}

export const AlertsAPI = {
  list: (service?: string) =>
    http.get<Alert[]>('/api/v1/alerts/', { params: { service } }).then((r) => r.data),
  ingest: (payload: Partial<Alert>) =>
    http.post('/api/v1/alerts/ingest', payload).then((r) => r.data),
}

export const IncidentsAPI = {
  list: (status?: string) =>
    http.get<Incident[]>('/api/v1/incidents/', { params: { status } }).then((r) => r.data),
  get: (id: string) =>
    http.get<IncidentDetail>(`/api/v1/incidents/${id}`).then((r) => r.data),
  analyze: (id: string) =>
    http.post<Incident>(`/api/v1/incidents/${id}/analyze`).then((r) => r.data),
}

export const RemediationAPI = {
  approve: (id: string) =>
    http.post<Remediation>(`/api/v1/remediation/${id}/approve`).then((r) => r.data),
  reject: (id: string, reason: string) =>
    http.post<Remediation>(`/api/v1/remediation/${id}/reject`, { reason }).then((r) => r.data),
}

export const StatsAPI = {
  summary: () => http.get<DashboardSummary>('/api/v1/stats/summary').then((r) => r.data),
}

export const KnowledgeAPI = {
  search: (query: string, top_k = 5) =>
    http
      .post<KnowledgeResult[]>('/api/v1/knowledge/search', { query, top_k })
      .then((r) => r.data),
}
