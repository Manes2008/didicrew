"use client";

import { useEffect } from "react";
import { useChannelStore } from "@/stores/useChannelStore";
import { useConfigStore } from "@/stores/useConfigStore";

export function AppInitializer() {
  const fetchChannels = useChannelStore((state) => state.fetchChannels);
  const fetchConfig = useConfigStore((state) => state.fetchConfig);

  useEffect(() => {
    // Pre-fetch global data in background when app mounts
    fetchChannels().catch(console.error);
    fetchConfig().catch(console.error);
  }, [fetchChannels, fetchConfig]);

  return null;
}
