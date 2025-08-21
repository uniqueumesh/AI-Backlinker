import React from 'react'

interface SendPanelProps {
  disabled: boolean
  from_email: string
  rate_limit_per_sec: number
  dry_run: boolean
  onChange: (patch: Partial<{ 
    from_email: string; 
    rate_limit_per_sec: number; 
    dry_run: boolean; 
  }>) => void
  onStart: () => Promise<void>
  error: string | null
  loading: boolean
  progress?: number
}

export function SendPanel({
  disabled,
  from_email,
  rate_limit_per_sec,
  dry_run,
  onChange,
  onStart,
  error,
  loading,
  progress,
}: SendPanelProps) {
  return (
    <div className="mt-6 rounded-lg border border-white/10 p-4">
      <div className="mb-3 text-sm text-slate-300">Send emails from the drafts below (defaults to dry-run).</div>
      <div className="flex flex-wrap items-end gap-3">
        <div>
          <div className="text-xs text-slate-400">From Email</div>
          <input 
            value={from_email} 
            onChange={e => onChange({ from_email: e.target.value })} 
            placeholder="you@domain.com" 
            className="w-64 rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" 
          />
        </div>
        <div>
          <div className="text-xs text-slate-400">Rate limit (per sec)</div>
          <input 
            type="number" 
            value={rate_limit_per_sec} 
            min={1} 
            max={100} 
            onChange={e => onChange({ rate_limit_per_sec: Number(e.target.value || 10) })} 
            className="w-24 rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" 
          />
        </div>
        <label className="inline-flex items-center gap-2 text-xs text-slate-300">
          <input 
            type="checkbox" 
            checked={dry_run} 
            onChange={e => onChange({ dry_run: e.target.checked })} 
          /> dry-run
        </label>
        <button 
          disabled={disabled || loading} 
          onClick={onStart} 
          className="rounded-md bg-indigo-400 px-4 py-2 text-sm font-bold text-black disabled:opacity-60"
        >
          {loading ? 'Starting…' : 'Send Emails'}
        </button>
      </div>
      {loading && progress !== undefined && (
        <div className="mt-2 text-xs text-slate-400">
          Progress: {Math.round((progress||0)*100)}% - {progress < 1 ? 'Sending emails...' : 'Completed!'}
        </div>
      )}
      {error && <div className="mt-2 text-sm text-amber-300">{error}</div>}
    </div>
  )
}

interface OutcomesTableProps {
  rows: Array<{ 
    row?: number | string; 
    to_email?: string; 
    status?: string; 
    code?: string; 
    message?: string 
  }>
}

export function OutcomesTable({ rows }: OutcomesTableProps) {
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
