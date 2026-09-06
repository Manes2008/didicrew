import { create } from "zustand";
import { apiClient, AllowedIPItem } from "@/lib/api-client";

interface IPManagerState {
  ipList: AllowedIPItem[];
  isLoading: boolean;
  isLoaded: boolean;
  error: string | null;

  fetchIPList: (force?: boolean) => Promise<void>;
  updateIP: (id: number, status: string, is_admin_ip?: boolean) => Promise<AllowedIPItem>;
  deleteIP: (id: number) => Promise<void>;
}

export const useIPManagerStore = create<IPManagerState>((set, get) => ({
  ipList: [],
  isLoading: false,
  isLoaded: false,
  error: null,

  fetchIPList: async (force = false) => {
    if (get().isLoaded && !force && get().ipList.length > 0) return;

    set({ isLoading: true, error: null });
    try {
      const ipList = await apiClient.getIPList();
      set({ ipList, isLoading: false, isLoaded: true });
    } catch (err: any) {
      set({ isLoading: false, isLoaded: true, error: err.message || "Khong the tai danh sach IP" });
    }
  },

  updateIP: async (id, status, is_admin_ip) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiClient.updateIP(id, status, is_admin_ip);
      const updatedList = get().ipList.map((ip) => (ip.id === id ? updated : ip));
      set({ ipList: updatedList, isLoading: false });
      return updated;
    } catch (err: any) {
      set({ isLoading: false, error: err.message });
      throw err;
    }
  },

  deleteIP: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.deleteIP(id);
      const updatedList = get().ipList.filter((ip) => ip.id !== id);
      set({ ipList: updatedList, isLoading: false });
    } catch (err: any) {
      set({ isLoading: false, error: err.message });
      throw err;
    }
  },
}));
