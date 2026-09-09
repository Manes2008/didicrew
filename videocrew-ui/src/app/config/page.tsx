"use client";

import { useState, useEffect } from "react";
import { useConfigStore } from "@/stores/useConfigStore";
import { apiClient } from "@/lib/api-client";
import { Settings, Key, Cpu, Sparkles, Check, Save, ShieldCheck, AlertCircle, RefreshCw } from "lucide-react";

export default function ConfigPage() {
  const { config, updateConfig } = useConfigStore();
  const [openaiKey, setOpenaiKey] = useState("");
  const [geminiKey, setGeminiKey] = useState("");
  const [provider, setProvider] = useState("Gemini");
  const [modelName, setModelName] = useState("gemini-3.6-flash");
  const [videoEngine, setVideoEngine] = useState("hunyuan");
  const [imageEngine, setImageEngine] = useState("flux-realism");
  const [isSaved, setIsSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  // Test Key States
  const [testingGemini, setTestingGemini] = useState(false);
  const [geminiTestResult, setGeminiTestResult] = useState<{ is_valid: boolean; message: string } | null>(null);

  const [testingOpenai, setTestingOpenai] = useState(false);
  const [openaiTestResult, setOpenaiTestResult] = useState<{ is_valid: boolean; message: string } | null>(null);

  useEffect(() => {
    if (config) {
      setProvider(config.provider || "Gemini");
      setModelName(config.model_name || "gemini-3.6-flash");
      setVideoEngine(config.video_engine || "hunyuan");
      setImageEngine(config.image_engine || "flux-realism");
    }
  }, [config]);

  const handleTestKey = async (targetProvider: "Gemini" | "OpenAI") => {
    if (targetProvider === "Gemini") {
      setTestingGemini(true);
      setGeminiTestResult(null);
      try {
        const res = await apiClient.testApiKey("Gemini", geminiKey || undefined);
        setGeminiTestResult({ is_valid: res.is_valid, message: res.message });
      } catch (err: any) {
        setGeminiTestResult({ is_valid: false, message: err.message });
      } finally {
        setTestingGemini(false);
      }
    } else {
      setTestingOpenai(true);
      setOpenaiTestResult(null);
      try {
        const res = await apiClient.testApiKey("OpenAI", openaiKey || undefined);
        setOpenaiTestResult({ is_valid: res.is_valid, message: res.message });
      } catch (err: any) {
        setOpenaiTestResult({ is_valid: false, message: err.message });
      } finally {
        setTestingOpenai(false);
      }
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateConfig({
        openai_api_key: openaiKey || undefined,
        gemini_api_key: geminiKey || undefined,
        provider,
        model_name: modelName,
        video_engine: videoEngine,
        image_engine: imageEngine,
      });
      setOpenaiKey("");
      setGeminiKey("");
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (err: any) {
      alert("Lỗi khi lưu cấu hình: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300 max-w-4xl">
      <div>
        <h1 className="text-2xl font-extrabold flex items-center gap-2.5">
          <Settings className="w-7 h-7 text-[#C2542D]" />
          Cấu hình Hệ thống & AI Keys
        </h1>
        <p className="text-sm text-[var(--vc-muted)] mt-1">
          Quản lý khóa API bảo mật (Google Gemini, OpenAI), kiểm tra tính hợp lệ của key và thiết lập Engine mặc định.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* API Keys Panel */}
        <div className="glass-panel p-6 space-y-5">
          <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2 border-b border-[var(--vc-border)] pb-3">
            <Key className="w-4 h-4 text-[#C99A45]" />
            Bảo mật & Khóa API AI
          </h2>

          <div className="space-y-5">
            {/* Gemini Key */}
            <div className="space-y-2 p-4 rounded-xl bg-zinc-950/60 border border-[var(--vc-border)]">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-300">Google Gemini API Key (Khuyên dùng):</label>
                {config?.has_gemini_key && (
                  <span className="text-[11px] text-emerald-400 font-mono">
                    Đã lưu ({config.masked_gemini_key})
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                <input
                  type="password"
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  placeholder="Nhập khóa mới nếu muốn cập nhật (AI...)"
                  className="flex-1 px-3.5 py-2 rounded-xl bg-black/40 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-[#C2542D]"
                />
                <button
                  type="button"
                  onClick={() => handleTestKey("Gemini")}
                  disabled={testingGemini}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-zinc-900 border border-zinc-700 text-zinc-200 hover:text-white hover:border-amber-500 transition flex items-center gap-1.5"
                >
                  {testingGemini ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />}
                  Test Key
                </button>
              </div>
              {geminiTestResult && (
                <div className={`text-xs p-2.5 rounded-lg flex items-center gap-2 ${
                  geminiTestResult.is_valid ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/20" : "bg-red-500/10 text-red-300 border border-red-500/20"
                }`}>
                  {geminiTestResult.is_valid ? <Check className="w-4 h-4 text-emerald-400" /> : <AlertCircle className="w-4 h-4 text-red-400" />}
                  <span>{geminiTestResult.message}</span>
                </div>
              )}
            </div>

            {/* OpenAI Key */}
            <div className="space-y-2 p-4 rounded-xl bg-zinc-950/60 border border-[var(--vc-border)]">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-300">OpenAI API Key (ChatGPT & DALL-E):</label>
                {config?.has_openai_key && (
                  <span className="text-[11px] text-emerald-400 font-mono">
                    Đã lưu ({config.masked_openai_key})
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                <input
                  type="password"
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  placeholder="Nhập khóa mới nếu muốn cập nhật (sk-...)"
                  className="flex-1 px-3.5 py-2 rounded-xl bg-black/40 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-[#C2542D]"
                />
                <button
                  type="button"
                  onClick={() => handleTestKey("OpenAI")}
                  disabled={testingOpenai}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-zinc-900 border border-zinc-700 text-zinc-200 hover:text-white hover:border-amber-500 transition flex items-center gap-1.5"
                >
                  {testingOpenai ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />}
                  Test Key
                </button>
              </div>
              {openaiTestResult && (
                <div className={`text-xs p-2.5 rounded-lg flex items-center gap-2 ${
                  openaiTestResult.is_valid ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/20" : "bg-red-500/10 text-red-300 border border-red-500/20"
                }`}>
                  {openaiTestResult.is_valid ? <Check className="w-4 h-4 text-emerald-400" /> : <AlertCircle className="w-4 h-4 text-red-400" />}
                  <span>{openaiTestResult.message}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Engine Defaults */}
        <div className="glass-panel p-6 space-y-5">
          <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2 border-b border-[var(--vc-border)] pb-3">
            <Cpu className="w-4 h-4 text-[#C2542D]" />
            Cấu hình Engine Mặc Định Hệ Thống
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300">AI Provider mặc định:</label>
              <select
                value={provider}
                onChange={(e) => {
                  const p = e.target.value;
                  setProvider(p);
                  if (p === "Gemini") {
                    setModelName("gemini-3.6-flash");
                    setImageEngine("flux-realism");
                  } else {
                    setModelName("gpt-4o-mini");
                    setImageEngine("dalle");
                  }
                }}
                className="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-[var(--vc-border)] text-sm"
              >
                <option value="Gemini">Google Gemini (Tối ưu nhất)</option>
                <option value="OpenAI">OpenAI (ChatGPT & DALL-E)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300">Model Kịch Bản Mặc Định:</label>
              <select
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-[var(--vc-border)] text-sm"
              >
                {provider === "Gemini" ? (
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

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300">Video Render Engine:</label>
              <select
                value={videoEngine}
                onChange={(e) => setVideoEngine(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-[var(--vc-border)] text-sm"
              >
                <option value="hunyuan">Tencent Hunyuan Video (SOTA)</option>
                <option value="wan2.1_local">Wan 2.1 Video Engine</option>
                <option value="luma">Luma Dream Machine</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300">Image Engine (Sinh Ảnh):</label>
              <select
                value={imageEngine}
                onChange={(e) => setImageEngine(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-[var(--vc-border)] text-sm"
              >
                <option value="flux-realism">Flux Realism Ultra HD (Khuyên dùng / Miễn phí)</option>
                <option value="gemini-2.5-flash-image">Gemini 2.5 Flash Image</option>
                <option value="gemini-3-pro-image">Gemini 3 Pro Image</option>
                <option value="dalle">OpenAI DALL-E 3</option>
                <option value="sdxl">Stable Diffusion XL (Cloud)</option>
              </select>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          {isSaved ? (
            <div className="flex items-center gap-2 text-emerald-400 text-sm font-semibold animate-in fade-in">
              <Check className="w-4 h-4" />
              Đã lưu cấu hình hệ thống thành công!
            </div>
          ) : (
            <div />
          )}
          <button
            type="submit"
            disabled={saving}
            className="gradient-btn px-6 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 cursor-pointer"
          >
            <Save className="w-4 h-4" />
            {saving ? "Đang lưu..." : "Lưu Cấu Hình"}
          </button>
        </div>
      </form>
    </div>
  );
}
