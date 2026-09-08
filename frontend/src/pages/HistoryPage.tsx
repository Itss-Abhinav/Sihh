import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { History, Search, Filter, Trash2, ArrowRight, ScanLine, AlertCircle } from 'lucide-react';
import { scansApi } from '../api/scans';
import { ScanSummaryItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { LegalDisclaimer } from '../components/LegalDisclaimer';

export const HistoryPage: React.FC = () => {
  const [scans, setScans] = useState<ScanSummaryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  useEffect(() => {
    loadScans();
  }, [statusFilter]);

  const loadScans = async () => {
    try {
      setIsLoading(true);
      const data = await scansApi.listScans(statusFilter === 'ALL' ? undefined : statusFilter);
      setScans(data);
    } catch {
      // Handled
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (!window.confirm('Are you sure you want to delete this scan record?')) return;
    try {
      await scansApi.deleteScan(id);
      setScans(prev => prev.filter(s => s.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete scan record.');
    }
  };

  const filteredScans = scans.filter(s => {
    const term = searchQuery.toLowerCase();
    return (
      (s.productName || '').toLowerCase().includes(term) ||
      (s.brandName || '').toLowerCase().includes(term) ||
      (s.category || '').toLowerCase().includes(term)
    );
  });

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <History className="w-6 h-6 text-emerald-400" />
            <span>Screening Scan Archive</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Historical record of automated package screening evaluations under Rulebook 2026.2.
          </p>
        </div>

        <Link
          to="/scan"
          className="inline-flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow-md transition-colors"
        >
          <ScanLine className="w-4 h-4" />
          <span>New Screening Scan</span>
        </Link>
      </div>

      <LegalDisclaimer variant="compact" />

      <div className="glass-panel p-4 rounded-xl border border-slate-800 flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by product, brand, or category..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700/80 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-700/80 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="COMPLIANT">Compliant</option>
            <option value="POTENTIAL_ISSUES_DETECTED">Potential Issues</option>
            <option value="PARTIALLY_VERIFIED">Partially Verified</option>
            <option value="UNABLE_TO_VERIFY">Unable to Verify</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="min-h-[30vh] flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-400"></div>
        </div>
      ) : filteredScans.length === 0 ? (
        <div className="glass-panel p-12 rounded-2xl text-center border border-slate-800 space-y-3">
          <AlertCircle className="w-8 h-8 text-slate-400 mx-auto" />
          <h3 className="text-sm font-semibold text-white">No screening scans found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            {searchQuery ? 'No records matched your search query.' : 'Run your first label screening scan to see compliance results here.'}
          </p>
          <Link
            to="/scan"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400 hover:text-emerald-300 mt-2"
          >
            <span>Scan a package label now</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredScans.map((s) => (
            <Link
              key={s.id}
              to={`/report/${s.id}`}
              className="glass-card p-4 rounded-xl border border-slate-800 hover:border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all hover:bg-slate-900/60 group"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-white text-sm group-hover:text-emerald-300 transition-colors">
                    {s.productName || 'Unspecified Packaged Commodity'}
                  </h4>
                  <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                    {s.brandName || 'Brand'}
                  </span>
                </div>
                <p className="text-xs text-slate-400 font-mono">
                  {s.category || 'General Commodity'} • {new Date(s.createdAt).toLocaleString()}
                </p>
              </div>

              <div className="flex items-center gap-4 shrink-0">
                <div className="flex items-center gap-2 text-xs font-mono">
                  <span className="text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/40">
                    {s.passedCount} pass
                  </span>
                  {s.failedCount > 0 && (
                    <span className="text-rose-400 bg-rose-950/60 px-2 py-0.5 rounded border border-rose-800/40">
                      {s.failedCount} issue{s.failedCount > 1 ? 's' : ''}
                    </span>
                  )}
                </div>

                <StatusBadge status={s.overallStatus} size="sm" />

                <button
                  onClick={(e) => handleDelete(s.id, e)}
                  title="Delete scan"
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};