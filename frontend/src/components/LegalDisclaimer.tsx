import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface Props {
  variant?: 'banner' | 'compact' | 'callout';
}

export const LegalDisclaimer: React.FC<Props> = ({ variant = 'banner' }) => {
  if (variant === 'compact') {
    return (
      <div className="flex items-center gap-1.5 text-xs text-amber-400 font-medium bg-amber-950/40 border border-amber-800/50 px-2.5 py-1 rounded-full">
        <AlertTriangle className="w-3.5 h-3.5" />
        <span>Automated screening result — not a legal determination.</span>
      </div>
    );
  }

  return (
    <div className="bg-amber-950/40 border-l-4 border-amber-500 p-4 rounded-r-lg shadow-sm">
      <div className="flex items-start gap-3">
        <div className="p-1.5 bg-amber-500/20 text-amber-400 rounded-lg shrink-0 mt-0.5">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-amber-300">Automated Screening Notice</h4>
          <p className="text-xs text-amber-200/80 mt-1 leading-relaxed">
            Automated screening result — not a legal determination. Evaluations are performed deterministically against the configured Legal Metrology (Packaged Commodities) Rules, 2011 (Rulebook 2026.2). Final statutory compliance requires physical verification and official inspection by authorized Legal Metrology officers.
          </p>
        </div>
      </div>
    </div>
  );
};