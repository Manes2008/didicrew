import { create } from "zustand";
import { apiClient, AnalyticsData } from "@/lib/api-client";

interface AnalyticsState {
  analytics: AnalyticsData | null;
  isLoading: boolean;
  isLoaded: boolean;
  error: string | null;

  fetchAnalytics: (force?: boolean) => Promise<AnalyticsData | null>;
}

export const useAnalyticsStore = create<AnalyticsState>((set, get) => ({
  analytics: null,
  isLoading: false,
  isLoaded: false,
  error: null,

  fetchAnalytics: async (force = false) => {
    if (get().isLoaded && !force && get().analytics) {
      return get().analytics;
    }

    set({ isLoading: true, error: null });
    try {
      const analytics = await apiClient.getAnalytics();
      set({ analytics, isLoading: false, isLoaded: true });
      return analytics;
    } catch (err: any) {
      const errorMsg = err.message || "Khong the tai du lieu analytics";
      set({ isLoading: false, isLoaded: true, error: errorMsg });
      return null;
    }
  },
}));
