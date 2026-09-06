import { create } from "zustand";
import { persist } from "zustand/middleware";
import { apiClient } from "@/lib/api-client";

export interface AuthUser {
  username: string;
  role: string;
  is_admin_ip: boolean;
  client_ip: string;
}

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;

  login: (username: string, password: string) => Promise<AuthUser>;
  register: (username: string, password: string, device_label?: string) => Promise<AuthUser>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,

      login: async (username, password) => {
        const data = await apiClient.login(username, password);
        const user: AuthUser = {
          username: data.username,
          role: data.role,
          is_admin_ip: data.is_admin_ip,
          client_ip: data.client_ip,
        };
        set({ user, isAuthenticated: true });
        // Giu tuong thich voi AuthGuard cu (localStorage "user")
        localStorage.setItem("user", JSON.stringify(user));
        return user;
      },

      register: async (username, password, device_label) => {
        const data = await apiClient.register(username, password, device_label);
        const user: AuthUser = {
          username: data.username,
          role: data.role,
          is_admin_ip: data.is_admin_ip,
          client_ip: data.client_ip,
        };
        set({ user, isAuthenticated: true });
        localStorage.setItem("user", JSON.stringify(user));
        return user;
      },

      logout: () => {
        set({ user: null, isAuthenticated: false });
        localStorage.removeItem("user");
      },
    }),
    {
      name: "videocrew_auth",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
