"use client";

import { useState, useEffect } from "react";
import { apiClient, RustDeskConfigData } from "@/lib/api-client";
import { Monitor, Radio, Key, Save, Check, ShieldAlert } from "lucide-react";

export default function RustDeskPage() {
  const [idServer, setIdServer] = useState("103.179.189.130");
  const [relayServer, setRelayServer] = useState("103.179.189.130");
  const [apiServer, setApiServer] = useState("");
  const [publicKey, setPublicKey] = useState("");
  const [isSaved, setIsSaved] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiClient.getRustDeskConfig().then((cfg) => {
      setIdServer(cfg.id_server || "103.179.189.130");
      setRelayServer(cfg.relay_server || "103.179.189.130");
      setApiServer(cfg.api_server || "");
      setPublicKey(cfg.public_key || "");
    });
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.updateRustDeskConfig({
        id_server: idServer,
        relay_server: relayServer,
        api_server: apiServer,
        public_key: publicKey,
        is_connected: true,
      });
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (err: any) {
      alert("Lỗi cập nhật RustDesk: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in duration-300 max-w-4xl">
      <div>
        <h1 className="text-xl sm:text-2xl font-extrabold flex items-center gap-2.5">
          <Monitor className="w-6 h-6 sm:w-7 sm:h-7 text-[#C2542D] shrink-0" />
          Cấu Hình Điều Khiển Từ Xa (RustDesk)
        </h1>
        <p className="text-sm text-[var(--vc-muted)] mt-1">
          Thiết lập máy chủ Relay Server & Public Key riêng để kết nối điều khiển máy chủ sản xuất video từ xa an toàn.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        <div className="glass-panel p-6 space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--vc-border)] pb-3">
            <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
              <Radio className="w-4 h-4 text-[#C99A45] shrink-0" />
              Máy Chủ RustDesk Tùy Chỉnh (Self-Hosted)
            </h2>
            <span className="vc-badge text-[10px] shrink-0">Đã kết nối</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300">ID Server (Host / IP):</label>
              <input
                type="text"
                required
                value={idServer}
                onChange={(e) => setIdServer(e.target.value)}
                placeholder="103.179.189.130"
                className="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-[#C2542D]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300">Relay Server (Host / IP):</label>
              <input
                type="text"
                required
                value={relayServer}
                onChange={(e) => setRelayServer(e.target.value)}
                placeholder="103.179.189.130"
                className="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-[#C2542D]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300">API Server (Tùy chọn):</label>
              <input
                type="text"
                value={apiServer}
                onChange={(e) => setApiServer(e.target.value)}
                placeholder="http://103.179.189.130:21114"
                className="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-[#C2542D]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300">Public Key (Khóa Công Khai):</label>
              <input
                type="password"
                value={publicKey}
                onChange={(e) => setPublicKey(e.target.value)}
                placeholder="Nhập Public Key để xác thực kết nối..."
                className="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-[#C2542D]"
              />
            </div>
          </div>
        </div>

        <div className="flex flex-col-reverse sm:flex-row sm:items-center sm:justify-between gap-3 pt-2">
          {isSaved ? (
            <div className="flex items-center gap-2 text-emerald-400 text-sm font-semibold animate-in fade-in">
              <Check className="w-4 h-4" />
              Đã lưu cấu hình RustDesk thành công!
            </div>
          ) : (
            <div />
          )}
          <button
            type="submit"
            disabled={loading}
            className="gradient-btn w-full sm:w-auto px-6 py-2.5 rounded-xl text-sm font-bold flex items-center justify-center gap-2 cursor-pointer"
          >
            <Save className="w-4 h-4" />
            {loading ? "Đang lưu..." : "Lưu Cấu Hình RustDesk"}
          </button>
        </div>
      </form>
    </div>
  );
}
