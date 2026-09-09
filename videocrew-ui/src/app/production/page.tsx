"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useChannelStore } from "@/stores/useChannelStore";
import { useProductionStore, STAGES_LIST } from "@/stores/useProductionStore";
import { 
  Play, 
  Sparkles, 
  Terminal, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  Film, 
  FileText, 
  Image as ImageIcon, 
  Mic, 
  Video, 
  Smartphone, 
  Monitor, 
  Layers,
  Wand2,
  PlusCircle,
  Maximize2,
  Copy,
  Check,
  Download,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  ArrowRight,
  ShieldCheck,
  Edit3,
  Volume2,
  FolderKanban,
  ExternalLink,
  Plus
} from "lucide-react";

export default function ProductionPage() {
  const { 
    channels, 
    selectedChannelId, 
    setSelectedChannelId, 
    isLoading: isChannelLoading, 
    isLoaded: isChannelLoaded, 
    fetchChannels 
  } = useChannelStore();

  const {
    idea,
    setIdea,
    provider,
    setProvider,
    modelName,
    setModelName,
    videoEngine,
    setVideoEngine,
    imageEngine,
    setImageEngine,
    aspectRatio,
    setAspectRatio,

    channelProjects,
    isLoadingProjects,
    fetchChannelProjects,
    loadExistingProject,

    isWorkspaceMode,
    currentStepIndex,
    projectId,
    isProcessing,
    logs,
    stageContents,
    stageApproval,
    mediaOutputs,

    setCurrentStepIndex,
    updateStageContent,
    startStepByStepWorkspace,
    runStageStep,
    approveAndNext,
    regenerateStage,
    resetProduction,
    saveEngineConfigToDatabase,
  } = useProductionStore();

  const [copied, setCopied] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [showProjectHistory, setShowProjectHistory] = useState(false);
  const [selectedImageModal, setSelectedImageModal] = useState<string | null>(null);
  const [savedFeedback, setSavedFeedback] = useState(false);

  const handleSaveDefaultConfig = async () => {
    await saveEngineConfigToDatabase();
    setSavedFeedback(true);
    setTimeout(() => setSavedFeedback(false), 2500);
  };

  useEffect(() => {
    if (!isChannelLoaded) {
      fetchChannels();
    }
  }, [isChannelLoaded, fetchChannels]);

  useEffect(() => {
    if (channels.length > 0 && (!selectedChannelId || !channels.some((c) => c.id === selectedChannelId))) {
      setSelectedChannelId(channels[0].id);
    }
  }, [channels, selectedChannelId, setSelectedChannelId]);

  useEffect(() => {
    if (selectedChannelId) {
      fetchChannelProjects(selectedChannelId);
    }
  }, [selectedChannelId, fetchChannelProjects]);

  const quickPromptTemplates = [
    "5 mẹo làm chủ ChatGPT & AI trong công việc năm 2026",
    "Bí mật tài chính: Vì sao người giàu càng giàu?",
    "Top 3 công cụ AI đỉnh cao giúp tăng gấp đôi hiệu suất",
    "Câu chuyện truyền cảm hứng về hành trình khởi nghiệp công nghệ",
  ];

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleStartProduction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedChannelId || channels.length === 0) {
      alert("Vui lòng tạo ít nhất 1 Kênh trước khi bắt đầu sản xuất!");
      return;
    }
    if (!idea.trim()) {
      alert("Vui lòng nhập Ý tưởng video!");
      return;
    }
    try {
      await startStepByStepWorkspace(selectedChannelId);
    } catch (err: any) {
      console.error(err);
    }
  };

  const currentStageMeta = STAGES_LIST[currentStepIndex] || STAGES_LIST[0];
  const currentContent = stageContents[currentStageMeta.key] || "";
  const currentStatus = stageApproval[currentStageMeta.key] || "pending";
  const selectedChannel = channels.find((c) => c.id === selectedChannelId);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Bar: Channel & Project Selector */}
      <div className="glass-panel p-4 rounded-2xl border border-[var(--vc-border)] bg-zinc-950/80 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* Channel Select */}
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold text-zinc-400 block tracking-wider">
                Kênh Phân Phối
              </span>
              {isChannelLoading && !isChannelLoaded ? (
                <div className="h-8 w-44 bg-zinc-800 rounded-xl animate-pulse" />
              ) : channels.length === 0 ? (
                <Link
                  href="/channels"
                  className="px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold hover:bg-amber-500/20 transition inline-flex items-center gap-1.5"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  Tạo Kênh Mới
                </Link>
              ) : (
                <select
                  value={selectedChannelId || channels[0]?.id || ""}
                  onChange={(e) => {
                    const newId = Number(e.target.value);
                    setSelectedChannelId(newId);
                    resetProduction();
                  }}
                  className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-700/80 text-xs font-bold text-white focus:border-amber-500 focus:ring-1 focus:ring-amber-500 outline-none cursor-pointer hover:border-zinc-600 transition min-w-[190px]"
                >
                  {channels.map((c) => (
                    <option key={c.id} value={c.id} className="bg-zinc-900 text-white font-medium">
                      {c.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          <div className="h-8 w-px bg-zinc-800 hidden md:block" />

          {/* Project Select for this Channel */}
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-orange-500/10 text-orange-400 border border-orange-500/20 flex items-center justify-center">
              <FolderKanban className="w-4 h-4" />
            </div>
            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold text-zinc-400 block tracking-wider">
                Dự Án Của Kênh
              </span>
              <select
                value={projectId || ""}
                onChange={(e) => {
                  const val = e.target.value;
                  if (val === "" || val === "new") {
                    resetProduction();
                  } else {
                    loadExistingProject(Number(val));
                  }
                }}
                className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-700/80 text-xs font-bold text-zinc-200 focus:border-amber-500 focus:ring-1 focus:ring-amber-500 outline-none cursor-pointer hover:border-zinc-600 transition min-w-[220px] max-w-[320px] truncate"
              >
                <option value="" className="bg-zinc-900 text-amber-400 font-bold">
                  + Tạo Dự Án Mới...
                </option>
                {channelProjects.map((p) => (
                  <option key={p.id} value={p.id} className="bg-zinc-900 text-white font-medium">
                    #{p.id} - [{p.current_stage || "brief"}] {p.idea.slice(0, 35)}...
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Quick Tools */}
        <div className="flex items-center gap-2">
          {channelProjects.length > 0 && (
            <button
              onClick={() => setShowProjectHistory(!showProjectHistory)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-zinc-900 border border-[var(--vc-border)] text-zinc-300 hover:text-white hover:border-zinc-700 transition"
            >
              <FolderKanban className="w-3.5 h-3.5 text-orange-400" />
              <span>Dự án ({channelProjects.length})</span>
            </button>
          )}

          {isWorkspaceMode && (
            <>
              <button
                onClick={() => setShowLogs(!showLogs)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-zinc-900 border border-[var(--vc-border)] text-zinc-300 hover:text-white hover:border-zinc-700 transition"
              >
                <Terminal className="w-3.5 h-3.5 text-amber-400" />
                <span>Log ({logs.length})</span>
              </button>

              <button
                onClick={resetProduction}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-zinc-900 border border-zinc-700 text-zinc-300 hover:bg-zinc-800 transition"
              >
                <Plus className="w-3.5 h-3.5 text-amber-400" />
                Dự Án Mới
              </button>
            </>
          )}
        </div>
      </div>

      {/* Project History Drawer (Optional Expand) */}
      {showProjectHistory && (
        <div className="glass-panel p-5 rounded-2xl border border-[var(--vc-border)] bg-zinc-950/90 space-y-3">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-2.5">
            <div className="flex items-center gap-2">
              <FolderKanban className="w-4 h-4 text-orange-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                Lịch Sử Dự Án của Kênh: <span className="text-amber-400">{selectedChannel?.name}</span>
              </h3>
            </div>
            <button
              onClick={() => setShowProjectHistory(false)}
              className="text-xs text-zinc-500 hover:text-zinc-300"
            >
              Đóng
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 max-h-60 overflow-y-auto pr-1">
            {channelProjects.map((proj) => (
              <div
                key={proj.id}
                onClick={() => {
                  loadExistingProject(proj.id);
                  setShowProjectHistory(false);
                }}
                className={`p-3 rounded-xl border transition cursor-pointer flex flex-col justify-between gap-2 ${
                  projectId === proj.id
                    ? "bg-amber-500/10 border-amber-500/50 ring-1 ring-amber-500/30"
                    : "bg-zinc-900/60 border-zinc-800/80 hover:border-zinc-700 hover:bg-zinc-900"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[11px] font-bold text-amber-400">#{proj.id}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-zinc-800 border border-zinc-700 text-zinc-300 capitalize">
                    {proj.current_stage || "brief"}
                  </span>
                </div>
                <p className="text-xs text-zinc-200 line-clamp-2 leading-relaxed">
                  {proj.idea}
                </p>
                <div className="flex items-center justify-between text-[10px] text-zinc-500 pt-1 border-t border-zinc-800/60">
                  <span>{new Date(proj.created_at).toLocaleDateString("vi-VN")}</span>
                  <span className="text-amber-400 font-semibold flex items-center gap-1">
                    Mở vào Studio <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Mode 1: Initial Setup Form (When not in workspace mode) */}
      {!isWorkspaceMode ? (
        <form onSubmit={handleStartProduction} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Idea Input */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass-panel p-6 rounded-2xl border border-[var(--vc-border)] space-y-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Wand2 className="w-4 h-4 text-amber-400" />
                  <label className="text-sm font-semibold text-zinc-200">
                    Ý Tưởng Video (Prompt & Storyline):
                  </label>
                </div>
                <span className="text-[11px] text-zinc-400 font-mono">
                  {idea.length} / 5000 ký tự
                </span>
              </div>

              <textarea
                value={idea}
                onChange={(e) => setIdea(e.target.value)}
                placeholder="Mô tả ý tưởng kịch bản video, bối cảnh, nhân vật hoặc thông điệp cốt lõi bạn muốn truyền tải..."
                rows={7}
                className="w-full p-4 rounded-xl bg-black/40 border border-[var(--vc-border)] focus:border-amber-500 focus:ring-1 focus:ring-amber-500 text-sm leading-relaxed outline-none transition resize-none placeholder:text-zinc-600"
              />

              {/* Quick Template Chips */}
              <div className="space-y-2">
                <span className="text-xs text-zinc-400 font-medium flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  Gợi ý chủ đề thịnh hành:
                </span>
                <div className="flex flex-wrap gap-2">
                  {quickPromptTemplates.map((tmpl, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setIdea(tmpl)}
                      className="px-3 py-1.5 rounded-lg text-xs bg-zinc-900/80 hover:bg-zinc-800 border border-[var(--vc-border)] hover:border-amber-500/40 text-zinc-300 hover:text-amber-300 transition text-left"
                    >
                      {tmpl}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Launch CTA */}
            <div className="glass-panel p-6 rounded-2xl border border-amber-500/30 bg-gradient-to-r from-amber-500/10 via-orange-500/5 to-transparent flex flex-col md:flex-row items-center justify-between gap-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-400" />
                  Quy Trình Kiểm Soát Từng Bước (Human-in-the-Loop)
                </h3>
                <p className="text-xs text-zinc-400 mt-1">
                  Mỗi giai đoạn (Brief, Kịch bản, Ảnh, Audio, Render) sẽ dừng lại để bạn duyệt hoặc chỉnh sửa trước khi chuyển bước tiếp theo.
                </p>
              </div>

              <button
                type="submit"
                disabled={isProcessing}
                className="w-full md:w-auto px-8 py-3.5 rounded-xl font-bold text-sm text-black bg-gradient-to-r from-amber-400 via-orange-400 to-amber-500 hover:from-amber-300 hover:to-orange-400 shadow-lg shadow-amber-500/20 active:scale-[0.98] transition flex items-center justify-center gap-2 whitespace-nowrap"
              >
                <Play className="w-4 h-4 fill-black" />
                Bắt Đầu Sản Xuất (Từng Bước)
              </button>
            </div>
          </div>

          {/* Sidebar Settings */}
          <div className="space-y-6">
            {/* AI Engine & Models */}
            <div className="glass-panel p-5 rounded-2xl border border-[var(--vc-border)] space-y-4">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-300 uppercase tracking-wider block">
                  Cấu Hình AI Engine
                </label>
                <span className="text-[10px] text-emerald-400 font-semibold flex items-center gap-1">
                  <Check className="w-3 h-3 text-emerald-400" />
                  Đã tự động lưu
                </span>
              </div>

              <div className="space-y-3">
                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-zinc-400">AI Provider:</label>
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-black/50 border border-[var(--vc-border)] text-xs"
                  >
                    <option value="Gemini">Google Gemini (Tối ưu nhất)</option>
                    <option value="OpenAI">OpenAI (ChatGPT & DALL-E)</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-zinc-400">Model Kịch Bản:</label>
                  <select
                    value={modelName}
                    onChange={(e) => setModelName(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-black/50 border border-[var(--vc-border)] text-xs"
                  >
                    {provider.includes("Gemini") ? (
                      <>
                        <option value="gemini-3.6-flash">Gemini 3.6 Flash (Khuyên dùng)</option>
                        <option value="gemini-3.7-flash">Gemini 3.7 Flash (Mới nhất)</option>
                        <option value="gemini-flash-latest">Gemini Flash Latest</option>
                        <option value="gemini-3.1-pro-preview">Gemini 3.1 Pro Preview</option>
                      </>
                    ) : (
                      <>
                        <option value="gpt-4o-mini">GPT-4o Mini (Tối ưu chi phí)</option>
                        <option value="gpt-4o">GPT-4o (Chất lượng cao)</option>
                      </>
                    )}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-zinc-400">Image Engine (Sinh Ảnh):</label>
                  <select
                    value={imageEngine}
                    onChange={(e) => setImageEngine(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-black/50 border border-[var(--vc-border)] text-xs font-medium text-white"
                  >
                    <optgroup label="Google Gemini Image Models">
                      <option value="gemini-2.5-flash-image">Gemini 2.5 Flash Image (Chuẩn)</option>
                      <option value="gemini-3-pro-image">Gemini 3 Pro Image (Chất lượng cao)</option>
                      <option value="gemini-3.1-flash-image">Gemini 3.1 Flash Image (Mới nhất)</option>
                      <option value="gemini-3.1-flash-lite-image">Gemini 3.1 Flash Lite Image</option>
                    </optgroup>
                    <optgroup label="High Quality Free & Cloud">
                      <option value="flux-realism">Flux Realism Ultra HD (Miễn phí / Sắc nét)</option>
                      <option value="dalle">OpenAI DALL-E 3</option>
                      <option value="sdxl">Stable Diffusion XL (Cloud)</option>
                    </optgroup>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-zinc-400">Video Render Engine:</label>
                  <select
                    value={videoEngine}
                    onChange={(e) => setVideoEngine(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-black/50 border border-[var(--vc-border)] text-xs"
                  >
                    <option value="hunyuan">Tencent Hunyuan Video (SOTA)</option>
                    <option value="wan2.1_local">Wan 2.1 Video Engine</option>
                    <option value="luma">Luma Dream Machine</option>
                  </select>
                </div>

                <div className="space-y-1.5 pt-1">
                  <label className="text-[11px] font-semibold text-zinc-400 block">Tỷ Lệ Khung Hình:</label>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => setAspectRatio("9:16")}
                      className={`p-2 rounded-xl border text-center transition flex flex-col items-center gap-1 ${
                        aspectRatio === "9:16"
                          ? "border-amber-500 bg-amber-500/10 text-amber-400 font-bold"
                          : "border-[var(--vc-border)] bg-black/40 text-zinc-400 hover:border-zinc-700"
                      }`}
                    >
                      <Smartphone className="w-4 h-4" />
                      <span className="text-[10px]">9:16 (Shorts)</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setAspectRatio("16:9")}
                      className={`p-2 rounded-xl border text-center transition flex flex-col items-center gap-1 ${
                        aspectRatio === "16:9"
                          ? "border-amber-500 bg-amber-500/10 text-amber-400 font-bold"
                          : "border-[var(--vc-border)] bg-black/40 text-zinc-400 hover:border-zinc-700"
                      }`}
                    >
                      <Monitor className="w-4 h-4" />
                      <span className="text-[10px]">16:9 (Ngang)</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setAspectRatio("1:1")}
                      className={`p-2 rounded-xl border text-center transition flex flex-col items-center gap-1 ${
                        aspectRatio === "1:1"
                          ? "border-amber-500 bg-amber-500/10 text-amber-400 font-bold"
                          : "border-[var(--vc-border)] bg-black/40 text-zinc-400 hover:border-zinc-700"
                      }`}
                    >
                      <Layers className="w-4 h-4" />
                      <span className="text-[10px]">1:1 (Vuông)</span>
                    </button>
                  </div>
                </div>

                <div className="pt-2">
                  <button
                    type="button"
                    onClick={handleSaveDefaultConfig}
                    className="w-full py-2 px-3 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 hover:text-white text-xs font-semibold transition flex items-center justify-center gap-2"
                  >
                    {savedFeedback ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400 font-bold">Đã lưu vào CSDL hệ thống!</span>
                      </>
                    ) : (
                      <>
                        <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                        <span>Lưu Làm Mặc Định Hệ Thống</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </form>
      ) : (
        /* Mode 2: Step-by-Step Approval Workspace */
        <div className="space-y-6">
          {/* Top Interactive Stepper Bar */}
          <div className="glass-panel p-3.5 rounded-2xl border border-[var(--vc-border)] bg-zinc-950/80">
            <div className="flex overflow-x-auto pb-1 gap-2.5 sm:grid sm:grid-cols-3 md:grid-cols-5">
              {STAGES_LIST.map((stage, idx) => {
                const status = stageApproval[stage.key] || "pending";
                const isCurrent = currentStepIndex === idx;
                const Icon = stage.icon;

                let badgeColor = "bg-zinc-900 border-zinc-800 text-zinc-500";
                let statusLabel = "Chờ tới lượt";

                if (status === "running") {
                  badgeColor = "bg-amber-500/20 border-amber-500/40 text-amber-300 animate-pulse";
                  statusLabel = "Đang chạy...";
                } else if (status === "waiting_approval") {
                  badgeColor = "bg-orange-500/20 border-orange-500/50 text-orange-400 font-bold shadow-lg shadow-orange-500/10";
                  statusLabel = "Chờ bạn duyệt!";
                } else if (status === "approved") {
                  badgeColor = "bg-emerald-500/15 border-emerald-500/30 text-emerald-400";
                  statusLabel = "Đã phê duyệt";
                } else if (status === "error") {
                  badgeColor = "bg-red-500/20 border-red-500/30 text-red-400";
                  statusLabel = "Gặp lỗi";
                }

                return (
                  <button
                    key={stage.key}
                    type="button"
                    onClick={() => setCurrentStepIndex(idx)}
                    className={`p-3 rounded-xl border text-left transition relative flex flex-col justify-between gap-1.5 min-w-[155px] sm:min-w-0 flex-1 ${
                      isCurrent
                        ? "bg-zinc-900/90 border-amber-500/60 ring-1 ring-amber-500/30"
                        : "bg-zinc-950/40 border-[var(--vc-border)] hover:bg-zinc-900/40"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={`p-1.5 rounded-lg border ${badgeColor}`}>
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <span className="text-xs font-bold text-zinc-200">
                          {stage.shortTitle}
                        </span>
                      </div>
                      {status === "approved" && (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      )}
                    </div>

                    <div className="flex items-center justify-between text-[10px]">
                      <span className="text-zinc-400 font-mono">Bước {idx + 1}/5</span>
                      <span className={`font-semibold ${
                        status === "waiting_approval" ? "text-orange-400" :
                        status === "approved" ? "text-emerald-400" :
                        status === "running" ? "text-amber-400" : "text-zinc-500"
                      }`}>
                        {statusLabel}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Active Step Workspace */}
          <div className="glass-panel rounded-2xl border border-[var(--vc-border)] overflow-hidden bg-zinc-950/90">
            {/* Stage Header */}
            <div className="p-6 border-b border-[var(--vc-border)] bg-gradient-to-r from-zinc-900/80 to-transparent flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start gap-3.5">
                <div className="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-400 mt-0.5">
                  <currentStageMeta.icon className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2.5">
                    <h2 className="text-lg font-bold text-white">
                      {currentStageMeta.name}
                    </h2>
                    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${
                      currentStatus === "waiting_approval" ? "bg-orange-500/20 border-orange-500/40 text-orange-400 animate-pulse" :
                      currentStatus === "approved" ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-400" :
                      currentStatus === "running" ? "bg-amber-500/20 border-amber-500/40 text-amber-400" :
                      "bg-zinc-800 border-zinc-700 text-zinc-400"
                    }`}>
                      {currentStatus === "waiting_approval" ? "CHỜ BẠN DUYỆT" :
                       currentStatus === "approved" ? "ĐÃ PHÊ DUYỆT" :
                       currentStatus === "running" ? "ĐANG SINH NỘI DUNG..." : "CHƯA THỰC THI"}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-400 mt-1">
                    {currentStageMeta.description}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {projectId && (
                  <a
                    href={`http://127.0.0.1:8000/api/v1/production/projects/${projectId}/export-bundle`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-amber-500/15 border border-amber-500/30 text-amber-400 hover:bg-amber-500/25 transition shadow-sm"
                    title="Tải toàn bộ file dự án (kịch bản Markdown, ảnh PNG phân cảnh, audio MP3, video MP4) thành file ZIP"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Tải Gói Dự Án (ZIP)</span>
                  </a>
                )}
                {currentContent && (
                  <button
                    type="button"
                    onClick={() => handleCopy(currentContent)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-zinc-900 border border-[var(--vc-border)] text-zinc-300 hover:text-white transition"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-zinc-400" />}
                    <span>{copied ? "Đã chép!" : "Sao chép"}</span>
                  </button>
                )}
              </div>
            </div>

            {/* Stage Body Content */}
            <div className="p-6 space-y-6">
              {currentStatus === "running" ? (
                <div className="py-16 text-center space-y-4">
                  <div className="w-12 h-12 rounded-full border-2 border-amber-500/30 border-t-amber-400 animate-spin mx-auto" />
                  <div>
                    <h4 className="text-sm font-bold text-white">
                      AI đang xử lý giai đoạn: {currentStageMeta.shortTitle}...
                    </h4>
                    <p className="text-xs text-zinc-400 mt-1 max-w-md mx-auto">
                      Quy trình sử dụng {provider} ({modelName}) kết hợp WorkflowEngine để tối ưu chất lượng. Vui lòng đợi trong giây lát.
                    </p>
                  </div>
                </div>
              ) : currentContent ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
                      <Edit3 className="w-3.5 h-3.5 text-amber-400" />
                      Nội dung chi tiết (Bạn có thể chỉnh sửa trực tiếp trước khi duyệt):
                    </span>
                    <span className="text-[11px] text-zinc-500 font-mono">
                      {currentContent.length} ký tự
                    </span>
                  </div>

                  {/* Stage-specific Media Previews */}
                  {currentStageMeta.key === "image" && mediaOutputs.image && mediaOutputs.image.length > 0 && (
                    <div className="p-4 rounded-xl bg-zinc-900/60 border border-[var(--vc-border)] space-y-3">
                      <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                        <ImageIcon className="w-4 h-4" />
                        Danh sách Ảnh AI đã sinh ({mediaOutputs.image.length} ảnh):
                      </h4>
                      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                        {mediaOutputs.image.map((imgUrl, i) => (
                          <div
                            key={i}
                            onClick={() => setSelectedImageModal(imgUrl)}
                            className="group relative rounded-xl overflow-hidden border border-zinc-800 bg-black aspect-[9/16] flex items-center justify-center cursor-pointer hover:border-amber-500/70 hover:shadow-lg hover:shadow-amber-500/10 transition"
                          >
                            <img
                              src={`http://127.0.0.1:8000/${imgUrl.replace(/\\/g, "/")}`}
                              alt={`Scene ${i + 1}`}
                              className="w-full h-full object-cover group-hover:scale-105 transition"
                            />
                            {/* Permanent top-left Badge */}
                            <div className="absolute top-2 left-2 z-10 px-2 py-0.5 rounded-md bg-black/75 backdrop-blur-md border border-amber-500/30 text-[9px] font-bold text-amber-400 shadow">
                              {imageEngine.includes("flux") ? "Flux Realism" : imageEngine.includes("gemini") ? "Gemini Image" : "DALL-E 3"}
                            </div>

                            {/* Hover Overlay */}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition p-3 flex flex-col justify-between z-20">
                              <div className="flex items-center justify-end">
                                <span className="p-1.5 rounded-lg bg-black/60 text-white border border-white/10">
                                  <Maximize2 className="w-3.5 h-3.5 text-amber-400" />
                                </span>
                              </div>
                              <div className="flex items-center justify-between">
                                <span className="text-[11px] font-bold text-white">Ảnh Cảnh #{i + 1}</span>
                                <span className="text-[9px] text-amber-400 font-semibold">Nhấp để xem</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {currentStageMeta.key === "voice" && mediaOutputs.voice && mediaOutputs.voice.length > 0 && (
                    <div className="p-4 rounded-xl bg-zinc-900/60 border border-[var(--vc-border)] space-y-3">
                      <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                        <Volume2 className="w-4 h-4" />
                        File Âm Thanh Voiceover AI:
                      </h4>
                      <audio controls className="w-full">
                        <source src={`http://127.0.0.1:8000/${mediaOutputs.voice[0].replace(/\\/g, "/")}`} type="audio/mpeg" />
                        Trình duyệt không hỗ trợ audio player.
                      </audio>
                    </div>
                  )}

                  {currentStageMeta.key === "video" && mediaOutputs.video && mediaOutputs.video.length > 0 && (
                    <div className="p-4 rounded-xl bg-zinc-900/60 border border-emerald-500/30 space-y-3">
                      <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                        <Video className="w-4 h-4" />
                        Video Hoàn Thiện:
                      </h4>
                      <video controls className="w-full max-h-96 rounded-lg bg-black">
                        <source src={`http://127.0.0.1:8000/${mediaOutputs.video[0].replace(/\\/g, "/")}`} type="video/mp4" />
                      </video>
                    </div>
                  )}

                  {/* Editable Raw Textarea */}
                  <textarea
                    value={currentContent}
                    onChange={(e) => updateStageContent(currentStageMeta.key, e.target.value)}
                    rows={12}
                    className="w-full p-4 rounded-xl bg-black/60 border border-[var(--vc-border)] focus:border-amber-500/70 focus:ring-1 focus:ring-amber-500/50 text-xs font-mono leading-relaxed outline-none transition resize-y text-zinc-200"
                  />
                </div>
              ) : (
                <div className="py-12 text-center space-y-3 text-zinc-500">
                  <currentStageMeta.icon className="w-8 h-8 mx-auto text-zinc-600" />
                  <p className="text-xs">Giai đoạn này chưa có nội dung hoặc chưa được thực thi.</p>
                  <button
                    type="button"
                    onClick={() => selectedChannelId && runStageStep(currentStepIndex, selectedChannelId)}
                    disabled={isProcessing}
                    className="px-4 py-2 rounded-xl text-xs font-semibold bg-zinc-900 border border-zinc-700 text-zinc-200 hover:bg-zinc-800 transition inline-flex items-center gap-2"
                  >
                    <Play className="w-3.5 h-3.5 text-amber-400" />
                    Chạy Giai Đoạn Này Ngay
                  </button>
                </div>
              )}
            </div>

            {/* Bottom Action / Approval Bar */}
            <div className="p-4 px-6 border-t border-[var(--vc-border)] bg-zinc-950 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="text-xs text-zinc-400">
                {currentStatus === "waiting_approval" ? (
                  <span className="text-orange-400 font-semibold flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4" />
                    Hãy kiểm tra nội dung ở trên, sau đó bấm nút &quot;Duyệt &amp; Tiếp Tục&quot;.
                  </span>
                ) : currentStatus === "approved" ? (
                  <span className="text-emerald-400 font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4" />
                    Giai đoạn này đã được phê duyệt thành công!
                  </span>
                ) : (
                  <span>Bạn có thể chỉnh sửa nội dung bất cứ lúc nào trước khi duyệt.</span>
                )}
              </div>

              <div className="flex items-center gap-3 w-full sm:w-auto">
                {/* Regenerate Button */}
                <button
                  type="button"
                  onClick={() => selectedChannelId && regenerateStage(currentStepIndex, selectedChannelId)}
                  disabled={isProcessing}
                  className="flex-1 sm:flex-initial px-4 py-2.5 rounded-xl text-xs font-semibold bg-zinc-900 border border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-white transition flex items-center justify-center gap-2"
                >
                  <RotateCcw className="w-3.5 h-3.5 text-zinc-400" />
                  Thực Thi Lại Bước Này
                </button>

                {/* Approve & Next Button */}
                <button
                  type="button"
                  onClick={() => selectedChannelId && approveAndNext(selectedChannelId)}
                  disabled={isProcessing || !currentContent}
                  className={`flex-1 sm:flex-initial px-6 py-2.5 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 ${
                    currentStatus === "approved"
                      ? "bg-emerald-600 hover:bg-emerald-500 text-white"
                      : "bg-gradient-to-r from-amber-400 via-orange-400 to-amber-500 hover:from-amber-300 hover:to-orange-400 text-black shadow-lg shadow-amber-500/20"
                  }`}
                >
                  {currentStepIndex === STAGES_LIST.length - 1 ? (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      Hoàn Tất Toàn Bộ Video
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4" />
                      Duyệt &amp; Sang Bước {currentStepIndex + 2} ({STAGES_LIST[currentStepIndex + 1]?.shortTitle})
                      <ArrowRight className="w-3.5 h-3.5 ml-0.5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Real-time WebSocket Log Console */}
          {showLogs && (
            <div className="glass-panel p-4 rounded-2xl border border-[var(--vc-border)] bg-black/90 space-y-3">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                <div className="flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-amber-400" />
                  <span className="text-xs font-mono font-bold text-zinc-300">Live WebSocket Console</span>
                </div>
                <button
                  onClick={() => setShowLogs(false)}
                  className="text-zinc-500 hover:text-zinc-300 text-xs"
                >
                  Đóng
                </button>
              </div>
              <div className="h-44 overflow-y-auto font-mono text-[11px] space-y-1 text-zinc-400 pr-2">
                {logs.length > 0 ? (
                  logs.map((log, i) => (
                    <div key={i} className="leading-relaxed">
                      <span className="text-zinc-600 mr-2">{i + 1}.</span>
                      <span className={
                        log.includes("[ERROR]") ? "text-red-400" :
                        log.includes("[APPROVED]") ? "text-emerald-400" :
                        log.includes("[WAIT]") ? "text-orange-400" :
                        log.includes("[SUCCESS]") ? "text-emerald-300" : "text-zinc-300"
                      }>
                        {log}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-zinc-600 italic">Chưa có bản ghi nhật ký nào.</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Image Lightbox Modal */}
      {selectedImageModal && (
        <div 
          onClick={() => setSelectedImageModal(null)}
          className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 animate-fadeIn"
        >
          <div 
            onClick={(e) => e.stopPropagation()}
            className="relative max-w-4xl max-h-[92vh] flex flex-col items-center glass-panel rounded-2xl border border-zinc-700 bg-zinc-950 p-4 space-y-3 overflow-hidden shadow-2xl"
          >
            {/* Modal Header */}
            <div className="w-full flex flex-wrap items-center justify-between border-b border-zinc-800 pb-3 gap-2">
              <div className="flex items-center gap-2">
                <ImageIcon className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-bold text-white">
                  Xem Chi Tiết Ảnh AI
                </span>
                <span className="px-2 py-0.5 rounded-md bg-amber-500/20 border border-amber-500/30 text-[10px] font-bold text-amber-400">
                  Được tạo bởi: {imageEngine.includes("flux") ? "Flux Realism (8K Ultra HD)" : imageEngine.includes("gemini") ? "Google Gemini Image Native" : "OpenAI DALL-E 3"}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <a
                  href={`http://127.0.0.1:8000/${selectedImageModal.replace(/\\/g, "/")}`}
                  target="_blank"
                  rel="noreferrer"
                  className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-300 hover:text-white hover:bg-zinc-800 transition"
                  title="Mở tab mới"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>

                <a
                  href={`http://127.0.0.1:8000/${selectedImageModal.replace(/\\/g, "/")}`}
                  download
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs transition shadow-lg shadow-amber-500/20"
                >
                  <Download className="w-3.5 h-3.5" />
                  Tải Ảnh Về
                </a>

                <button
                  type="button"
                  onClick={() => setSelectedImageModal(null)}
                  className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Modal Full Image */}
            <div className="relative max-h-[75vh] overflow-hidden rounded-xl bg-black flex items-center justify-center">
              <img
                src={`http://127.0.0.1:8000/${selectedImageModal.replace(/\\/g, "/")}`}
                alt="AI Generated Full"
                className="max-h-[75vh] w-auto object-contain rounded-xl shadow-inner"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
