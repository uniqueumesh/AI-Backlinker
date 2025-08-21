import React, { useState } from 'react'
import { type ResearchStatus } from '../services/api'

interface ResultsTableProps {
  rows: NonNullable<ResearchStatus['results']>
  selected: Set<string>
  onToggleSelect: (url: string) => void
  onEditEmail: (url: string, email: string) => void
}

export function ResultsTable({ rows, selected, onToggleSelect, onEditEmail }: ResultsTableProps) {
  const [emailErrors, setEmailErrors] = useState<Map<string, boolean>>(new Map())
  
  if (!rows || rows.length === 0) {
    return <div className="text-sm text-slate-400">No results found for this keyword.</div>
  }

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return email.trim() === '' || emailRegex.test(email.trim())
  }

  const handleEmailChange = (url: string, email: string) => {
    const isValid = validateEmail(email)
    setEmailErrors(prev => {
      const next = new Map(prev)
      if (isValid) {
        next.delete(url)
      } else {
        next.set(url, true)
      }
      return next
    })
    onEditEmail(url, email)
  }

  const handleEmailBlur = (url: string, email: string) => {
    if (email.trim()) {
      const isValid = validateEmail(email)
      setEmailErrors(prev => {
        const next = new Map(prev)
        if (isValid) {
          next.delete(url)
        } else {
          next.set(url, true)
        }
        return next
      })
    }
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
          {rows.map((r, i) => {
            const hasEmailError = emailErrors.get(r.url)
            return (
              <tr key={i} className="border-b border-white/5 align-top">
                <td className="py-2 pr-4">
                  <input 
                    type="checkbox" 
                    checked={selected.has(r.url)} 
                    onChange={() => onToggleSelect(r.url)} 
                  />
                </td>
                <td className="py-2 pr-4 text-indigo-300 underline underline-offset-2">
                  <a href={r.url} target="_blank" rel="noreferrer">{r.url}</a>
                </td>
                <td className="py-2 pr-4 text-slate-200">{r.domain || ''}</td>
                <td className="py-2 pr-4 text-slate-200">{r.title || ''}</td>
                <td className="py-2 pr-4 text-slate-200">
                  <div className="space-y-1">
                    <input
                      defaultValue={r.contact_email || ''}
                      placeholder="name@domain.com"
                      className={`w-56 rounded-md border px-2 py-1 text-xs ${
                        hasEmailError 
                          ? 'border-amber-400 bg-amber-500/10' 
                          : 'border-white/15 bg-white/5'
                      }`}
                      onChange={e => handleEmailChange(r.url, e.target.value)}
                      onBlur={e => handleEmailBlur(r.url, e.target.value)}
                      aria-describedby={hasEmailError ? `email-error-${i}` : undefined}
                    />
                    {hasEmailError && (
                      <div id={`email-error-${i}`} className="text-xs text-amber-400">
                        Please enter a valid email address
                      </div>
                    )}
                  </div>
                </td>
                <td className="py-2 pr-4 text-slate-400">
                  {(r.page_excerpt || '').slice(0, 160)}
                  {(r.page_excerpt || '').length > 160 ? '…' : ''}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
