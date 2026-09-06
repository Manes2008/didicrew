import { create } from "zustand";
import { apiClient, RustDeskConfigData } from "@/lib/api-client";

interface RustDeskState {
  config: RustDeskConfigData | null;
  isLoading: boolean;
  isLoaded: boolean;
  error: string | null;

  fetchConfig: (force?: boolean) => Promise<RustDeskConfigData | null>;
  updateConfig: (data: RustDeskConfigData) => Promise<RustDeskConfigData>;
}

export const useRustDeskStore = create<RustDeskState>((set, get) => ({
  config: null,
  isLoading: false,
  isLoaded: false,
  error: null,

  fetchConfig: async (force = false) => {
    if (get().isLoaded && !force && get().config) {
      return get().config;
    }

    set({ isLoading: true, error: null });
    try {
      const config = await apiClient.getRustDeskConfig();
      set({ config, isLoading: false, isLoaded: true });
      return config;
    } catch (err: any) {
      set({ isLoading: false, isLoaded: true, error: err.message || "Khong the tai cau hinh RustDesk" });
      return null;
    }
  },

  updateConfig: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiClient.updateRustDeskConfig(data);
      set({ config: updated, isLoading: false, isLoaded: true });
      return updated;
    } catch (err: any) {
      set({ isLoading: false, error: err.message });
      throw err;
    }
  },
}));
