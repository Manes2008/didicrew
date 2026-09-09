import { create } from "zustand";
import { apiClient, Channel } from "@/lib/api-client";

interface ChannelState {
  channels: Channel[];
  selectedChannelId: number | null;
  isLoading: boolean;
  isLoaded: boolean;
  error: string | null;

  fetchChannels: (force?: boolean) => Promise<Channel[]>;
  setSelectedChannelId: (id: number | null) => void;
  createChannel: (data: { name: string; description?: string; goal: string }) => Promise<Channel>;
  updateChannel: (id: number, data: { name: string; description?: string; goal: string }) => Promise<Channel>;
  deleteChannel: (id: number) => Promise<void>;
}

export const useChannelStore = create<ChannelState>((set, get) => ({
  channels: [],
  selectedChannelId: null,
  isLoading: false,
  isLoaded: false,
  error: null,

  fetchChannels: async (force = false) => {
    if (get().isLoaded && !force && get().channels.length > 0) {
      return get().channels;
    }

    set({ isLoading: true, error: null });
    try {
      const channels = await apiClient.getChannels();
      const currentSelected = get().selectedChannelId;
      const validSelected = channels.some((c) => c.id === currentSelected)
        ? currentSelected
        : channels.length > 0
        ? channels[0].id
        : null;

      set({
        channels,
        selectedChannelId: validSelected,
        isLoading: false,
        isLoaded: true,
      });
      return channels;
    } catch (err: any) {
      const errorMsg = err.message || "Khong the tai danh sach kenh";
      set({ isLoading: false, isLoaded: true, error: errorMsg });
      return [];
    }
  },

  setSelectedChannelId: (id) => set({ selectedChannelId: id }),

  createChannel: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const newChannel = await apiClient.createChannel(data);
      const updatedChannels = [...get().channels, newChannel];
      set({
        channels: updatedChannels,
        selectedChannelId: get().selectedChannelId ?? newChannel.id,
        isLoading: false,
      });
      return newChannel;
    } catch (err: any) {
      set({ isLoading: false, error: err.message });
      throw err;
    }
  },

  updateChannel: async (id, data) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiClient.updateChannel(id, data);
      const updatedChannels = get().channels.map((c) => (c.id === id ? updated : c));
      set({
        channels: updatedChannels,
        isLoading: false,
      });
      return updated;
    } catch (err: any) {
      set({ isLoading: false, error: err.message });
      throw err;
    }
  },

  deleteChannel: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.deleteChannel(id);
      const updatedChannels = get().channels.filter((c) => c.id !== id);
      const newSelected =
        get().selectedChannelId === id
          ? updatedChannels.length > 0
            ? updatedChannels[0].id
            : null
          : get().selectedChannelId;

      set({
        channels: updatedChannels,
        selectedChannelId: newSelected,
        isLoading: false,
      });
    } catch (err: any) {
      set({ isLoading: false, error: err.message });
      throw err;
    }
  },
}));
