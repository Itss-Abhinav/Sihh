import React from 'react';
import { CheckCircle, AlertTriangle, AlertOctagon, Sparkles } from 'lucide-react';

interface Props {
  selectedDemo: string | null;
  onSelectDemo: (demoId: string) => void;
  disabled?: boolean;
}

export const DemoSelector: React.FC<Props> = ({ selectedDemo, onSelectDemo, disabled }) => {
  const demos = [
    {
      id: 'demoA',
      title: 'Demo A: Mostly Compliant',
      badge: 'Compliant Sample',
      badgeColor: 'text-emerald-400 bg-emerald-950/70 border-emerald-800',
      description: 'SunGold Butter Cookies — MRP with tax clause, standard 200g SI units, complete factory address & consumer care.',
      icon: CheckCircle,
    },
    {
      id: 'demoB',
      title: 'Demo B: Missing Manufacturer',
      badge: 'Critical Omission',
      badgeColor: 'text-amber-400 bg-amber-950/70 border-amber-800',
      description: 'Crunchy Nacho Crisps — Missing manufacturer postal address, missing consumer helpline, price lacks tax clause.',
      icon: AlertTriangle,
    },
    {
      id: 'demoC',
      title: 'Demo C: Multiple Issues',
      badge: 'Multiple Non-Compliances',
      badgeColor: 'text-rose-400 bg-rose-950/70 border-rose-800',
      description: 'Herbal Glow Body Wash — Prohibited "approx" qualifier, invalid "when packed" clause, incomplete city-only address.',
      icon: AlertOctagon,
    },
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300 uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
          <span>Quick Benchmark Demo Scans</span>
        </div>
        <span className="text-[10px] text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
          Synthetic Test Datasets
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {demos.map((d) => {
          const Icon = d.icon;
          const isSelected = selectedDemo === d.id;
          return (
            <button
              key={d.id}
              type="button"
              disabled={disabled}
              onClick={() => onSelectDemo(d.id)}
              className={`text-left p-3.5 rounded-xl border transition-all ${
                isSelected
                  ? 'border-emerald-500 bg-emerald-950/30 ring-1 ring-emerald-500/50 shadow-md shadow-emerald-950/30'
                  : 'border-slate-800 bg-slate-900/50 hover:bg-slate-800/60 hover:border-slate-700'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                  <Icon className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  {d.title}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed mb-2.5">
                {d.description}
              </p>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${d.badgeColor}`}>
                {d.badge}
              </span>
            </button>
          );
        })}
      </div>
      <p className="text-[11px] text-slate-400 italic">
        * Demo datasets are synthetic screening benchmarks for evaluation and testing. They are never presented as real-world manufacturer evidence.
      </p>
    </div>
  );
};