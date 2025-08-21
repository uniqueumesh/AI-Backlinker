/**
 * Progress Tracker Component - monitors research job progress
 */
import React from 'react';
import { type ResearchStatus } from '../../services/api';

interface ProgressTrackerProps {
  status: ResearchStatus | null;
}

export function ProgressTracker({ status }: ProgressTrackerProps) {
  if (!status) return null;

  return (
    <div className="mt-4">
      {status.status !== 'done' && status.status !== 'error' && (
        <div className="text-sm text-slate-300">
          Working… ({Math.round((status.progress || 0) * 100)}%)
        </div>
      )}
      {status.status === 'error' && (
        <div className="text-sm text-rose-300">
          {status.error || 'Job failed'}
        </div>
      )}
    </div>
  );
}
