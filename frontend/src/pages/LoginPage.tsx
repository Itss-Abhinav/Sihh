import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, LogIn, Lock, Mail, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide email and password.');
      return;
    }
    setError(null);
    setIsLoading(true);
    try {
      await login(email, password);
      navigate('/scan');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail: string, demoPwd: string) => {
    setEmail(demoEmail);
    setPassword(demoPwd);
  };

  return (
    <div className="max-w-md mx-auto px-4 py-12 space-y-6">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center mx-auto shadow-lg shadow-emerald-950/60">
          <ShieldCheck className="w-7 h-7 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Sign In to LabelCheck</h1>
        <p className="text-xs text-slate-400">Access your historical screening archive and administrative reports</p>
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-5">
        {error && (
          <div className="p-3 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="officer@domain.in"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold py-2.5 rounded-xl text-xs flex items-center justify-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50"
          >
            <LogIn className="w-4 h-4" />
            <span>{isLoading ? 'Authenticating...' : 'Sign In'}</span>
          </button>
        </form>

        <div className="pt-4 border-t border-slate-800 space-y-2">
          <span className="text-[11px] font-semibold text-slate-400 block">Autofill Demo Test Roles:</span>
          <div className="grid grid-cols-2 gap-1.5">
            <button
              type="button"
              onClick={() => handleQuickLogin('admin@labelcheck.in', 'Admin@12345')}
              className="text-[11px] text-left bg-slate-900 hover:bg-slate-800 border border-slate-800 p-2 rounded-lg text-slate-300"
            >
              <span className="font-semibold text-emerald-400 block">Admin Role</span>
              <span className="text-[10px] text-slate-400 font-mono">admin@labelcheck.in</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('inspector@lm.gov.in', 'Inspector@12345')}
              className="text-[11px] text-left bg-slate-900 hover:bg-slate-800 border border-slate-800 p-2 rounded-lg text-slate-300"
            >
              <span className="font-semibold text-sky-400 block">Inspector Role</span>
              <span className="text-[10px] text-slate-400 font-mono">inspector@lm.gov.in</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('retailer@store.in', 'Retailer@12345')}
              className="text-[11px] text-left bg-slate-900 hover:bg-slate-800 border border-slate-800 p-2 rounded-lg text-slate-300"
            >
              <span className="font-semibold text-amber-400 block">Retailer Role</span>
              <span className="text-[10px] text-slate-400 font-mono">retailer@store.in</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('demo@labelcheck.in', 'Demo@12345')}
              className="text-[11px] text-left bg-slate-900 hover:bg-slate-800 border border-slate-800 p-2 rounded-lg text-slate-300"
            >
              <span className="font-semibold text-teal-400 block">Consumer Role</span>
              <span className="text-[10px] text-slate-400 font-mono">demo@labelcheck.in</span>
            </button>
          </div>
        </div>

        <div className="text-center pt-2">
          <p className="text-xs text-slate-400">
            Don't have an account?{' '}
            <Link to="/register" className="text-emerald-400 hover:text-emerald-300 font-semibold underline">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};