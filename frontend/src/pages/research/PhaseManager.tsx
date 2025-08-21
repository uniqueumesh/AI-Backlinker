/**
 * Phase Manager Component - coordinates between research phases
 */
import React from 'react';
import { type ResearchStatus } from '../../services/api';
import { ResultsTable } from '../ResearchPhase';
import { GenerateEmailsPanel, DraftsTable } from '../EmailGenerationPhase';
import { SendPanel, OutcomesTable } from '../EmailSendingPhase';

interface PhaseManagerProps {
  status: ResearchStatus | null;
  selectedUrls: Set<string>;
  setSelectedUrls: React.Dispatch<React.SetStateAction<Set<string>>>;
  egForm: any;
  setEgForm: React.Dispatch<React.SetStateAction<any>>;
  egJobId: string | null;
  egError: string | null;
  egLoading: boolean;
  egProgress: number;
  drafts: any[];
  setDrafts: React.Dispatch<React.SetStateAction<any[]>>;
  sendForm: any;
  setSendForm: React.Dispatch<React.SetStateAction<any>>;
  sendJobId: string | null;
  sendError: string | null;
  sendLoading: boolean;
  sendProgress: number;
  sendResults: any[];
  jobId: string | null;
  onEmailEdit: (url: string, email: string) => void;
  onEmailGenerationStart: () => Promise<void>;
  onSendStart: () => Promise<void>;
}

export function PhaseManager({
  status,
  selectedUrls,
  setSelectedUrls,
  egForm,
  setEgForm,
  egJobId,
  egError,
  egLoading,
  egProgress,
  drafts,
  setDrafts,
  sendForm,
  setSendForm,
  sendJobId,
  sendError,
  sendLoading,
  sendProgress,
  sendResults,
  jobId,
  onEmailEdit,
  onEmailGenerationStart,
  onSendStart
}: PhaseManagerProps) {
  if (!status || status.status !== 'done') return null;

  return (
    <>
      <ResultsTable
        rows={status.results || []}
        selected={selectedUrls}
        onToggleSelect={(url) => setSelectedUrls(prev => {
          const next = new Set(prev);
          if (next.has(url)) next.delete(url); else next.add(url);
          return next;
        })}
        onEditEmail={onEmailEdit}
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
        onChange={(f) => setEgForm((prev: any) => ({ ...prev, ...f }))}
        onStart={onEmailGenerationStart}
        error={egError}
        loading={egLoading || !!egJobId}
        progress={egProgress}
      />

      <DraftsTable 
        rows={drafts} 
        onEdit={(idx, patch) => {
          setDrafts((prev: any[]) => prev.map((r, i) => i === idx ? { ...r, ...patch } : r));
        }} 
      />

      <SendPanel
        disabled={drafts.length === 0}
        from_email={sendForm.from_email}
        rate_limit_per_sec={sendForm.rate_limit_per_sec}
        dry_run={sendForm.dry_run}
        onChange={(patch) => setSendForm((prev: any) => ({ ...prev, ...patch }))}
        onStart={onSendStart}
        error={sendError}
        loading={sendLoading || !!sendJobId}
        progress={sendProgress}
      />

      <OutcomesTable rows={sendResults} />
    </>
  );
}
