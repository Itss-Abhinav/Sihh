import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Info, BookOpen } from 'lucide-react';
import { RuleCheckResult } from '../types';
import { StatusBadge } from './StatusBadge';

interface Props {
  check: RuleCheckResult;
}

export const ComplianceCard: React.FC<Props> = ({ check }) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  const getBorderColor = (status: string) => {
    switch (status) {
      case 'PASS':
        return 'border-emerald-800/40 bg-slate-900/60 hover:border-emerald-700/60';
      case 'FAIL':
        return 'border-rose-800/50 bg-rose-950/20 hover:border-rose-700/70';
      case 'REQUIRES_VERIFICATION':
        return 'border-amber-800/50 bg-amber-950/20 hover:border-amber-700/70';
      case 'UNABLE_TO_VERIFY':
        return 'border-slate-800 bg-slate-900/40 hover:border-slate-700';
      case 'NOT_APPLICABLE':
        return 'border-slate-800/50 bg-slate-950/30 opacity-75';
      default:
        return 'border-slate-800 bg-slate-900/40';
    }
  };

  return (
    <div className={`border rounded-xl p-4 transition-all ${getBorderColor(check.status)}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <h4 className="font-semibold text-white text-sm tracking-tight">{check.field}</h4>
            <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700">
              {check.ruleCode}
            </span>
            <span className="text-[10px] font-medium text-slate-400 bg-slate-800/40 px-2 py-0.5 rounded">
              {check.category}
            </span>
          </div>

          <div className="text-xs text-slate-300 space-y-1 mt-2">
            <div>
              <span className="text-slate-400 font-medium">Detected: </span>
              <span className="font-mono text-slate-200 bg-slate-800/80 px-1.5 py-0.5 rounded">
                {check.detectedValue || 'Not detected'}
              </span>
            </div>
            <div>
              <span className="text-slate-400 font-medium">Requirement: </span>
              <span className="text-slate-300">{check.expectedRequirement}</span>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-end gap-2 shrink-0">
          <StatusBadge status={check.status} size="sm" />
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 mt-1 transition-colors"
          >
            <span>{isExpanded ? 'Hide Details' : 'View Citation'}</span>
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-slate-800/70 text-xs leading-relaxed text-slate-300">
        <p>{check.explanation}</p>
      </div>

      {isExpanded && (
        <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-2.5 text-xs">
          <div className="flex items-start gap-2 text-slate-300 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
            <BookOpen className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-emerald-400 block mb-0.5">Statutory Reference</span>
              <span className="font-mono text-slate-300">{check.sourceReference}</span>
            </div>
          </div>

          {check.penaltyNote && (
            <div className="flex items-start gap-2 text-slate-300 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
              <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-amber-400 block mb-0.5">Section 36 Penalty Context (Informational Only)</span>
                <span className="text-slate-400 text-[11px] leading-relaxed">{check.penaltyNote}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};