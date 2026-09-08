import React from 'react';
import { ShieldCheck, Scale, FileText } from 'lucide-react';
import { LegalDisclaimer } from './LegalDisclaimer';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950 mt-16 pt-10 pb-8 text-slate-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <LegalDisclaimer variant="banner" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pb-8 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span className="font-bold text-white font-mono text-base">LABELCHECK</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              AI-assisted screening application for packaged commodities in India. Evaluates packaging labels against The Legal Metrology (Packaged Commodities) Rules, 2011 and official gazette amendments.
            </p>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-3">
              <Scale className="w-4 h-4 text-emerald-400" />
              <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-200">Regulatory Framework</h5>
            </div>
            <ul className="text-xs space-y-1.5 text-slate-400">
              <li>The Legal Metrology Act, 2009 (Act 1 of 2010)</li>
              <li>Legal Metrology (Packaged Commodities) Rules, 2011</li>
              <li>Department of Consumer Affairs, Govt. of India</li>
              <li>Schedules I to IV & Rulebook Version 2026.2</li>
            </ul>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-3">
              <FileText className="w-4 h-4 text-emerald-400" />
              <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-200">Screening Disclaimers</h5>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Screening reports indicate rule-based compliance checks only and do not constitute legal certificates, statutory clearance, or evidence of legal compliance in judicial proceedings.
            </p>
          </div>
        </div>

        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-3">
          <p>© {new Date().getFullYear()} LABELCHECK — Legal Metrology Screening System.</p>
          <div className="flex items-center gap-4">
            <span className="text-slate-400 font-mono">Rulebook: 2026.2</span>
            <span>Deterministic Rule Engine</span>
          </div>
        </div>
      </div>
    </footer>
  );
};