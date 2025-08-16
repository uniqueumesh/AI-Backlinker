import { useEffect, useState } from 'react'
import { startResearch, getResearchStatus, type ResearchStatus } from '../services/api'
import { SignedIn } from '@clerk/clerk-react'

export default function ResearchPage() {
  const [keyword, setKeyword] = useState('')
  const [jobId, setJobId] = useState<string | null>(null)
  const [status, setStatus] = useState<ResearchStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!jobId) return
    let stop = false
    const poll = async () => {
      try {
        const s = await getResearchStatus(jobId)
        if (stop) return
        setStatus(s)
        if (s.status === 'done' || s.status === 'error') return
        setTimeout(poll, 1500)
      } catch (e: any) {
        if (stop) return
        setError(e?.message || 'Failed to fetch status')
      }
    }
    poll()
    return () => { stop = true }
  }, [jobId])

  const onStart = async () => {
    setError(null)
    setStatus(null)
    setJobId(null)
    if (!keyword.trim()) {
      setError('Please enter a keyword')
      return
    }
    try {
      setLoading(true)
      const r = await startResearch(keyword.trim(), 10)
      setJobId(r.job_id)
    } catch (e: any) {
      setError(e?.message || 'Failed to start research')
    } finally {
      setLoading(false)
    }
  }

  return (
    <SignedIn>
      <div className="mt-8">
        <div className="flex gap-2">
          <input
            value={keyword}
            onChange={e => setKeyword(e.target.value)}
            placeholder="Enter keyword (e.g., ai writers)"
            className="flex-1 rounded-md border border-white/15 bg-white/5 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-400 focus:outline-none"
          />
          <button
            onClick={onStart}
            disabled={loading}
            className="rounded-md bg-indigo-500 px-4 py-2 text-sm font-bold text-black disabled:opacity-60"
          >
            {loading ? 'Starting…' : 'Start Research'}
          </button>
        </div>
        {error && <div className="mt-2 text-sm text-amber-300">{error}</div>}
        {status && (
          <div className="mt-4">
            {status.status !== 'done' && status.status !== 'error' && (
              <div className="text-sm text-slate-300">Working… ({Math.round((status.progress || 0) * 100)}%)</div>
            )}
            {status.status === 'error' && (
              <div className="text-sm text-rose-300">{status.error || 'Job failed'}</div>
            )}
            {status.status === 'done' && (
              <ResultsTable rows={status.results || []} />
            )}
          </div>
        )}
      </div>
    </SignedIn>
  )
}

function ResultsTable({ rows }: { rows: NonNullable<ResearchStatus['results']> }) {
  if (!rows || rows.length === 0) {
    return <div className="text-sm text-slate-400">No results found for this keyword.</div>
  }
  return (
    <div className="mt-3 overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-white/10 text-slate-300">
          <tr>
            <th className="py-2 pr-4">URL</th>
            <th className="py-2 pr-4">Domain</th>
            <th className="py-2 pr-4">Title</th>
            <th className="py-2 pr-4">Email</th>
            <th className="py-2 pr-4">Excerpt</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-b border-white/5 align-top">
              <td className="py-2 pr-4 text-indigo-300 underline underline-offset-2"><a href={r.url} target="_blank" rel="noreferrer">{r.url}</a></td>
              <td className="py-2 pr-4 text-slate-200">{r.domain || ''}</td>
              <td className="py-2 pr-4 text-slate-200">{r.title || ''}</td>
              <td className="py-2 pr-4 text-slate-200">{r.contact_email || ''}</td>
              <td className="py-2 pr-4 text-slate-400">{(r.page_excerpt || '').slice(0, 160)}{(r.page_excerpt || '').length > 160 ? '…' : ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


