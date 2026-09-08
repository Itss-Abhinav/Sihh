import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, ScanLine, ArrowRight, Scale } from 'lucide-react';
import { LegalDisclaimer } from '../components/LegalDisclaimer';

export const LandingPage: React.FC = () => {
  return (
    <div className="space-y-16 pb-12">
      <section className="relative overflow-hidden pt-12 pb-16 lg:pt-20 lg:pb-24">
        <div className="absolute inset-0 -z-10 flex items-center justify-center opacity-25 pointer-events-none">
          <div className="w-[600px] h-[600px] bg-emerald-600/20 blur-[120px] rounded-full"></div>
          <div className="w-[400px] h-[400px] bg-teal-600/15 blur-[100px] rounded-full -ml-32"></div>
        </div>

        <div className="max-w-4xl mx-auto text-center space-y-6 px-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/70 border border-emerald-800/60 text-emerald-400 text-xs font-semibold tracking-wide">
            <Scale className="w-3.5 h-3.5" />
            <span>Rulebook Version 2026.2 — Legal Metrology (PC) Rules 2011</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Automated Indian Packaged Commodity <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">Label Screening</span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Screen retail packaging labels against statutory Legal Metrology requirements in seconds. Powered by optical character extraction and a 100% deterministic legal rule engine.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link
              to="/scan"
              className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-6 py-3 rounded-xl shadow-lg shadow-emerald-950/60 transition-all hover:scale-[1.02]"
            >
              <ScanLine className="w-5 h-5" />
              <span>Start Label Scan</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </Link>

            <Link
              to="/history"
              className="flex items-center gap-2 bg-slate-800/80 hover:bg-slate-700/80 text-white font-medium px-5 py-3 rounded-xl border border-slate-700 transition-colors"
            >
              <span>View Scan Archive</span>
            </Link>
          </div>

          <div className="pt-6 max-w-2xl mx-auto">
            <LegalDisclaimer variant="compact" />
          </div>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-10">
          <h2 className="text-xs font-mono font-semibold uppercase tracking-widest text-emerald-400 mb-2">Deterministic Pipeline</h2>
          <h3 className="text-2xl sm:text-3xl font-bold text-white">How LabelCheck Screens Labels</h3>
          <p className="text-slate-400 text-sm max-w-xl mx-auto mt-2">
            AI is strictly confined to character extraction. Legal compliance determinations are 100% governed by hard-coded statutory rule logic.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative">
          {[
            { step: '01', title: 'Package Image', desc: 'Capture label via mobile camera or upload photograph (JPG/PNG/WEBP).' },
            { step: '02', title: 'Optical OCR', desc: 'Isolate text blocks and normalize alphanumeric typography.' },
            { step: '03', title: 'Entity Extraction', desc: 'Identify MRP, quantity, manufacturer, dates, and consumer care.' },
            { step: '04', title: 'Scope & Exemption', desc: 'Evaluate Rule 3 exclusions and Rule 26 small measure exemptions.' },
            { step: '05', title: 'Legal Rule Engine', desc: 'Evaluate 21 statutory rules with official gazette citations.' },
          ].map((item, i) => (
            <div key={i} className="glass-card p-5 rounded-xl border border-slate-800 relative group hover:border-slate-700 transition-colors">
              <span className="text-2xl font-black text-slate-700 group-hover:text-emerald-500/50 transition-colors font-mono">{item.step}</span>
              <h4 className="text-sm font-bold text-white mt-2 mb-1.5">{item.title}</h4>
              <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 pt-6">
        <div className="glass-panel p-8 rounded-2xl border border-slate-800/80">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-8 pb-6 border-b border-slate-800">
            <div>
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <span>Statutory Scope: Legal Metrology (PC) Rules, 2011</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Incorporating consolidated gazette amendments through Rulebook 2026.2.
              </p>
            </div>
            <Link
              to="/scan"
              className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1 shrink-0"
            >
              <span>Test Benchmark Scans</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: 'Mandatory Declarations',
                rule: 'Rule 6(1)(a)-(r)',
                desc: 'Checks for MRP, "inclusive of all taxes" phrase, Unit Sale Price (USP), Net Quantity, Mfg/Import date, and Generic Commodity Name.',
              },
              {
                title: 'Manufacturer & Address Structure',
                rule: 'Rule 6(1)(a) & Rule 10(1)',
                desc: 'Validates complete physical factory/office address including premises, street, city/state, PIN code, and registered short-address provisos.',
              },
              {
                title: 'Quantity & Standard Units',
                rule: 'Rules 11-13',
                desc: 'Detects prohibited qualifying terms ("approx", "minimum") and prohibited non-standard count units ("dozen", "score"). Enforces standard SI units.',
              },
              {
                title: 'Third Schedule "When Packed"',
                rule: 'Third Schedule',
                desc: 'Strictly restricts "when packed" weight qualification exclusively to soaps, lotions, and non-milk creams. Flags unauthorized usage on other goods.',
              },
              {
                title: 'Fourth Schedule Commodity Units',
                rule: 'Fourth Schedule',
                desc: 'Mandates specific metric forms (e.g. curd by weight, ice cream by weight, industrial diesel by volume, garments by number).',
              },
              {
                title: 'Consumer Care Redressal',
                rule: 'Rule 6(2)',
                desc: 'Verifies dedicated consumer grievance contact channels including name/designation, physical address, telephone helpline, and email.',
              },
            ].map((f, i) => (
              <div key={i} className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-white">{f.title}</h4>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/40">
                    {f.rule}
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};