import { apiClient } from './client';
import { User } from '../types';

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const authApi = {
  async register(data: { email: string; password: string; full_name?: string; role?: string }): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/api/auth/register', data);
    return res.data;
  },

  async login(data: { email: string; password: string }): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/api/auth/login', data);
    return res.data;
  },

  async getMe(): Promise<User> {
    const res = await apiClient.get<User>('/api/auth/me');
    return res.data;
  }
};