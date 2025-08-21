import React, { useState } from 'react'
import { type EmailRow } from '../services/api'

interface GenerateEmailsPanelProps {
  disabled: boolean
  hasSelection: boolean
  selectedCount: number
  subject: string
  take: number
  provider: 'gemini' | 'openai'
  model: string
  your_name: string
  your_email: string
  onChange: (patch: Partial<{ 
    subject: string; 
    take: number; 
    provider: 'gemini' | 'openai'; 
    model: string; 
    your_name: string; 
    your_email: string 
  }>) => void
  onStart: () => Promise<void>
  error: string | null
  loading: boolean
  progress?: number
}

export function GenerateEmailsPanel({
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
}: GenerateEmailsPanelProps) {
  // Validation according to Phase 3 plan
  const isSubjectValid = subject.trim().length >= 3 && subject.trim().length <= 120
  const isTakeValid = take >= 1 && take <= 100
  const isFormValid = isSubjectValid && isTakeValid && hasSelection && selectedCount >= 1 && selectedCount <= 100

  // Get default model suggestions per provider
  const getDefaultModel = (provider: string) => {
    if (provider === 'gemini') return 'gemini-2.5-flash'
    if (provider === 'openai') return 'gpt-4o-mini'
    return ''
  }

  return (
    <div className="mt-6 rounded-lg border border-white/10 p-4">
      <div className="mb-3 text-sm text-slate-300">
        Generate personalized email drafts {hasSelection ? `(using ${selectedCount} selected ${selectedCount===1?'row':'rows'})` : '(select 1–100 rows)'}.
      </div>
      
      <div className="flex flex-wrap items-end gap-3">
        <div>
          <div className="text-xs text-slate-400">Your Name</div>
          <input 
            value={your_name} 
            onChange={e => onChange({ your_name: e.target.value })} 
            placeholder="John Doe" 
            className="rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" 
          />
        </div>
        <div>
          <div className="text-xs text-slate-400">Your Email</div>
          <input 
            value={your_email} 
            onChange={e => onChange({ your_email: e.target.value })} 
            placeholder="john@example.com" 
            className="rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" 
          />
        </div>
        <div>
          <div className="text-xs text-slate-400">Subject *</div>
          <input 
            value={subject} 
            onChange={e => onChange({ subject: e.target.value })} 
            className={`rounded-md border px-2 py-1 text-sm ${
              subject.trim() && !isSubjectValid 
                ? 'border-amber-400 bg-amber-500/10' 
                : 'border-white/15 bg-white/5'
            }`}
            aria-describedby={subject.trim() && !isSubjectValid ? "subject-error" : undefined}
          />
          {subject.trim() && !isSubjectValid && (
            <div id="subject-error" className="text-xs text-amber-400 mt-1">
              Subject must be 3-120 characters
            </div>
          )}
        </div>
        <div>
          <div className="text-xs text-slate-400">Take (1–100)</div>
          <input 
            type="number" 
            value={Math.min(Math.max(take, 1), 100)} 
            min={1} 
            max={100} 
            onChange={e => onChange({ take: Math.min(Math.max(Number(e.target.value || 5), 1), 100) })} 
            className={`w-24 rounded-md border px-2 py-1 text-sm ${
              !isTakeValid 
                ? 'border-amber-400 bg-amber-500/10' 
                : 'border-white/15 bg-white/5'
            }`}
            aria-describedby={!isTakeValid ? "take-error" : undefined}
          />
          {!isTakeValid && (
            <div id="take-error" className="text-xs text-amber-400 mt-1">
              Must be 1-100
            </div>
          )}
        </div>
        <div>
          <div className="text-xs text-slate-400">Provider</div>
          <select 
            value={provider} 
            onChange={e => {
              const newProvider = e.target.value as 'gemini' | 'openai'
              onChange({ 
                provider: newProvider,
                model: getDefaultModel(newProvider) // Auto-set default model
              })
            }} 
            className="rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm"
          >
            <option value="gemini">Gemini</option>
            <option value="openai">OpenAI</option>
          </select>
        </div>
        <div>
          <div className="text-xs text-slate-400">Model (optional)</div>
          <input 
            value={model} 
            onChange={e => onChange({ model: e.target.value })} 
            placeholder={getDefaultModel(provider)}
            className="rounded-md border border-white/15 bg-white/5 px-2 py-1 text-sm" 
          />
        </div>
        <button 
          disabled={disabled || loading || !isFormValid} 
          onClick={onStart} 
          className="rounded-md bg-emerald-400 px-4 py-2 text-sm font-bold text-black disabled:opacity-60 disabled:cursor-not-allowed"
          aria-describedby={!isFormValid ? "form-error" : undefined}
        >
          {loading ? 'Starting…' : 'Generate Emails'}
        </button>
      </div>

      {/* Progress and Status Indicators */}
      {loading && (
        <div className="mt-3" role="status" aria-live="polite">
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <div className="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
            {progress !== undefined ? (
              <>
                <span>Generating emails…</span>
                <span className="text-xs text-slate-400">({Math.round((progress || 0) * 100)}%)</span>
              </>
            ) : (
              <span>Starting email generation…</span>
            )}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mt-3 p-3 rounded-md bg-amber-500/10 border border-amber-400/30" role="alert">
          <div className="text-sm text-amber-300">
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      {/* Form Validation Summary */}
      {!isFormValid && !loading && (
        <div id="form-error" className="mt-3 text-xs text-slate-400" role="status">
          {!hasSelection && "Please select at least one row from the research results."}
          {hasSelection && selectedCount > 100 && "Please select no more than 100 rows."}
          {hasSelection && selectedCount < 1 && "Please select at least one row."}
        </div>
      )}
    </div>
  )
}

interface DraftsTableProps {
  rows: EmailRow[]
  onEdit: (idx: number, patch: Partial<EmailRow>) => void
}

export function DraftsTable({ rows, onEdit }: DraftsTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())
  
  if (!rows || rows.length === 0) return null

  const toggleExpanded = (idx: number) => {
    setExpandedRows(prev => {
      const next = new Set(prev)
      if (next.has(idx)) next.delete(idx)
      else next.add(idx)
      return next
    })
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      // Could add a toast notification here
    } catch (err) {
      console.error('Failed to copy to clipboard:', err)
    }
  }

  const downloadCSV = () => {
    const csvContent = [
      ['To Email', 'Subject', 'Body', 'URL', 'Domain', 'Title'],
      ...rows.map(row => [
        row.to_email || '',
        row.subject || '',
        row.body || '',
        row.url || '',
        row.domain || '',
        row.title || ''
      ])
    ].map(row => row.map(field => `"${(field || '').replace(/"/g, '""')}"`).join(','))
    .join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `email_drafts_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
  
  return (
    <div className="mt-4 overflow-x-auto">
      <div className="mb-3 flex items-center justify-between">
        <div className="text-sm text-slate-300">
          Drafts (review and edit before sending) - {rows.length} email{rows.length !== 1 ? 's' : ''}
        </div>
        <button
          onClick={downloadCSV}
          className="rounded-md bg-slate-600 px-3 py-1 text-xs text-slate-200 hover:bg-slate-500 transition-colors"
        >
          Download CSV
        </button>
      </div>
      
      <table className="w-full text-left text-sm">
        <thead className="border-b border-white/10 text-slate-300">
          <tr>
            <th className="py-2 pr-4">To</th>
            <th className="py-2 pr-4">Subject</th>
            <th className="py-2 pr-4">Body</th>
            <th className="py-2 pr-4">Actions</th>
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
                <div className="space-y-2">
                  {/* Truncated body with expand/collapse */}
                  <div className="relative">
                    {expandedRows.has(i) ? (
                      <textarea
                        value={r.body}
                        onChange={e => onEdit(i, { body: e.target.value })}
                        rows={6}
                        className="w-full rounded-md border border-white/15 bg-white/5 p-2 text-xs"
                      />
                    ) : (
                      <div className="relative">
                        <div className="max-h-20 overflow-hidden">
                          <textarea
                            value={r.body}
                            onChange={e => onEdit(i, { body: e.target.value })}
                            rows={3}
                            className="w-full rounded-md border border-white/15 bg-white/5 p-2 text-xs resize-none"
                          />
                        </div>
                        {r.body.length > 200 && (
                          <div className="absolute bottom-0 right-0 bg-gradient-to-l from-slate-900 to-transparent px-2 py-1 text-xs text-slate-400">
                            ...
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {/* Expand/Collapse button */}
                  <button
                    onClick={() => toggleExpanded(i)}
                    className="text-xs text-slate-400 hover:text-slate-300 transition-colors"
                  >
                    {expandedRows.has(i) ? 'Collapse' : 'Expand'}
                  </button>
                </div>
              </td>
              <td className="py-2 pr-4">
                <div className="flex flex-col gap-1">
                  <button
                    onClick={() => copyToClipboard(r.body)}
                    className="text-xs text-slate-400 hover:text-slate-300 transition-colors"
                    title="Copy body to clipboard"
                  >
                    Copy Body
                  </button>
                  <button
                    onClick={() => copyToClipboard(`${r.subject}\n\n${r.body}`)}
                    className="text-xs text-slate-400 hover:text-slate-300 transition-colors"
                    title="Copy full email to clipboard"
                  >
                    Copy Full
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
