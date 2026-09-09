import { create } from "zustand";
import { persist } from "zustand/middleware";
import { apiClient } from "@/lib/api-client";

export interface AuthUser {
  username: string;
  role: string;
  is_admin_ip: boolean;
  client_ip: string;
}

export const AUTH_STORAGE_VERSION = 2;
export const SESSION_TTL_MS = 24 * 60 * 60 * 1000; // 24 gio

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  loginAt: number | null;
  storageVersion: number;

  login: (username: string, password: string) => Promise<AuthUser>;
  register: (username: string, password: string, device_label?: string) => Promise<AuthUser>;
  logout: () => void;
  checkSessionValidity: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      loginAt: null,
      storageVersion: AUTH_STORAGE_VERSION,

      login: async (username, password) => {
        const data = await apiClient.login(username, password);
        const user: AuthUser = {
          username: data.username,
          role: data.role,
          is_admin_ip: data.is_admin_ip,
          client_ip: data.client_ip,
        };
        set({
          user,
          isAuthenticated: true,
          loginAt: Date.now(),
          storageVersion: AUTH_STORAGE_VERSION,
        });
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
        set({
          user,
          isAuthenticated: true,
          loginAt: Date.now(),
          storageVersion: AUTH_STORAGE_VERSION,
        });
        localStorage.setItem("user", JSON.stringify(user));
        return user;
      },

      logout: () => {
        set({ user: null, isAuthenticated: false, loginAt: null });
        localStorage.removeItem("user");
      },

      checkSessionValidity: () => {
        const state = get();
        if (!state.isAuthenticated) return false;

        // 1. Kiem tra lech version deploy
        if (state.storageVersion !== AUTH_STORAGE_VERSION) {
          get().logout();
          return false;
        }

        // 2. Kiem tra het han phien 24 gio
        if (!state.loginAt || Date.now() - state.loginAt > SESSION_TTL_MS) {
          get().logout();
          return false;
        }

        return true;
      },
    }),
    {
      name: "videocrew_auth",
      version: AUTH_STORAGE_VERSION,
      migrate: (persistedState: any, version: number) => {
        // Tu dong reset sach se ve trang thai chua dang nhap neu phien cu khac version
        if (version !== AUTH_STORAGE_VERSION) {
          return {
            user: null,
            isAuthenticated: false,
            loginAt: null,
            storageVersion: AUTH_STORAGE_VERSION,
          };
        }
        return persistedState as any;
      },
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        loginAt: state.loginAt,
        storageVersion: state.storageVersion,
      }),
    }
  )
);
