import React from 'react';
import { CheckCircle2, AlertCircle, HelpCircle, MinusCircle, AlertTriangle } from 'lucide-react';
import { ComplianceStatus, OverallStatus } from '../types';

interface StatusBadgeProps {
  status: ComplianceStatus | OverallStatus | string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  let colorClasses = 'bg-slate-800 text-slate-300 border-slate-700';
  let label = status;
  let Icon = HelpCircle;

  switch (status) {
    case 'COMPLIANT':
      colorClasses = 'bg-emerald-950/70 text-emerald-300 border-emerald-700/60';
      label = 'Label appears compliant with configured checks';
      Icon = CheckCircle2;
      break;
    case 'POTENTIAL_ISSUES_DETECTED':
      colorClasses = 'bg-rose-950/70 text-rose-300 border-rose-700/60';
      label = 'Potential compliance issue detected';
      Icon = AlertCircle;
      break;
    case 'PARTIALLY_VERIFIED':
      colorClasses = 'bg-sky-950/70 text-sky-300 border-sky-700/60';
      label = 'Partially Verified';
      Icon = HelpCircle;
      break;
    case 'UNABLE_TO_VERIFY':
      colorClasses = 'bg-slate-800/80 text-slate-300 border-slate-700';
      label = 'Unable to verify from available image';
      Icon = HelpCircle;
      break;
    case 'PASS':
      colorClasses = 'bg-emerald-950/70 text-emerald-300 border-emerald-700/60';
      label = 'PASS';
      Icon = CheckCircle2;
      break;
    case 'FAIL':
      colorClasses = 'bg-rose-950/70 text-rose-300 border-rose-700/60';
      label = 'POTENTIAL ISSUE';
      Icon = AlertCircle;
      break;
    case 'REQUIRES_VERIFICATION':
      colorClasses = 'bg-amber-950/70 text-amber-300 border-amber-700/60';
      label = 'REQUIRES VERIFICATION';
      Icon = AlertTriangle;
      break;
    case 'NOT_APPLICABLE':
      colorClasses = 'bg-slate-800/50 text-slate-400 border-slate-700/40';
      label = 'NOT APPLICABLE';
      Icon = MinusCircle;
      break;
    default:
      break;
  }

  const sizeClasses = size === 'sm' 
    ? 'text-xs px-2 py-0.5 gap-1' 
    : size === 'lg' 
      ? 'text-sm px-3.5 py-1.5 gap-2 font-semibold' 
      : 'text-xs px-2.5 py-1 gap-1.5 font-medium';

  return (
    <span className={`inline-flex items-center rounded-full border shadow-sm ${colorClasses} ${sizeClasses}`}>
      <Icon className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5'} />
      <span>{label}</span>
    </span>
  );
};