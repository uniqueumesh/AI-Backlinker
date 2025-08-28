/**
 * Research Form Component - handles keyword input and research initiation
 */
import React, { useState } from 'react';
import { startResearch } from '../../services/api';

interface ResearchFormProps {
  onResearchStart: (jobId: string) => void;
  loading: boolean;
  error: string | null;
}

export function ResearchForm({ onResearchStart, loading, error }: ResearchFormProps) {
  const [keyword, setKeyword] = useState('');

  const handleSubmit = async () => {
    if (!keyword.trim()) {
      return;
    }
    
    try {
      const response = await startResearch(keyword.trim(), 3);
      onResearchStart(response.job_id);
    } catch (e: any) {
      // Error handling is done by parent component
      console.error('Research start failed:', e);
    }
  };

  return (
    <div className="flex gap-2">
      <input
        value={keyword}
        onChange={e => setKeyword(e.target.value)}
        placeholder="Enter keyword (e.g., ai writers)"
        className="flex-1 rounded-md border border-white/15 bg-white/5 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-400 focus:outline-none"
      />
      <button
        onClick={handleSubmit}
        disabled={loading || !keyword.trim()}
        className="rounded-md bg-indigo-500 px-4 py-2 text-sm font-bold text-black disabled:opacity-60"
      >
        {loading ? 'Starting…' : 'Start Research'}
      </button>
      {error && <div className="mt-2 text-sm text-amber-300">{error}</div>}
    </div>
  );
}
