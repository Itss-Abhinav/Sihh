import React, { useState, useEffect } from 'react';
import { useParams, useLocation, Link, useNavigate } from 'react-router-dom';
import { 
  AlertCircle, CheckCircle2, MinusCircle, 
  ArrowLeft, RefreshCw, FileText, Printer, AlertTriangle 
} from 'lucide-react';
import { scansApi } from '../api/scans';
import { ScanDetailResponse } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { ComplianceCard } from '../components/ComplianceCard';
import { LegalDisclaimer } from '../components/LegalDisclaimer';

export const ReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  const [scan, setScan] = useState<ScanDetailResponse | null>(location.state?.scanResult || null);
  const [isLoading, setIsLoading] = useState<boolean>(!location.state?.scanResult);
  const [error, setError] = useState<string | null>(null);
  const [activeCategoryFilter, setActiveCategoryFilter] = useState<string>('ALL');
  const [showRawOcr, setShowRawOcr] = useState<boolean>(false);

  useEffect(() => {
    if (!scan && id) {
      const fetchScan = async () => {
        try {
          setIsLoading(true);
          const data = await scansApi.getScan(id);
          setScan(data);
        } catch (err: any) {
          setError(err.response?.data?.detail || 'Failed to retrieve scan report.');
        } finally {
          setIsLoading(false);
        }
      };
      fetchScan();
    }
  }, [id, scan]);

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-3">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-400"></div>
        <p className="text-xs text-slate-400 font-mono">Loading compliance screening report...</p>
      </div>
    );
  }

  if (error || !scan) {
    return (
      <div className="max-w-md mx-auto my-16 p-6 glass-panel rounded-2xl text-center border border-rose-800 space-y-4">
        <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
        <h3 className="text-base font-bold text-white">Report Not Found</h3>
        <p className="text-xs text-slate-300">{error || 'Unable to display compliance report.'}</p>
        <Link
          to="/scan"
          className="inline-flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold px-4 py-2 rounded-lg text-xs"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Perform New Scan</span>
        </Link>
      </div>
    );
  }

  const { summary, checks, extractedData } = scan;

  const categories = ['ALL', ...Array.from(new Set(checks.map(c => c.category)))];

  const filteredChecks = activeCategoryFilter === 'ALL' 
    ? checks 
    : checks.filter(c => c.category === activeCategoryFilter);

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8 print:py-0 print:px-0">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate(-1)}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">Compliance Screening Report</h1>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/70 border border-emerald-800/60 px-2 py-0.5 rounded">
                Rulebook 2026.2
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Scan ID: {scan.id} • {new Date(scan.createdAt).toLocaleString()} • {scan.executionTimeMs}ms
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 print:hidden">
          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-2 rounded-lg transition-colors"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print Report</span>
          </button>
          <Link
            to="/scan"
            className="flex items-center gap-1.5 text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-4 py-2 rounded-lg shadow-md transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>New Scan</span>
          </Link>
        </div>
      </div>

      <LegalDisclaimer variant="banner" />

      <div className="glass-panel p-6 rounded-2xl border border-slate-800 relative overflow-hidden">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Screening Result</span>
            </div>
            <div className="mb-2">
              <StatusBadge status={scan.overallStatus} size="lg" />
            </div>
            <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
              {scan.overallStatus === 'COMPLIANT' && 'Label appears compliant with the configured statutory checks under Legal Metrology Rules 2011.'}
              {scan.overallStatus === 'POTENTIAL_ISSUES_DETECTED' && 'Potential compliance issue detected. Review specific failed checks below.'}
              {scan.overallStatus === 'PARTIALLY_VERIFIED' && 'Checks passed, but certain declarations require manual verification.'}
              {scan.overallStatus === 'UNABLE_TO_VERIFY' && 'Unable to verify from the available image. Missing critical declarations.'}
            </p>
          </div>

          <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800 text-right shrink-0">
            <span className="text-xs text-slate-400 font-medium block">Packaged Commodity</span>
            <span className="text-base font-bold text-white block">{scan.productName || 'Unspecified Commodity'}</span>
            <span className="text-xs text-emerald-400 font-medium block">{scan.brandName} • {scan.category}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Passed Checks</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <span className="text-2xl font-black text-emerald-400 font-mono">{summary.passed}</span>
        </div>

        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Potential Issues</span>
            <AlertCircle className="w-4 h-4 text-rose-400" />
          </div>
          <span className="text-2xl font-black text-rose-400 font-mono">{summary.failed}</span>
        </div>

        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Requires Verification</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <span className="text-2xl font-black text-amber-400 font-mono">
            {(summary.requires_verification || 0) + (summary.unable_to_verify || 0)}
          </span>
        </div>

        <div className="glass-card p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Not Applicable</span>
            <MinusCircle className="w-4 h-4 text-slate-400" />
          </div>
          <span className="text-2xl font-black text-slate-400 font-mono">{summary.not_applicable}</span>
        </div>
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <FileText className="w-4 h-4 text-emerald-400" />
            <span>Extracted Label Declarations (OCR)</span>
          </h3>
          <button
            onClick={() => setShowRawOcr(!showRawOcr)}
            className="text-xs text-emerald-400 hover:text-emerald-300 font-medium"
          >
            {showRawOcr ? 'Hide Raw OCR Text' : 'View Raw OCR Text'}
          </button>
        </div>

        {showRawOcr && (
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
            {scan.rawOcrText || 'No raw OCR text available.'}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {[
            { label: 'MRP', val: extractedData.mrp?.value, conf: extractedData.mrp?.confidence },
            { label: 'Unit Sale Price', val: extractedData.unitSalePrice?.value, conf: extractedData.unitSalePrice?.confidence },
            { label: 'Net Quantity', val: extractedData.netQuantity?.value, conf: extractedData.netQuantity?.confidence },
            { label: 'Generic Name', val: extractedData.genericName?.value, conf: extractedData.genericName?.confidence },
            { label: 'Mfg / Packing Date', val: extractedData.manufactureDate?.value, conf: extractedData.manufactureDate?.confidence },
            { label: 'Manufacturer / Packer', val: extractedData.manufacturerName?.value, conf: extractedData.manufacturerName?.confidence },
            { label: 'Postal Address', val: extractedData.manufacturerAddress?.value, conf: extractedData.manufacturerAddress?.confidence },
            { label: 'Consumer Helpline', val: extractedData.consumerCarePhone?.value || extractedData.consumerCareEmail?.value, conf: extractedData.consumerCarePhone?.confidence },
            { label: 'Country of Origin', val: extractedData.countryOfOrigin?.value, conf: extractedData.countryOfOrigin?.confidence },
          ].map((item, i) => (
            <div key={i} className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 space-y-1">
              <div className="flex items-center justify-between text-[11px] text-slate-400 font-medium">
                <span>{item.label}</span>
                {item.conf && (
                  <span className="font-mono text-[10px] text-emerald-400">
                    {(item.conf * 100).toFixed(0)}% conf
                  </span>
                )}
              </div>
              <p className="text-xs font-semibold text-slate-200 truncate">
                {item.val || <span className="text-slate-400 italic font-normal">Not detected</span>}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-white">Evaluated Legal Metrology Rules</h3>
            <p className="text-xs text-slate-400">Showing {filteredChecks.length} of {checks.length} statutory screening checks</p>
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategoryFilter(cat)}
                className={`text-xs px-2.5 py-1 rounded-lg transition-colors font-medium ${
                  activeCategoryFilter === cat
                    ? 'bg-emerald-500 text-slate-950 font-bold'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          {filteredChecks.map((chk, idx) => (
            <ComplianceCard key={idx} check={chk} />
          ))}
        </div>
      </div>
    </div>
  );
};