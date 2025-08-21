/**
 * Main Research Page Container - orchestrates research workflow
 */
import React, { useEffect, useState } from 'react';
import { SignedIn } from '@clerk/clerk-react';
import { 
  startResearch,
  getResearchStatus,
  emailsGenerateStart,
  getEmailsGenerateStatus,
  getSendStatus,
  sendStart,
  type ResearchStatus,
  type EmailRow,
} from '../../services/api';
import { ResearchForm } from './ResearchForm';
import { ProgressTracker } from './ProgressTracker';
import { PhaseManager } from './PhaseManager';

export default function ResearchPage() {
  const [keyword, setKeyword] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<ResearchStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedUrls, setSelectedUrls] = useState<Set<string>>(new Set());

  // Phase 3 state
  const [egForm, setEgForm] = useState({ 
    subject: 'Guest post collaboration', 
    take: 5, 
    provider: 'gemini' as 'gemini' | 'openai', 
    model: '', 
    your_name: '', 
    your_email: '' 
  });
  const [egJobId, setEgJobId] = useState<string | null>(null);
  const [egError, setEgError] = useState<string | null>(null);
  const [egLoading, setEgLoading] = useState(false);
  const [egProgress, setEgProgress] = useState<number>(0);
  const [drafts, setDrafts] = useState<EmailRow[]>([]);

  // Phase 4 state (sending)
  const [sendForm, setSendForm] = useState({ 
    from_email: '', 
    rate_limit_per_sec: 10, 
    dry_run: true
  });
  const [sendJobId, setSendJobId] = useState<string | null>(null);
  const [sendError, setSendError] = useState<string | null>(null);
  const [sendLoading, setSendLoading] = useState(false);
  const [sendProgress, setSendProgress] = useState<number>(0);
  const [sendResults, setSendResults] = useState<Array<{ 
    row?: number | string; 
    to_email?: string; 
    status?: string; 
    code?: string; 
    message?: string 
  }>>([]);

  // Poll email generation status when a job is active
  useEffect(() => {
    if (!egJobId) return;
    let stop = false;
    const poll = async () => {
      try {
        const s = await getEmailsGenerateStatus(egJobId);
        if (stop) return;
        setEgProgress(s.progress || 0);
        if (s.status === 'done') {
          setDrafts(s.results || []);
          setEgJobId(null);
          setEgProgress(0);
          return;
        }
        if (s.status === 'error') {
          setEgError(s.error || 'Email generation failed');
          setEgJobId(null);
          setEgProgress(0);
          return;
        }
        setTimeout(poll, 1500);
      } catch (e: any) {
        if (stop) return;
        setEgError(e?.message || 'Failed to fetch email generation status');
        setEgJobId(null);
        setEgProgress(0);
      }
    };
    poll();
    return () => { stop = true };
  }, [egJobId]);

  // Prefill from_email when user enters their email in Phase 3
  useEffect(() => {
    if (egForm.your_email && !sendForm.from_email) {
      setSendForm(s => ({ ...s, from_email: egForm.your_email }));
    }
  }, [egForm.your_email]);

  // Poll send status
  useEffect(() => {
    if (!sendJobId) return;
    let stop = false;
    const poll = async () => {
      try {
        const s = await getSendStatus(sendJobId);
        if (stop) return;
        setSendProgress(s.progress || 0);
        if (s.status === 'done') {
          setSendResults(s.results || []);
          setSendJobId(null);
          setSendProgress(0);
          return;
        }
        if (s.status === 'error') {
          setSendError(s.error || 'Sending failed');
          setSendJobId(null);
          setSendProgress(0);
          return;
        }
        setTimeout(poll, 1500);
      } catch (e: any) {
        if (stop) return;
        setSendError(e?.message || 'Failed to fetch send status');
        setSendJobId(null);
        setSendProgress(0);
      }
    };
    poll();
    return () => { stop = true };
  }, [sendJobId]);

  // Poll research status
  useEffect(() => {
    if (!jobId) return;
    let stop = false;
    const poll = async () => {
      try {
        const s = await getResearchStatus(jobId);
        if (stop) return;
        setStatus(s);
        if (s.status === 'done' || s.status === 'error') return;
        setTimeout(poll, 1500);
      } catch (e: any) {
        if (stop) return;
        setError(e?.message || 'Failed to fetch status');
      }
    };
    poll();
    return () => { stop = true };
  }, [jobId]);

  const handleResearchStart = async (jobId: string) => {
    setError(null);
    setStatus(null);
    setJobId(jobId);
    setLoading(false);
  };

  const handleEmailEdit = (url: string, email: string) => {
    setStatus(s => {
      if (!s || !s.results) return s;
      const updated = (s.results || []).map(r => 
        r.url === url ? { ...r, contact_email: email } as any : r
      );
      return { ...s, results: updated };
    });
  };

  const handleEmailGenerationStart = async () => {
    setEgError(null);
    setDrafts([]);
    if (!jobId) { 
      setEgError('No research job in context'); 
      return; 
    }
    
    const selCount = selectedUrls.size;
    if (selCount < 1 || selCount > 100) {
      setEgError('Please select between 1 and 100 rows');
      return;
    }

    // Validate that selected URLs have valid contact emails
    const validUrls = Array.from(selectedUrls).filter(url => {
      const row = status?.results?.find(r => r.url === url);
      return row && row.contact_email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(row.contact_email);
    });

    if (validUrls.length === 0) {
      setEgError('Selected rows must have valid contact emails. Please add/edit contact emails in the research results above.');
      return;
    }

    try {
      setEgLoading(true);
      const res = await emailsGenerateStart({
        research_job_id: jobId,
        selected_urls: validUrls,
        subject: egForm.subject.trim() || 'Guest post collaboration',
        take: Math.min(Math.max(egForm.take, 1), 100),
        provider: egForm.provider,
        model: egForm.model || undefined,
        your_name: egForm.your_name || undefined,
        your_email: egForm.your_email || undefined,
      });
      setEgJobId(res.job_id);
    } catch (e: any) {
      setEgError(e?.message || 'Failed to start email generation');
    } finally {
      setEgLoading(false);
    }
  };

  const handleSendStart = async () => {
    setSendError(null);
    setSendResults([]);
    if (!drafts.length) { 
      setSendError('No drafts to send'); 
      return; 
    }
    
    const rows = drafts
      .filter(r => (r.to_email || '').trim())
      .map(r => ({ to_email: r.to_email, subject: r.subject, body: r.body }));
    
    if (!rows.length) { 
      setSendError('No valid recipient emails in drafts'); 
      return; 
    }
    
    if (!sendForm.from_email.trim()) { 
      setSendError('Please enter From Email'); 
      return; 
    }
    
    try {
      setSendLoading(true);
      const res = await sendStart({
        provider: 'smtp', // Default to SMTP
        from_email: sendForm.from_email.trim(),
        rows,
        rate_limit_per_sec: sendForm.rate_limit_per_sec,
        dry_run: sendForm.dry_run,
        sandbox: false, // Default to false
      });
      setSendJobId(res.job_id);
    } catch (e: any) {
      setSendError(e?.message || 'Failed to start sending');
    } finally {
      setSendLoading(false);
    }
  };

  return (
    <SignedIn>
      <div className="mt-8">
        <ResearchForm
          onResearchStart={handleResearchStart}
          loading={loading}
          error={error}
        />
        
        <ProgressTracker status={status} />
        
        {status && (
          <PhaseManager
            status={status}
            selectedUrls={selectedUrls}
            setSelectedUrls={setSelectedUrls}
            egForm={egForm}
            setEgForm={setEgForm}
            egJobId={egJobId}
            egError={egError}
            egLoading={egLoading}
            egProgress={egProgress}
            drafts={drafts}
            setDrafts={setDrafts}
            sendForm={sendForm}
            setSendForm={setSendForm}
            sendJobId={sendJobId}
            sendError={sendError}
            sendLoading={sendLoading}
            sendProgress={sendProgress}
            sendResults={sendResults}
            jobId={jobId}
            onEmailEdit={handleEmailEdit}
            onEmailGenerationStart={handleEmailGenerationStart}
            onSendStart={handleSendStart}
          />
        )}
      </div>
    </SignedIn>
  );
}
