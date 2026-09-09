"use client";

import Link from "next/link";
import { useChannelStore } from "@/stores/useChannelStore";
import { 
  Film, 
  Layers, 
  Sparkles, 
  Activity, 
  ArrowRight, 
  CheckCircle2, 
  Cpu, 
  PlaySquare 
} from "lucide-react";

export default function DashboardPage() {
  const { channels, isLoading } = useChannelStore();

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Hero Banner */}
      <div className="glass-panel p-5 sm:p-8 relative overflow-hidden border-[var(--vc-border)]">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-[#C2542D]/20 to-[#C99A45]/10 blur-3xl -z-10 rounded-full" />
        <div className="max-w-2xl space-y-4">
          <div className="vc-badge">
            <Sparkles className="w-3.5 h-3.5 text-[#C2542D] shrink-0" />
            AI Video Production Studio v2.0
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight">
            Tự động hóa sản xuất <span className="gradient-text">Video Ngắn Đa Kênh</span>
          </h1>
          <p className="text-[var(--vc-muted)] text-sm leading-relaxed">
            Hệ thống đa tác nhân CrewAI kết hợp xử lý bất đồng bộ FastAPI & WebSocket, 
            cho phép sáng tạo kịch bản, vẽ phối cảnh và dựng video hoàn chỉnh theo thời gian thực.
          </p>
          <div className="pt-2 flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <Link
              href="/production"
              className="gradient-btn w-full sm:w-auto px-5 py-2.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2"
            >
              <PlaySquare className="w-4 h-4" />
              Bắt đầu Sản xuất Ngay
            </Link>
            <Link
              href="/channels"
              className="w-full sm:w-auto px-5 py-2.5 rounded-xl font-semibold text-sm text-zinc-300 hover:text-white bg-white/[0.05] hover:bg-white/[0.08] transition border border-white/10 flex items-center justify-center gap-2"
            >
              <Layers className="w-4 h-4" />
              Quản lý Kênh ({channels.length})
            </Link>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="glass-panel p-6 glass-panel-hover">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[var(--vc-muted)]">
              Kênh Đang Hoạt Động
            </span>
            <div className="p-2 rounded-lg bg-[#C2542D]/10 text-[#C2542D]">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold mt-3">{isLoading ? "..." : channels.length}</div>
          <div className="text-xs text-[var(--vc-muted)] mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Đã đồng bộ cơ sở dữ liệu
          </div>
        </div>

        <div className="glass-panel p-6 glass-panel-hover">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[var(--vc-muted)]">
              Hạ Tầng Backend
            </span>
            <div className="p-2 rounded-lg bg-[#C99A45]/10 text-[#C99A45]">
              <Cpu className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold mt-3">DidicrewStudio</div>
          <div className="text-xs text-[var(--vc-muted)] mt-1 flex items-center gap-1">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            Core AI Engine & Workflow
          </div>
        </div>

        <div className="glass-panel p-6 glass-panel-hover">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-[var(--vc-muted)]">
              Giao Thức Streaming
            </span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Sparkles className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold mt-3">WebSockets</div>
          <div className="text-xs text-[var(--vc-muted)] mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Real-time Pipeline Tracker
          </div>
        </div>
      </div>
    </div>
  );
}
