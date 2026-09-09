export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://127.0.0.1:8000/api/v1/ws";

// Wrapper fetch tu dong bo sung header ngrok-skip-browser-warning de bo qua trang canh bao cua Ngrok Free
const fetch = (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  const headers = new Headers(init?.headers);
  if (!headers.has("ngrok-skip-browser-warning")) {
    headers.set("ngrok-skip-browser-warning", "69420");
  }
  return globalThis.fetch(input, { ...init, headers });
};

export interface Channel {
  id: number;
  name: string;
  description?: string;
  goal: string;
  created_at: string;
  updated_at: string;
}

export interface VideoGeneratePayload {
  channel_id: number;
  idea: string;
  provider: string;
  model_name: string;
  video_engine: string;
  image_engine: string;
  aspect_ratio: string;
}

export interface SingleStageRunPayload {
  project_id?: number | null;
  channel_id: number;
  stage_name: string;
  idea: string;
  custom_content?: string;
  provider: string;
  model_name: string;
  video_engine: string;
  image_engine: string;
  aspect_ratio: string;
}

export interface TaskTriggerResult {
  task_id: string;
  project_id: number;
  status: string;
  message: string;
}

export interface ProjectStageItem {
  id: number;
  project_id: number;
  stage_name: string;
  result_content?: string | null;
  media_path?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectItem {
  id: number;
  channel_id: number;
  idea: string;
  provider: string;
  model_name: string;
  current_stage: string;
  status: string;
  created_at: string;
  updated_at: string;
  stages?: ProjectStageItem[];
}

export interface SystemConfigData {
  provider: string;
  model_name: string;
  video_engine: string;
  image_engine: string;
  has_openai_key: boolean;
  has_gemini_key: boolean;
  masked_openai_key?: string;
  masked_gemini_key?: string;
}

export interface CostLogItem {
  id: number;
  project_id: number;
  stage_name: string;
  sub_step_name: string;
  model_name?: string;
  provider?: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost_usd: number;
  elapsed_seconds: number;
  created_at: string;
}

export interface AnalyticsData {
  total_projects: number;
  completed_projects: number;
  total_tokens_used: number;
  total_cost_usd: number;
  cost_logs: CostLogItem[];
}

export interface AllowedIPItem {
  id: number;
  ip_address: string;
  label?: string;
  status: string;
  is_admin_ip: boolean;
  approved_at?: string;
  created_at: string;
}

export interface RustDeskConfigData {
  id_server: string;
  relay_server: string;
  api_server?: string;
  public_key?: string;
  is_connected: boolean;
}

export const apiClient = {
  // Auth
  async login(username: string, password: string): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Đăng nhập thất bại");
    }
    return res.json();
  },

  async register(username: string, password: string, device_label?: string): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, device_label }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Đăng ký thất bại");
    }
    return res.json();
  },

  // Channels
  async getChannels(): Promise<Channel[]> {
    const res = await fetch(`${API_BASE_URL}/channels`);
    if (!res.ok) throw new Error("Khong the lay danh sach kenh");
    return res.json();
  },

  async createChannel(data: { name: string; description?: string; goal: string }): Promise<Channel> {
    const res = await fetch(`${API_BASE_URL}/channels`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Loi khi tao kenh moi");
    }
    return res.json();
  },

  async updateChannel(id: number, data: { name: string; description?: string; goal: string }): Promise<Channel> {
    const res = await fetch(`${API_BASE_URL}/channels/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Loi khi cap nhat kenh");
    }
    return res.json();
  },

  async deleteChannel(id: number): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/channels/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Khong the xoa kenh");
  },

  // Production
  async triggerVideoGeneration(payload: VideoGeneratePayload): Promise<TaskTriggerResult> {
    const res = await fetch(`${API_BASE_URL}/production/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Loi khi khoi tao san xuat video");
    }
    return res.json();
  },

  async triggerSingleStage(payload: SingleStageRunPayload): Promise<TaskTriggerResult> {
    const res = await fetch(`${API_BASE_URL}/production/stage/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Loi khi chay stage don le");
    }
    return res.json();
  },

  async getChannelProjects(channelId: number): Promise<ProjectItem[]> {
    const res = await fetch(`${API_BASE_URL}/production/channels/${channelId}/projects`);
    if (!res.ok) throw new Error("Khong the lay danh sach du an cua kenh");
    return res.json();
  },

  async getProjectDetail(projectId: number): Promise<ProjectItem> {
    const res = await fetch(`${API_BASE_URL}/production/projects/${projectId}`);
    if (!res.ok) throw new Error("Khong the lay chi tiet du an");
    return res.json();
  },

  // System Config
  async getConfig(): Promise<SystemConfigData> {
    const res = await fetch(`${API_BASE_URL}/config`);
    if (!res.ok) throw new Error("Khong the lay cau hinh he thong");
    return res.json();
  },

  async updateConfig(data: Partial<SystemConfigData & { openai_api_key?: string; gemini_api_key?: string }>): Promise<SystemConfigData> {
    const res = await fetch(`${API_BASE_URL}/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Loi khi cap nhat cau hinh");
    return res.json();
  },

  async testApiKey(provider: string, apiKey?: string): Promise<{ provider: string; is_valid: boolean; status: string; message: string }> {
    const res = await fetch(`${API_BASE_URL}/config/test-key`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, api_key: apiKey }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Lỗi kiểm tra API Key");
    }
    return res.json();
  },

  // Analytics
  async getAnalytics(): Promise<AnalyticsData> {
    const res = await fetch(`${API_BASE_URL}/analytics/summary`);
    if (!res.ok) throw new Error("Khong the lay du lieu analytics");
    return res.json();
  },

  // IP Manager
  async getIPList(): Promise<AllowedIPItem[]> {
    const res = await fetch(`${API_BASE_URL}/ip-manager`);
    if (!res.ok) throw new Error("Khong the lay danh sach IP");
    return res.json();
  },

  async updateIP(id: number, status: string, is_admin_ip?: boolean): Promise<AllowedIPItem> {
    const res = await fetch(`${API_BASE_URL}/ip-manager/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, is_admin_ip }),
    });
    if (!res.ok) throw new Error("Khong the cap nhat trang thai IP");
    return res.json();
  },

  async deleteIP(id: number): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/ip-manager/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Khong the xoa IP");
  },

  // RustDesk
  async getRustDeskConfig(): Promise<RustDeskConfigData> {
    const res = await fetch(`${API_BASE_URL}/rustdesk`);
    if (!res.ok) throw new Error("Khong the lay cau hinh RustDesk");
    return res.json();
  },

  async updateRustDeskConfig(data: RustDeskConfigData): Promise<RustDeskConfigData> {
    const res = await fetch(`${API_BASE_URL}/rustdesk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Khong the cap nhat RustDesk");
    return res.json();
  },
};
