import { create } from "zustand";
import { persist } from "zustand/middleware";
import { apiClient, SingleStageRunPayload, ProjectItem, WS_BASE_URL } from "@/lib/api-client";
import { FileText, Image as ImageIcon, Mic, Video } from "lucide-react";

export interface StageMeta {
  key: string;
  name: string;
  shortTitle: string;
  description: string;
  icon: any;
}

export const STAGES_LIST: StageMeta[] = [
  { key: "brief", name: "1. Định hướng Sáng tạo (Brief)", shortTitle: "Brief", description: "Xác định mục tiêu, khán giả, thông điệp cốt lõi và phong cách", icon: FileText },
  { key: "script", name: "2. Biên soạn Kịch bản (Script)", shortTitle: "Kịch bản", description: "Bảng phân cảnh chi tiết, thời lượng từng cảnh và lời thoại", icon: FileText },
  { key: "image", name: "3. Tạo Visual & Ảnh AI (Images)", shortTitle: "Visual & Ảnh", description: "Tối ưu hóa visual prompt và sinh ảnh phân cảnh AI", icon: ImageIcon },
  { key: "voice", name: "4. Tổng hợp Giọng đọc (Voice)", shortTitle: "Giọng đọc", description: "Tạo file thuyết minh AI Neural Voice khớp thời lượng", icon: Mic },
  { key: "video", name: "5. Dựng & Xuất Video (Render)", shortTitle: "Xuất Video", description: "Ghép nối video, khớp âm thanh, sub và hiệu ứng", icon: Video },
];

let globalWs: WebSocket | null = null;

interface ProductionState {
  // Form Configuration (Persisted)
  idea: string;
  provider: string;
  modelName: string;
  videoEngine: string;
  imageEngine: string;
  aspectRatio: string;

  // Channel Projects
  channelProjects: ProjectItem[];
  isLoadingProjects: boolean;

  // Workspace & Stepper State
  isWorkspaceMode: boolean;
  currentStepIndex: number;
  projectId: number | null;
  taskId: string | null;
  isProcessing: boolean;
  progressPercent: number;
  logs: string[];

  // Stage Data & Approvals
  stageContents: Record<string, string>;
  stageApproval: Record<string, "pending" | "running" | "waiting_approval" | "approved" | "error">;
  mediaOutputs: Record<string, string[]>;

  // Actions
  setIdea: (idea: string) => void;
  setProvider: (provider: string) => void;
  setModelName: (modelName: string) => void;
  setVideoEngine: (videoEngine: string) => void;
  setImageEngine: (imageEngine: string) => void;
  setAspectRatio: (aspectRatio: string) => void;

  setCurrentStepIndex: (index: number) => void;
  setIsWorkspaceMode: (mode: boolean) => void;
  updateStageContent: (stageKey: string, content: string) => void;

  fetchChannelProjects: (channelId: number) => Promise<void>;
  loadExistingProject: (projectId: number) => Promise<void>;
  saveEngineConfigToDatabase: () => Promise<void>;

  startStepByStepWorkspace: (channelId: number) => Promise<void>;
  runStageStep: (stageIndex: number, channelId: number) => Promise<void>;
  approveAndNext: (channelId: number) => Promise<void>;
  regenerateStage: (stageIndex: number, channelId: number) => Promise<void>;
  resetProduction: () => void;
}

const initialApproval: Record<string, "pending" | "running" | "waiting_approval" | "approved" | "error"> = {
  brief: "pending",
  script: "pending",
  image: "pending",
  voice: "pending",
  video: "pending",
};

export const useProductionStore = create<ProductionState>()(
  persist(
    (set, get) => ({
      idea: "",
      provider: "Gemini",
      modelName: "gemini-3.6-flash",
      videoEngine: "hunyuan",
      imageEngine: "gemini",
      aspectRatio: "9:16",

      channelProjects: [],
      isLoadingProjects: false,

      isWorkspaceMode: false,
      currentStepIndex: 0,
      projectId: null,
      taskId: null,
      isProcessing: false,
      progressPercent: 0,
      logs: [],

      stageContents: {
        brief: "",
        script: "",
        image: "",
        voice: "",
        video: "",
      },
      stageApproval: initialApproval,
      mediaOutputs: {
        image: [],
        voice: [],
        video: [],
      },

      setIdea: (idea) => set({ idea }),
      setProvider: (provider) => {
        if (provider === "Gemini") {
          set({ provider, modelName: "gemini-3.6-flash", imageEngine: "gemini" });
        } else {
          set({ provider, modelName: "gpt-4o-mini", imageEngine: "dalle" });
        }
      },
      setModelName: (modelName) => set({ modelName }),
      setVideoEngine: (videoEngine) => set({ videoEngine }),
      setImageEngine: (imageEngine) => set({ imageEngine }),
      setAspectRatio: (aspectRatio) => set({ aspectRatio }),

      setCurrentStepIndex: (currentStepIndex) => set({ currentStepIndex }),
      setIsWorkspaceMode: (isWorkspaceMode) => set({ isWorkspaceMode }),
      updateStageContent: (stageKey, content) =>
        set((state) => ({
          stageContents: { ...state.stageContents, [stageKey]: content },
        })),

      saveEngineConfigToDatabase: async () => {
        const { provider, modelName, videoEngine, imageEngine } = get();
        try {
          await apiClient.updateConfig({
            provider,
            model_name: modelName,
            video_engine: videoEngine,
            image_engine: imageEngine,
          });
        } catch (err) {
          console.error("Loi luu config vao DB:", err);
        }
      },

      fetchChannelProjects: async (channelId: number) => {
        if (!channelId) return;
        set({ isLoadingProjects: true });
        try {
          const projs = await apiClient.getChannelProjects(channelId);
          set({ channelProjects: projs, isLoadingProjects: false });
        } catch (err) {
          set({ isLoadingProjects: false });
        }
      },

      loadExistingProject: async (projectId: number) => {
        if (!projectId) return;
        set({ isProcessing: true, logs: [`[INFO] Đang tải chi tiết dự án #${projectId}...`] });
        try {
          const proj = await apiClient.getProjectDetail(projectId);
          
          const newContents = { brief: "", script: "", image: "", voice: "", video: "" };
          const newApproval: Record<string, any> = { ...initialApproval };
          const newMedia: Record<string, string[]> = { image: [], voice: [], video: [] };
          let lastCompletedIndex = 0;

          if (proj.stages && proj.stages.length > 0) {
            proj.stages.forEach((st) => {
              if (st.result_content) {
                newContents[st.stage_name as keyof typeof newContents] = st.result_content;
                newApproval[st.stage_name] = "approved";

                if (st.stage_name === "image") {
                  const matches = st.result_content.match(/generated_images[/\\][^\s"']+\.(?:png|jpg|jpeg|webp)/gi) || [];
                  newMedia.image = Array.from(new Set(matches));
                } else if (st.stage_name === "voice") {
                  const matches = st.result_content.match(/generated_audio[/\\][^\s"']+\.(?:mp3|wav|ogg)/gi) || [];
                  newMedia.voice = Array.from(new Set(matches));
                } else if (st.stage_name === "video") {
                  const matches = st.result_content.match(/(?:generated_videos|exports)[/\\][^\s"']+\.(?:mp4|mov|webm)/gi) || [];
                  newMedia.video = Array.from(new Set(matches));
                }

                const idx = STAGES_LIST.findIndex((s) => s.key === st.stage_name);
                if (idx >= lastCompletedIndex) {
                  lastCompletedIndex = idx;
                }
              }
            });
          }

          set({
            projectId: proj.id,
            idea: proj.idea,
            provider: proj.provider || "Gemini",
            modelName: proj.model_name || "gemini-3.6-flash",
            isWorkspaceMode: true,
            currentStepIndex: lastCompletedIndex,
            stageContents: newContents,
            stageApproval: newApproval,
            mediaOutputs: newMedia,
            isProcessing: false,
            logs: [`[SUCCESS] Đã nạp thành công dự án #${proj.id} vào Studio Workspace.`],
          });
        } catch (err: any) {
          set({
            isProcessing: false,
            logs: [...get().logs, `[ERROR] Không thể tải dự án: ${err.message}`],
          });
        }
      },

      startStepByStepWorkspace: async (channelId: number) => {
        const { idea } = get();
        if (!channelId) throw new Error("Vui long chon kenh hop le");
        if (!idea.trim()) throw new Error("Vui long nhap y tuong video");

        // Luu cau hinh vao DB
        get().saveEngineConfigToDatabase();

        set({
          isWorkspaceMode: true,
          currentStepIndex: 0,
          projectId: null,
          taskId: null,
          isProcessing: false,
          progressPercent: 10,
          logs: ["[INFO] Chuyen sang che do Step-by-Step Approval Workspace."],
          stageApproval: { ...initialApproval, brief: "running" },
          stageContents: { brief: "", script: "", image: "", voice: "", video: "" },
          mediaOutputs: { image: [], voice: [], video: [] },
        });

        await get().runStageStep(0, channelId);
        get().fetchChannelProjects(channelId);
      },

      runStageStep: async (stageIndex: number, channelId: number) => {
        const stageMeta = STAGES_LIST[stageIndex];
        if (!stageMeta) return;

        const { idea, provider, modelName, videoEngine, imageEngine, aspectRatio, projectId, stageContents } = get();

        if (globalWs) {
          try {
            globalWs.close();
          } catch (e) {}
          globalWs = null;
        }

        set((state) => ({
          isProcessing: true,
          currentStepIndex: stageIndex,
          stageApproval: { ...state.stageApproval, [stageMeta.key]: "running" },
          logs: [...state.logs, `[START] Bat dau chay AI cho buoc: ${stageMeta.name}`],
        }));

        try {
          let customContent = "";
          if (stageIndex > 0) {
            const prevKey = STAGES_LIST[stageIndex - 1].key;
            customContent = stageContents[prevKey] || "";
          }

          const payload: SingleStageRunPayload = {
            project_id: projectId,
            channel_id: channelId,
            stage_name: stageMeta.key,
            idea,
            custom_content: customContent,
            provider,
            model_name: modelName,
            video_engine: videoEngine,
            image_engine: imageEngine,
            aspect_ratio: aspectRatio,
          };

          const res = await apiClient.triggerSingleStage(payload);
          set({
            projectId: res.project_id,
            taskId: res.task_id,
            logs: [...get().logs, `[SUCCESS] Task ID: ${res.task_id}. Dang ket noi WebSocket Stream...`],
          });

          const wsUrl = `${WS_BASE_URL}/tasks/${res.task_id}`;
          const ws = new WebSocket(wsUrl);
          globalWs = ws;

          ws.onmessage = (event) => {
            try {
              const msg = JSON.parse(event.data);
              if (msg.message) {
                set((state) => ({ logs: [...state.logs, `[STAGE] ${msg.message}`] }));
              }

              if (msg.event === "stage_complete" && msg.stage === stageMeta.key) {
                const rawContent = msg.result_content || msg.result_preview || "";
                
                const updatedMedia = { ...get().mediaOutputs };
                if (msg.stage === "image") {
                  const matches = rawContent.match(/generated_images[/\\][^\s"']+\.(?:png|jpg|jpeg|webp)/gi) || [];
                  updatedMedia.image = Array.from(new Set(matches));
                } else if (msg.stage === "voice") {
                  const matches = rawContent.match(/generated_audio[/\\][^\s"']+\.(?:mp3|wav|ogg)/gi) || [];
                  updatedMedia.voice = Array.from(new Set(matches));
                } else if (msg.stage === "video") {
                  const matches = rawContent.match(/(?:generated_videos|exports)[/\\][^\s"']+\.(?:mp4|mov|webm)/gi) || [];
                  updatedMedia.video = Array.from(new Set(matches));
                }

                set((state) => ({
                  isProcessing: false,
                  stageContents: { ...state.stageContents, [stageMeta.key]: rawContent },
                  stageApproval: { ...state.stageApproval, [stageMeta.key]: "waiting_approval" },
                  mediaOutputs: updatedMedia,
                  logs: [...state.logs, `[WAIT] Giai doan ${stageMeta.name} da xong va dang cho ban DUYET de tiep tuc!`],
                }));

                ws.close();
                globalWs = null;
                get().fetchChannelProjects(channelId);
              } else if (msg.event === "error") {
                set((state) => ({
                  isProcessing: false,
                  stageApproval: { ...state.stageApproval, [stageMeta.key]: "error" },
                  logs: [...state.logs, `[ERROR] ${msg.message}`],
                }));
                ws.close();
                globalWs = null;
              }
            } catch (err) {
              console.error("Loi parse WS message:", err);
            }
          };

          ws.onerror = () => {
            set((state) => ({
              logs: [...state.logs, `[WARN] WebSocket stream error.`],
            }));
          };
        } catch (err: any) {
          set((state) => ({
            isProcessing: false,
            stageApproval: { ...state.stageApproval, [stageMeta.key]: "error" },
            logs: [...state.logs, `[ERROR] ${err.message}`],
          }));
          throw err;
        }
      },

      approveAndNext: async (channelId: number) => {
        const { currentStepIndex } = get();
        const curMeta = STAGES_LIST[currentStepIndex];
        if (!curMeta) return;

        set((state) => ({
          stageApproval: { ...state.stageApproval, [curMeta.key]: "approved" },
          logs: [...state.logs, `[APPROVED] Ban da phe duyet ket qua cua buoc: ${curMeta.name}`],
        }));

        if (currentStepIndex < STAGES_LIST.length - 1) {
          const nextIndex = currentStepIndex + 1;
          set({ currentStepIndex: nextIndex });
          await get().runStageStep(nextIndex, channelId);
        } else {
          set((state) => ({
            logs: [...state.logs, `[COMPLETED] Toan bo 5 giai doan da hoan thanh va duoc phe duyet 100%!`],
          }));
        }
      },

      regenerateStage: async (stageIndex: number, channelId: number) => {
        await get().runStageStep(stageIndex, channelId);
      },

      resetProduction: () => {
        if (globalWs) {
          try {
            globalWs.close();
          } catch (e) {}
          globalWs = null;
        }
        set({
          isWorkspaceMode: false,
          currentStepIndex: 0,
          projectId: null,
          taskId: null,
          isProcessing: false,
          progressPercent: 0,
          logs: [],
          stageContents: { brief: "", script: "", image: "", voice: "", video: "" },
          stageApproval: initialApproval,
          mediaOutputs: { image: [], voice: [], video: [] },
        });
      },
    }),
    {
      name: "videocrew_engine_config",
      partialize: (state) => ({
        provider: state.provider,
        modelName: state.modelName,
        videoEngine: state.videoEngine,
        imageEngine: state.imageEngine,
        aspectRatio: state.aspectRatio,
      }),
    }
  )
);
