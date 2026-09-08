import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, ScanLine, History, BarChart3, LogIn, LogOut, User as UserIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();

  const navLinkClass = (path: string) => {
    const isActive = location.pathname === path;
    return `flex items-center gap-1.5 text-sm font-medium transition-colors px-3 py-1.5 rounded-lg ${
      isActive 
        ? 'text-emerald-400 bg-emerald-950/60 border border-emerald-800/40' 
        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
    }`;
  };

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-950/50 group-hover:scale-105 transition-transform">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-lg tracking-tight text-white font-mono">LABELCHECK</span>
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 font-semibold px-1.5 py-0.5 rounded border border-emerald-500/30">IN</span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono tracking-wide -mt-0.5">LM (PC) Rules 2011</p>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-1.5">
          <Link to="/scan" className={navLinkClass('/scan')}>
            <ScanLine className="w-4 h-4" />
            <span>Scan Label</span>
          </Link>
          <Link to="/history" className={navLinkClass('/history')}>
            <History className="w-4 h-4" />
            <span>Scan History</span>
          </Link>
          <Link to="/admin" className={navLinkClass('/admin')}>
            <BarChart3 className="w-4 h-4" />
            <span>Compliance Analytics</span>
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          {isAuthenticated && user ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 bg-slate-800/80 border border-slate-700/60 px-2.5 py-1 rounded-lg text-xs">
                <UserIcon className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-slate-200 font-medium max-w-[120px] truncate">{user.full_name || user.email}</span>
                <span className="bg-emerald-900/60 text-emerald-300 text-[10px] px-1.5 py-0.2 rounded font-mono uppercase border border-emerald-700/40">
                  {user.role}
                </span>
              </div>
              <button
                onClick={logout}
                title="Logout"
                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="flex items-center gap-1.5 text-xs font-medium text-slate-200 hover:text-white bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 px-3 py-1.5 rounded-lg transition-colors"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </Link>
              <Link
                to="/scan"
                className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-slate-950 bg-emerald-400 hover:bg-emerald-300 px-3 py-1.5 rounded-lg shadow-sm transition-colors"
              >
                <span>Instant Scan</span>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};