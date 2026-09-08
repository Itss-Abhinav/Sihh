import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BarChart3, AlertCircle, CheckCircle2, HelpCircle, Layers, TrendingUp, AlertTriangle, ArrowRight } from 'lucide-react';
import { adminApi } from '../api/admin';
import { AdminDashboardStats } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { LegalDisclaimer } from '../components/LegalDisclaimer';

export const AdminPage: React.FC = () => {
  const [stats, setStats] = useState<AdminDashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setIsLoading(true);
        const data = await adminApi.getDashboardMetrics();
        setStats(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch compliance analytics.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-400"></div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="max-w-md mx-auto my-16 p-6 glass-panel rounded-2xl text-center border border-rose-800 space-y-3">
        <AlertCircle className="w-8 h-8 text-rose-400 mx-auto" />
        <h3 className="text-base font-bold text-white">Dashboard Error</h3>
        <p className="text-xs text-slate-300">{error || 'Could not load analytics.'}</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Compliance Screening Analytics</h1>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 border border-emerald-800/60 px-2 py-0.5 rounded">
            Statutory Surveillance
          </span>
        </div>
        <p className="text-xs sm:text-sm text-slate-400">
          Aggregated screening records reflecting automated label verification checks under Rulebook 2026.2.
        </p>
      </div>

      <LegalDisclaimer variant="banner" />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Total Evaluated Scans</span>
            <Layers className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-white font-mono">{stats.totalScans}</span>
            <span className="text-xs text-slate-400 font-mono">records</span>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Screening Compliant</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-emerald-400 font-mono">{stats.compliantScans}</span>
            <span className="text-xs text-emerald-400/80 font-mono">({stats.complianceRatePct}%)</span>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Potential Issues</span>
            <AlertCircle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-rose-400 font-mono">{stats.potentialIssueScans}</span>
            <span className="text-xs text-slate-400 font-mono">flags</span>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Partially / Unverified</span>
            <HelpCircle className="w-4 h-4 text-sky-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-sky-400 font-mono">
              {stats.partiallyVerifiedScans + stats.unableToVerifyScans}
            </span>
            <span className="text-xs text-slate-400 font-mono">reviews</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>Repeated Potential Compliance Issues Detected</span>
            </h3>
            <span className="text-[10px] font-mono text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              Statutory Pattern
            </span>
          </div>

          <p className="text-[11px] text-slate-400 leading-relaxed">
            Screening observations reflecting repeated statutory exceptions detected in packaging declarations. Note: These metrics record automated detections, not judicial findings.
          </p>

          <div className="space-y-3 pt-1">
            {stats.commonPotentialViolations.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">No recurring potential violations recorded.</p>
            ) : (
              stats.commonPotentialViolations.map((v, i) => (
                <div key={i} className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 flex items-center justify-between gap-3">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-slate-200">{v.ruleName}</span>
                      <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-1.5 py-0.2 rounded">
                        {v.ruleCode}
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-400 block">{v.category}</span>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="text-sm font-bold font-mono text-rose-400 block">{v.occurrenceCount}</span>
                    <span className="text-[10px] text-slate-400">occurrences</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              <span>Commodity Category Distribution</span>
            </h3>
            <span className="text-[10px] font-mono text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              Coverage
            </span>
          </div>

          <p className="text-[11px] text-slate-400 leading-relaxed">
            Breakdown of scanned packaged commodities grouped by statutory schedule classification.
          </p>

          <div className="space-y-3 pt-1">
            {stats.categoryDistribution.map((c, i) => {
              const pct = stats.totalScans > 0 ? ((c.count / stats.totalScans) * 100).toFixed(0) : 0;
              return (
                <div key={i} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-slate-300">{c.category}</span>
                    <span className="font-mono text-slate-400">{c.count} ({pct}%)</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full"
                      style={{ width: `${pct}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-emerald-400" />
            <span>Recent Screening Records</span>
          </h3>
          <Link
            to="/history"
            className="text-xs text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-1"
          >
            <span>Full Archive</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="divide-y divide-slate-800 border border-slate-800 rounded-xl overflow-hidden">
          {stats.recentScans.slice(0, 5).map((s) => (
            <Link
              key={s.id}
              to={`/report/${s.id}`}
              className="p-3.5 bg-slate-950/40 hover:bg-slate-900/60 flex items-center justify-between gap-3 text-xs transition-colors"
            >
              <div>
                <span className="font-semibold text-white block">{s.productName || 'Unspecified Commodity'}</span>
                <span className="text-slate-400 font-mono text-[11px]">
                  {s.brandName} • {new Date(s.createdAt).toLocaleDateString()}
                </span>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <StatusBadge status={s.overallStatus} size="sm" />
                <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};