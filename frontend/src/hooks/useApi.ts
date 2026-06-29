/** React Query hooks wrapping the typed API client. */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { IncidentsAPI, KnowledgeAPI, RemediationAPI, StatsAPI } from '@/services/api'

export function useStats() {
  return useQuery({ queryKey: ['stats'], queryFn: StatsAPI.summary, refetchInterval: 10000 })
}

export function useIncidents(status?: string) {
  return useQuery({
    queryKey: ['incidents', status ?? 'all'],
    queryFn: () => IncidentsAPI.list(status),
    refetchInterval: 10000,
  })
}

export function useIncident(id: string | null) {
  return useQuery({
    queryKey: ['incident', id],
    queryFn: () => IncidentsAPI.get(id as string),
    enabled: !!id,
  })
}

export function useApproveRemediation(incidentId: string | null) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (remediationId: string) => RemediationAPI.approve(remediationId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['incident', incidentId] })
      qc.invalidateQueries({ queryKey: ['incidents'] })
      qc.invalidateQueries({ queryKey: ['stats'] })
    },
  })
}

export function useRejectRemediation(incidentId: string | null) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      RemediationAPI.reject(id, reason),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['incident', incidentId] })
      qc.invalidateQueries({ queryKey: ['incidents'] })
    },
  })
}

export function useKnowledgeSearch() {
  return useMutation({
    mutationFn: ({ query, topK }: { query: string; topK?: number }) =>
      KnowledgeAPI.search(query, topK ?? 5),
  })
}
