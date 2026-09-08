import { apiClient } from './client';
import { ScanSummaryItem, ScanDetailResponse } from '../types';

export const scansApi = {
  async createScan(formData: FormData): Promise<ScanDetailResponse> {
    const res = await apiClient.post<ScanDetailResponse>('/api/scans', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  async listScans(status?: string): Promise<ScanSummaryItem[]> {
    const params = status ? { status } : {};
    const res = await apiClient.get<ScanSummaryItem[]>('/api/scans', { params });
    return res.data;
  },

  async getScan(id: string): Promise<ScanDetailResponse> {
    const res = await apiClient.get<ScanDetailResponse>(`/api/scans/${id}`);
    return res.data;
  },

  async deleteScan(id: string): Promise<void> {
    await apiClient.delete(`/api/scans/${id}`);
  }
};