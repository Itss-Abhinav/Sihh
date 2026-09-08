import { apiClient } from './client';
import { AdminDashboardStats } from '../types';

export const adminApi = {
  async getDashboardMetrics(): Promise<AdminDashboardStats> {
    const res = await apiClient.get<AdminDashboardStats>('/api/admin/dashboard');
    return res.data;
  }
};