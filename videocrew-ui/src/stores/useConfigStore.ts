import { create } from "zustand";
import { apiClient, SystemConfigData } from "@/lib/api-client";

interface ConfigState {
  config: SystemConfigData | null;
  isLoading: boolean;
  isLoaded: boolean;
  error: string | null;

  fetchConfig: (force?: boolean) => Promise<SystemConfigData | null>;
  updateConfig: (
    data: Partial<SystemConfigData & { openai_api_key?: string; gemini_api_key?: string }>
  ) => Promise<SystemConfigData>;
}

export const useConfigStore = create<ConfigState>((set, get) => ({
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
      const config = await apiClient.getConfig();
      set({ config, isLoading: false, isLoaded: true });
      return config;
    } catch (err: any) {
      const errorMsg = err.message || "Khong the tai cau hinh he thong";
      set({ isLoading: false, isLoaded: true, error: errorMsg });
      return null;
    }
  },

  updateConfig: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiClient.updateConfig(data);
      set({ config: updated, isLoading: false, isLoaded: true });
      return updated;
    } catch (err: any) {
      set({ isLoading: false, error: err.message });
      throw err;
    }
  },
}));
