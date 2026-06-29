import React, { useState } from 'react'

import { Badge, Button, Card, Spinner } from '@/components/ui'
import { useKnowledgeSearch } from '@/hooks/useApi'

const KnowledgePage: React.FC = () => {
  const [query, setQuery] = useState('high api latency after deployment')
  const search = useKnowledgeSearch()

  const run = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) search.mutate({ query, topK: 5 })
  }

  return (
    <div className="space-y-4">
      <Card title="Knowledge base search (RAG)">
        <form onSubmit={run} className="flex gap-2">
          <input
            className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search runbooks and postmortems…"
          />
          <Button type="submit" disabled={search.isPending}>
            Search
          </Button>
        </form>
      </Card>

      {search.isPending && <Spinner />}

      {search.data && (
        <div className="space-y-3">
          {search.data.length === 0 && (
            <p className="text-sm text-gray-500">No matching documents.</p>
          )}
          {search.data.map((r) => (
            <Card key={r.chunk_id}>
              <div className="flex items-center justify-between mb-1">
                <div className="font-medium text-gray-800">{r.title}</div>
                <div className="flex items-center gap-2">
                  <Badge value={r.source_type} />
                  <span className="text-xs text-gray-400">score {r.score.toFixed(3)}</span>
                </div>
              </div>
              <p className="text-sm text-gray-600 line-clamp-3 whitespace-pre-wrap">
                {r.content.slice(0, 320)}
                {r.content.length > 320 ? '…' : ''}
              </p>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default KnowledgePage
