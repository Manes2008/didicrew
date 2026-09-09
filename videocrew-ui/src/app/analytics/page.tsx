"use client";

import { useState, useEffect } from "react";
import { apiClient, AnalyticsData } from "@/lib/api-client";
import { BarChart3, Coins, Clock, CheckCircle2, TrendingUp, Cpu, Download, Filter, Search, RefreshCw, FileText, Image as ImageIcon, Mic, Video } from "lucide-react";

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedStageFilter, setSelectedStageFilter] = useState<string>("all");
  const [searchModel, setSearchModel] = useState("");

  const fetchStats = () => {
    setLoading(true);
    apiClient.getAnalytics()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleExportCSV = () => {
    if (!data?.cost_logs || data.cost_logs.length === 0) return;
    const headers = ["ID", "Giai doan", "Sub-Step", "Model", "Input Tokens", "Output Tokens", "Tong Tokens", "Chi phi USD", "Thoi gian s", "Thoi diem"];
    const rows = data.cost_logs.map(l => [
      l.id,
      l.stage_name,
      l.sub_step_name || "",
      l.model_name || "",
      l.input_tokens,
      l.output_tokens,
      l.total_tokens,
      l.cost_usd,
      l.elapsed_seconds,
      l.created_at
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `videocrew_analytics_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredLogs = (data?.cost_logs || []).filter(l => {
    const matchStage = selectedStageFilter === "all" || l.stage_name === selectedStageFilter;
    const matchModel = !searchModel || (l.model_name && l.model_name.toLowerCase().includes(searchModel.toLowerCase())) || (l.sub_step_name && l.sub_step_name.toLowerCase().includes(searchModel.toLowerCase()));
    return matchStage && matchModel;
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold flex items-center gap-2.5">
            <BarChart3 className="w-7 h-7 text-[#C2542D]" />
            Phân Tích Hiệu Quả & Chi Phí Token
          </h1>
          <p className="text-sm text-[var(--vc-muted)] mt-1">
            Theo dõi chi tiết mức độ tiêu hao Token, chi phí USD và thời gian thực thi của từng Engine AI trong quy trình sản xuất.
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          <button
            onClick={fetchStats}
            disabled={loading}
            className="p-2.5 rounded-xl bg-zinc-900 border border-zinc-700 text-zinc-300 hover:text-white transition"
            title="Làm mới thống kê"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>

          {data?.cost_logs && data.cost_logs.length > 0 && (
            <button
              onClick={handleExportCSV}
              className="gradient-btn px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2"
            >
              <Download className="w-3.5 h-3.5" />
              Xuất Báo Cáo CSV
            </button>
          )}
        </div>
      </div>

      {/* Stats KPI */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-panel p-5 space-y-2 rounded-2xl border border-[var(--vc-border)]">
          <span className="text-xs font-semibold uppercase tracking-wider text-[var(--vc-muted)]">
            Tổng Dự Án
          </span>
          <div className="text-2xl font-extrabold">{data?.total_projects || 0}</div>
          <div className="text-[11px] text-zinc-400">Đã khởi tạo trong hệ thống</div>
        </div>

        <div className="glass-panel p-5 space-y-2 rounded-2xl border border-[var(--vc-border)]">
          <span className="text-xs font-semibold uppercase tracking-wider text-[var(--vc-muted)]">
            Dự Án Hoàn Thành
          </span>
          <div className="text-2xl font-extrabold text-emerald-400">{data?.completed_projects || 0}</div>
          <div className="text-[11px] text-zinc-400">Xuất video & duyệt thành công</div>
        </div>

        <div className="glass-panel p-5 space-y-2 rounded-2xl border border-[var(--vc-border)]">
          <span className="text-xs font-semibold uppercase tracking-wider text-[var(--vc-muted)]">
            Tổng Token Sử Dụng
          </span>
          <div className="text-2xl font-extrabold text-amber-400">
            {(data?.total_tokens_used || 0).toLocaleString()}
          </div>
          <div className="text-[11px] text-zinc-400">Token Input + Output (LLM)</div>
        </div>

        <div className="glass-panel p-5 space-y-2 rounded-2xl border border-[var(--vc-border)]">
          <span className="text-xs font-semibold uppercase tracking-wider text-[var(--vc-muted)]">
            Tổng Chi Phí Ước Tính
          </span>
          <div className="text-2xl font-extrabold text-[#C2542D] flex items-baseline gap-2">
            ${data?.total_cost_usd || "0.0000"}
            <span className="text-xs font-normal text-zinc-400">
              (~{(Number(data?.total_cost_usd || 0) * 25400).toLocaleString("vi-VN", { maximumFractionDigits: 0 })} VNĐ)
            </span>
          </div>
          <div className="text-[11px] text-zinc-400">USD tương đương</div>
        </div>
      </div>

      {/* Filter Bar & Cost Table */}
      <div className="glass-panel p-6 space-y-5 rounded-2xl border border-[var(--vc-border)]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--vc-border)] pb-4">
          <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-200 flex items-center gap-2">
            <Coins className="w-4 h-4 text-amber-400" />
            Nhật Ký Chi Tiết Tiêu Hao Token Theo Giai Đoạn ({filteredLogs.length})
          </h2>

          <div className="flex flex-wrap items-center gap-3">
            {/* Stage Filter */}
            <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-zinc-800 text-xs overflow-x-auto max-w-full">
              <button
                onClick={() => setSelectedStageFilter("all")}
                className={`px-3 py-1.5 rounded-lg font-semibold transition whitespace-nowrap ${selectedStageFilter === "all" ? "bg-amber-500 text-black" : "text-zinc-400 hover:text-white"}`}
              >
                Tất cả
              </button>
              <button
                onClick={() => setSelectedStageFilter("brief")}
                className={`px-2.5 py-1.5 rounded-lg font-semibold transition whitespace-nowrap ${selectedStageFilter === "brief" ? "bg-amber-500 text-black" : "text-zinc-400 hover:text-white"}`}
              >
                Brief
              </button>
              <button
                onClick={() => setSelectedStageFilter("script")}
                className={`px-2.5 py-1.5 rounded-lg font-semibold transition whitespace-nowrap ${selectedStageFilter === "script" ? "bg-amber-500 text-black" : "text-zinc-400 hover:text-white"}`}
              >
                Kịch bản
              </button>
              <button
                onClick={() => setSelectedStageFilter("image")}
                className={`px-2.5 py-1.5 rounded-lg font-semibold transition whitespace-nowrap ${selectedStageFilter === "image" ? "bg-amber-500 text-black" : "text-zinc-400 hover:text-white"}`}
              >
                Ảnh AI
              </button>
              <button
                onClick={() => setSelectedStageFilter("voice")}
                className={`px-2.5 py-1.5 rounded-lg font-semibold transition whitespace-nowrap ${selectedStageFilter === "voice" ? "bg-amber-500 text-black" : "text-zinc-400 hover:text-white"}`}
              >
                Giọng đọc
              </button>
              <button
                onClick={() => setSelectedStageFilter("video")}
                className={`px-2.5 py-1.5 rounded-lg font-semibold transition whitespace-nowrap ${selectedStageFilter === "video" ? "bg-amber-500 text-black" : "text-zinc-400 hover:text-white"}`}
              >
                Render
              </button>
            </div>

            {/* Search Input */}
            <div className="relative">
              <input
                type="text"
                value={searchModel}
                onChange={(e) => setSearchModel(e.target.value)}
                placeholder="Tìm model/step..."
                className="px-3 py-1.5 pl-8 rounded-xl bg-black/40 border border-zinc-800 text-xs text-zinc-200 outline-none focus:border-amber-500 w-36"
              />
              <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-2.5 top-2" />
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs min-w-[680px]">
            <thead>
              <tr className="border-b border-zinc-800 text-zinc-400 font-semibold">
                <th className="py-3 px-3">Giai đoạn</th>
                <th className="py-3 px-3">Sub-Step</th>
                <th className="py-3 px-3">Model / Engine</th>
                <th className="py-3 px-3">Input</th>
                <th className="py-3 px-3">Output</th>
                <th className="py-3 px-3">Tổng Tokens</th>
                <th className="py-3 px-3">Chi phí ($)</th>
                <th className="py-3 px-3">Thời gian</th>
                <th className="py-3 px-3">Thời điểm</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-900 text-zinc-300 font-mono">
              {filteredLogs.length > 0 ? (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-white/[0.02] transition">
                    <td className="py-3 px-3 font-sans font-bold text-white uppercase">
                      <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[10px]">
                        {log.stage_name}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-zinc-400">{log.sub_step_name || "-"}</td>
                    <td className="py-3 px-3 text-amber-400 font-semibold">{log.model_name || "gemini-3.6-flash"}</td>
                    <td className="py-3 px-3">{log.input_tokens.toLocaleString()}</td>
                    <td className="py-3 px-3">{log.output_tokens.toLocaleString()}</td>
                    <td className="py-3 px-3 font-bold text-white">{log.total_tokens.toLocaleString()}</td>
                    <td className="py-3 px-3 text-amber-500 font-bold">${log.cost_usd.toFixed(5)}</td>
                    <td className="py-3 px-3">{log.elapsed_seconds.toFixed(2)}s</td>
                    <td className="py-3 px-3 font-sans text-zinc-500">
                      {new Date(log.created_at).toLocaleTimeString("vi-VN")} - {new Date(log.created_at).toLocaleDateString("vi-VN")}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-zinc-600 font-sans italic">
                    Chưa có nhật ký tiêu hao token nào khớp với bộ lọc.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
