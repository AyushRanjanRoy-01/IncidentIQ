/**
 * Knowledge base page component.
 * 
 * Displays runbooks, post-mortems, and knowledge articles.
 */

import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card } from '../components/common/Card'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { api } from '../services/api'

interface KnowledgeDoc {
  doc_id: string
  title: string
  type: 'runbook' | 'postmortem' | 'article'
  content: string
  tags: string[]
  created_at: string
}

const KnowledgePage: React.FC = () => {
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('all')

  const { data: docs, isLoading, error } = useQuery<KnowledgeDoc[]>({
    queryKey: ['knowledge-docs'],
    queryFn: async () => {
      try {
        const response = await api.get('/api/v1/knowledge')
        return response.data
      } catch (error) {
        // Return mock data if API is not available
        console.warn('API not available, using mock data', error)
        return [
          {
            doc_id: 'doc-001',
            title: 'High API Latency Runbook',
            type: 'runbook' as const,
            content: '# Runbook: High API Latency\n\n## Symptoms\n- API response time > 2s\n- Increased error rates\n\n## Resolution\n1. Check recent deployments\n2. Review database metrics\n3. Consider rollback',
            tags: ['latency', 'api', 'performance'],
            created_at: new Date().toISOString()
          },
          {
            doc_id: 'doc-002',
            title: 'Checkout Incident 2024',
            type: 'postmortem' as const,
            content: '# Post-Mortem: Checkout Service Outage\n\n## Incident Summary\n**Date:** January 15, 2024\n**Duration:** 2 hours\n\n## Root Cause\nDatabase connection pool exhaustion',
            tags: ['incident', 'checkout', 'database'],
            created_at: new Date().toISOString()
          }
        ]
      }
    },
  })

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (error) {
    return <div className="text-red-600">Error loading knowledge base</div>
  }

  const filteredDocs = docs?.filter((doc) => {
    if (filter === 'all') return true
    return doc.type === filter
  }) || []

  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold mb-8">Knowledge Base</h1>

      <div className="mb-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md"
        >
          <option value="all">All Types</option>
          <option value="runbook">Runbooks</option>
          <option value="postmortem">Post-Mortems</option>
          <option value="article">Articles</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <Card title="Documents">
            <div className="space-y-2">
              {filteredDocs.map((doc) => (
                <div
                  key={doc.doc_id}
                  className={`p-4 border rounded-md cursor-pointer hover:bg-gray-50 ${
                    selectedDoc === doc.doc_id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200'
                  }`}
                  onClick={() => setSelectedDoc(doc.doc_id)}
                >
                  <h3 className="font-medium">{doc.title}</h3>
                  <p className="text-sm text-gray-600 capitalize">{doc.type}</p>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {doc.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="lg:col-span-2">
          {selectedDoc ? (
            <Card>
              <div className="prose max-w-none">
                {/* TODO: Render markdown content */}
                <pre className="whitespace-pre-wrap">
                  {docs?.find((d) => d.doc_id === selectedDoc)?.content}
                </pre>
              </div>
            </Card>
          ) : (
            <Card>
              <p className="text-gray-500">Select a document to view content</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default KnowledgePage
