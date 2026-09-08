import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Role } from '../types';

interface Props {
  children: React.ReactNode;
  allowedRoles?: Role[];
}

export const ProtectedRoute: React.FC<Props> = ({ children, allowedRoles }) => {
  const { user, isLoading, isAuthenticated } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-400"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return (
      <div className="max-w-md mx-auto my-16 p-6 glass-panel rounded-xl text-center border border-rose-800/40">
        <h3 className="text-base font-bold text-rose-300">Access Restricted</h3>
        <p className="text-xs text-slate-300 mt-2">
          This section requires one of the following roles: {allowedRoles.join(', ')}. Your current role is {user.role}.
        </p>
      </div>
    );
  }

  return <>{children}</>;
};