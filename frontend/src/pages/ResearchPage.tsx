import { useEffect, useState } from 'react'
import {
  startResearch,
  getResearchStatus,
  emailsGenerateStart,
  getEmailsGenerateStatus,
  getSendStatus,
  sendStart,
  type ResearchStatus,
  type EmailRow,
} from '../services/api'
import { SignedIn } from '@clerk/clerk-react'

export default function ResearchPage() {
  const [keyword, setKeyword] = useState('')
  const [jobId, setJobId] = useState<string | null>(null)
  const [status, setStatus] = useState<ResearchStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedUrls, setSelectedUrls] = useState<Set<string>>(new Set())

  // Phase 3 state
  const [egForm, setEgForm] = useState({ subject: 'Guest post collaboration', take: 5, provider: 'gemini' as 'gemini' | 'openai', model: '', your_name: '', your_email: '' })
  const [egJobId, setEgJobId] = useState<string | null>(null)
  const [egError, setEgError] = useState<string | null>(null)
  const [egLoading, setEgLoading] = useState(false)
  const [egProgress, setEgProgress] = useState<number>(0)
  const [drafts, setDrafts] = useState<EmailRow[]>([])

  // Phase 4 state (sending)
  const [sendForm, setSendForm] = useState({ provider: 'smtp' as 'sendgrid' | 'mailersend' | 'smtp', from_email: '', rate_limit_per_sec: 10, dry_run: true, sandbox: false })
  const [sendJobId, setSendJobId] = useState<string | null>(null)
  const [sendError, setSendError] = useState<string | null>(null)
  const [sendLoading, setSendLoading] = useState(false)
  const [sendProgress, setSendProgress] = useState<number>(0)
  const [sendResults, setSendResults] = useState<Array<{ row?: number | string; to_email?: string; status?: string; code?: string; message?: string }>>([])

  // Poll email generation status when a job is active
  useEffect(() => {
    if (!egJobId) return
    let stop = false
    const poll = async () => {
      try {
        const s = await getEmailsGenerateStatus(egJobId)
        if (stop) return
        setEgProgress(s.progress || 0)
        if (s.status === 'done') {
          setDrafts(s.results || [])
          setEgJobId(null)
          return
        }
        if (s.status === 'error') {
          setEgError(s.error || 'Email generation failed')
          setEgJobId(null)
          return
        }
        setTimeout(poll, 1500)
      } catch (e: any) {
        if (stop) return
        setEgError(e?.message || 'Failed to fetch email generation status')
        setEgJobId(null)
      }
    }
    poll()
    return () => { stop = true }
  }, [egJobId])

  // Prefill from_email when user enters their email in Phase 3
  useEffect(() => {
    if (egForm.your_email && !sendForm.from_email) {
      setSendForm(s => ({ ...s, from_email: egForm.your_email }))
    }
  }, [egForm.your_email])

  // Poll send status
  useEffect(() => {
    if (!sendJobId) return
    let stop = false
    const poll = async () => {
      try {
        const s = await getSendStatus(sendJobId)
        if (stop) return
        setSendProgress(s.progress || 0)
        if (s.status === 'done') {
          setSendResults(s.results || [])
          setSendJobId(null)
          return
        }
        if (s.status === 'error') {
          setSendError(s.error || 'Sending failed')
          setSendJobId(null)
          return
        }
        setTimeout(poll, 1500)
      } catch (e: any) {
        if (stop) return
        setSendError(e?.message || 'Failed to fetch send status')
        setSendJobId(null)
      }
    }
    poll()
    return () => { stop = true }
  }, [sendJobId])

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
              <>
                <ResultsTable
                  rows={status.results || []}
                  selected={selectedUrls}
                  onToggleSelect={(url) => setSelectedUrls(prev => {
                    const next = new Set(prev)
                    if (next.has(url)) next.delete(url); else next.add(url)
                    return next
                  })}
                  onEditEmail={(url, email) => {
                    // Update local table email for the displayed rows
                    setStatus(s => {
                      if (!s || !s.results) return s
                      const updated = (s.results || []).map(r => r.url === url ? { ...r, contact_email: email } as any : r)
                      return { ...s, results: updated }
                    })
                  }}
                />

                <GenerateEmailsPanel
                  disabled={(status.results || []).length === 0}
                  hasSelection={selectedUrls.size > 0}
                  selectedCount={selectedUrls.size}
                  subject={egForm.subject}
                  take={egForm.take}
                  provider={egForm.provider}
                  model={egForm.model}
                  your_name={egForm.your_name}
                  your_email={egForm.your_email}
                  onChange={(f) => setEgForm(prev => ({ ...prev, ...f }))}
                  onStart={async () => {
                    setEgError(null)
                    setDrafts([])
                    if (!jobId) { setEgError('No research job in context'); return }
                    const selCount = selectedUrls.size
                    if (selCount < 1 || selCount > 10) {
                      setEgError('Please select between 1 and 10 rows')
                      return
                    }
                    try {
                      setEgLoading(true)
                      const res = await emailsGenerateStart({
                        research_job_id: jobId,
                        selected_urls: Array.from(selectedUrls),
                        subject: egForm.subject.trim() || 'Guest post collaboration',
                        take: Math.min(Math.max(selCount, 1), 10),
                        provider: egForm.provider,
                        model: egForm.model || undefined,
                        your_name: egForm.your_name || undefined,
                        your_email: egForm.your_email || undefined,
                      })
                      setEgJobId(res.job_id)
                    } catch (e: any) {
                      setEgError(e?.message || 'Failed to start email generation')
                    } finally {
                      setEgLoading(false)
                    }
                  }}
                  error={egError}
                  loading={egLoading || !!egJobId}
                  progress={egProgress}
                />

                <DraftsTable rows={drafts} onEdit={(idx, patch) => {
                  setDrafts(prev => prev.map((r, i) => i === idx ? { ...r, ...patch } : r))
                }} />

                <SendPanel
                  disabled={drafts.length === 0}
                  provider={sendForm.provider}
                  from_email={sendForm.from_email}
                  rate_limit_per_sec={sendForm.rate_limit_per_sec}
                  dry_run={sendForm.dry_run}
                  sandbox={sendForm.sandbox}
                  onChange={(f) => setSendForm(prev => ({ ...prev, ...f }))}
                  onStart={async () => {
                    setSendError(null)
                    setSendResults([])
                    if (!drafts.length) { setSendError('No drafts to send'); return }
                    const rows = drafts
                      .filter(r => (r.to_email || '').trim())
                      .map(r => ({ to_email: r.to_email, subject: r.subject, body: r.body }))
                    if (!rows.length) { setSendError('No valid recipient emails in drafts'); return }
                    if (!sendForm.from_email.trim()) { setSendError('Please enter From Email'); return }
                    try {
                      setSendLoading(true)
                      const res = await sendStart({
                        provider: sendForm.provider,
                        from_email: sendForm.from_email.trim(),
                        rows,
                        rate_limit_per_sec: sendForm.rate_limit_per_sec,
                        dry_run: sendForm.dry_run,
                        sandbox: sendForm.sandbox,
                      })
                      setSendJobId(res.job_id)
                    } catch (e: any) {
                      setSendError(e?.message || 'Failed to start sending')
                    } finally {
                      setSendLoading(false)
                    }
                  }}
                  error={sendError}
                  loading={sendLoading || !!sendJobId}
                  progress={sendProgress}
                />

                <OutcomesTable rows={sendResults} />
              </>
            )}
          </div>
        )}
      </div>
    </SignedIn>
  )
}

function ResultsTable({ rows, selected, onToggleSelect, onEditEmail }: {
  rows: NonNullable<ResearchStatus['results']>
  selected: Set<string>
  onToggleSelect: (url: string) => void
  onEditEmail: (url: string, email: string) => void
}) {
  if (!rows || rows.length === 0) {
    return <div className="text-sm text-slate-400">No results found for this keyword.</div>
  }
  return (
    <div className="mt-3 overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-white/10 text-slate-300">
          <tr>
            <th className="py-2 pr-4">Select</th>
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
              <td className="py-2 pr-4">
                <input type="checkbox" checked={selected.has(r.url)} onChange={() => onToggleSelect(r.url)} />
              </td>
              <td className="py-2 pr-4 text-indigo-300 underline underline-offset-2"><a href={r.url} target="_blank" rel="noreferrer">{r.url}</a></td>
              <td className="py-2 pr-4 text-slate-200">{r.domain || ''}</td>
              <td className="py-2 pr-4 text-slate-200">{r.title || ''}</td>
              <td className="py-2 pr-4 text-slate-200">
                <input
                  defaultValue={r.contact_email || ''}
                  placeholder="name@domain.com"
                  className="w-56 rounded-md border border-white/15 bg-white/5 px-2 py-1 text-xs"
                  onBlur={e => onEditEmail(r.url, e.target.value.trim())}
                />
              </td>
              <td className="py-2 pr-4 text-slate-400">{(r.page_excerpt || '').slice(0, 160)}{(r.page_excerpt || '').length > 160 ? '…' : ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function GenerateEmailsPanel({
  disabled,
  hasSelection,
  selectedCount,
  subject,
  take,
  provider,
  model,
  your_name,
  your_email,
  onChange,
  onStart,
  error,
  loading,
  progress,
}: {
  disabled: boolean
  hasSelection: boolean
  selectedCount: number
  subject: string
  take: number
  provider: 'gemini' | 'openai'
  model: string
  your_name: string
  your_email: string
  onChange: (patch: Partial<{ subject: string; take: number; provider: 'gemini' | 'openai'; model: string; your_name: string; your_email: string }>) => void
  onStart: () => Promise<void>
  error: string | null
  loading: boolean
  progress?: number
}) {
  return (
    <div className="mt-6 rounded-lg border border-white/10 p-4">
      <div className="mb-3 text-sm text-slate-300">Generate personalized email drafts {hasSelection ? `(using ${selectedCount} selected ${selectedCount===1?'row':'rows'})` : '(select 1–10 rows)'}.</div>
      <div className="flex flex-wrap items-end gap-3">
        <div>
          <div className="text-xs text-slate-400">Your Name</div>
          <input value={your_name} onChange={e => onChange({ your_name: e.target.value })} placeholder="John Doe" className="rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" />
        </div>
        <div>
          <div className="text-xs text-slate-400">Your Email</div>
          <input value={your_email} onChange={e => onChange({ your_email: e.target.value })} placeholder="john@example.com" className="rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" />
        </div>
        <div>
          <div className="text-xs text-slate-400">Subject</div>
          <input value={subject} onChange={e => onChange({ subject: e.target.value })} className="rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" />
        </div>
        <div>
          <div className="text-xs text-slate-400">Take (1–10)</div>
          <input type="number" value={Math.min(Math.max(take,1),10)} min={1} max={10} onChange={e => onChange({ take: Math.min(Math.max(Number(e.target.value || 5),1),10) })} className="w-24 rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" />
        </div>
        <div>
          <div className="text-xs text-slate-400">Provider</div>
          <select value={provider} onChange={e => onChange({ provider: e.target.value as any })} className="rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm">
            <option value="gemini">gemini</option>
            <option value="openai">openai</option>
          </select>
        </div>
        <div>
          <div className="text-xs text-slate-400">Model (optional)</div>
          <input value={model} onChange={e => onChange({ model: e.target.value })} placeholder="gemini-2.5-flash / gpt-4o-mini" className="rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" />
        </div>
        <button disabled={disabled || loading} onClick={onStart} className="rounded-md bg-emerald-400 px-4 py-2 text-sm font-bold text-black disabled:opacity-60">
          {loading ? 'Starting…' : 'Generate Emails'}
        </button>
      </div>
      {loading && progress !== undefined && <div className="mt-2 text-xs text-slate-400">Progress: {Math.round((progress||0)*100)}%</div>}
      {error && <div className="mt-2 text-sm text-amber-300">{error}</div>}
    </div>
  )
}

function DraftsTable({ rows, onEdit }: { rows: EmailRow[]; onEdit: (idx: number, patch: Partial<EmailRow>) => void }) {
  if (!rows || rows.length === 0) return null
  return (
    <div className="mt-4 overflow-x-auto">
      <div className="mb-2 text-sm text-slate-300">Drafts (review and edit before sending)</div>
      <table className="w-full text-left text-sm">
        <thead className="border-b border-white/10 text-slate-300">
          <tr>
            <th className="py-2 pr-4">To</th>
            <th className="py-2 pr-4">Subject</th>
            <th className="py-2 pr-4">Body</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-b border-white/5 align-top">
              <td className="py-2 pr-4">
                <input
                  value={r.to_email || ''}
                  onChange={e => onEdit(i, { to_email: e.target.value })}
                  placeholder="recipient@domain.com"
                  className="w-64 rounded-md border border-white/15 bg-white/5 px-2 py-1 text-xs text-slate-200"
                />
              </td>
              <td className="py-2 pr-4">
                <input
                  value={r.subject}
                  onChange={e => onEdit(i, { subject: e.target.value })}
                  className="w-72 rounded-md border border-white/15 bg-white/5 px-2 py-1 text-xs"
                />
              </td>
              <td className="py-2 pr-4">
                <textarea
                  value={r.body}
                  onChange={e => onEdit(i, { body: e.target.value })}
                  rows={4}
                  className="w-full rounded-md border border-white/15 bg-white/5 p-2 text-xs"
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function SendPanel({
  disabled,
  provider,
  from_email,
  rate_limit_per_sec,
  dry_run,
  sandbox,
  onChange,
  onStart,
  error,
  loading,
  progress,
}: {
  disabled: boolean
  provider: 'sendgrid' | 'mailersend' | 'smtp'
  from_email: string
  rate_limit_per_sec: number
  dry_run: boolean
  sandbox: boolean
  onChange: (patch: Partial<{ provider: 'sendgrid' | 'mailersend' | 'smtp'; from_email: string; rate_limit_per_sec: number; dry_run: boolean; sandbox: boolean }>) => void
  onStart: () => Promise<void>
  error: string | null
  loading: boolean
  progress?: number
}) {
  return (
    <div className="mt-6 rounded-lg border border-white/10 p-4">
      <div className="mb-3 text-sm text-slate-300">Send emails from the drafts below (defaults to dry-run).</div>
      <div className="flex flex-wrap items-end gap-3">
        <div>
          <div className="text-xs text-slate-400">Provider</div>
          <select value={provider} onChange={e => onChange({ provider: e.target.value as any })} className="rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm">
            <option value="smtp">smtp</option>
            <option value="sendgrid">sendgrid</option>
            <option value="mailersend">mailersend</option>
          </select>
        </div>
        <div>
          <div className="text-xs text-slate-400">From Email</div>
          <input value={from_email} onChange={e => onChange({ from_email: e.target.value })} placeholder="you@domain.com" className="w-64 rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" />
        </div>
        <div>
          <div className="text-xs text-slate-400">Rate limit (per sec)</div>
          <input type="number" value={rate_limit_per_sec} min={1} max={100} onChange={e => onChange({ rate_limit_per_sec: Number(e.target.value || 10) })} className="w-24 rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" />
        </div>
        <label className="inline-flex items-center gap-2 text-xs text-slate-300">
          <input type="checkbox" checked={dry_run} onChange={e => onChange({ dry_run: e.target.checked })} /> dry-run
        </label>
        {provider === 'sendgrid' && (
          <label className="inline-flex items-center gap-2 text-xs text-slate-300">
            <input type="checkbox" checked={sandbox} onChange={e => onChange({ sandbox: e.target.checked })} /> sendgrid sandbox
          </label>
        )}
        <button disabled={disabled || loading} onClick={onStart} className="rounded-md bg-indigo-400 px-4 py-2 text-sm font-bold text-black disabled:opacity-60">
          {loading ? 'Starting…' : 'Send Emails'}
        </button>
      </div>
      {loading && progress !== undefined && <div className="mt-2 text-xs text-slate-400">Progress: {Math.round((progress||0)*100)}%</div>}
      {error && <div className="mt-2 text-sm text-amber-300">{error}</div>}
    </div>
  )
}

function OutcomesTable({ rows }: { rows: Array<{ row?: number | string; to_email?: string; status?: string; code?: string; message?: string }> }) {
  if (!rows || rows.length === 0) return null
  return (
    <div className="mt-4 overflow-x-auto">
      <div className="mb-2 text-sm text-slate-300">Send outcomes</div>
      <table className="w-full text-left text-sm">
        <thead className="border-b border-white/10 text-slate-300">
          <tr>
            <th className="py-2 pr-4">Row</th>
            <th className="py-2 pr-4">To</th>
            <th className="py-2 pr-4">Status</th>
            <th className="py-2 pr-4">Code</th>
            <th className="py-2 pr-4">Message</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-b border-white/5 align-top">
              <td className="py-2 pr-4 text-slate-200">{r.row ?? ''}</td>
              <td className="py-2 pr-4 text-slate-200">{r.to_email ?? ''}</td>
              <td className="py-2 pr-4 text-slate-200">{r.status ?? ''}</td>
              <td className="py-2 pr-4 text-slate-200">{r.code ?? ''}</td>
              <td className="py-2 pr-4 text-slate-400">{r.message ?? ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


