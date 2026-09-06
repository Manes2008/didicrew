"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/useAuthStore";
import { 
  Film, 
  Sparkles, 
  Lock, 
  User, 
  ShieldCheck, 
  ArrowRight, 
  Cpu, 
  Flame
} from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login, register } = useAuthStore();
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [deviceLabel, setDeviceLabel] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isRegister) {
        await register(username, password, deviceLabel);
        alert("Dang ky thanh cong! Vui long dang nhap voi tai khoan moi.");
        setIsRegister(false);
      } else {
        await login(username.trim(), password.trim());
        router.push("/");
      }
    } catch (err: any) {
      setError(err.message || "Tên đăng nhập hoặc mật khẩu / Admin Key không chính xác");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 lg:p-8 bg-studio-grid relative overflow-hidden">
      {/* Dynamic Ambient Background Glows */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[#FF5E1E]/15 rounded-full blur-[130px] pointer-events-none -z-10 animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-[450px] h-[450px] bg-[#FFAA00]/10 rounded-full blur-[120px] pointer-events-none -z-10" />

      {/* Main Studio Container */}
      <div className="max-w-5xl w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* Left Column: AI Studio Showcase */}
        <div className="lg:col-span-7 space-y-6 text-left">
          <div className="space-y-4">
            <div className="vc-badge">
              <Sparkles className="w-3.5 h-3.5 text-[#FF5E1E]" />
              VideoCrew Studio AI • Next-Gen Generative Suite
            </div>
            <h1 className="text-4xl lg:text-5xl font-black tracking-tight leading-[1.15]">
              Sản Xuất Video AI <br />
              <span className="gradient-text">Đa Kênh Tự Động</span>
            </h1>
            <p className="text-[var(--vc-muted)] text-sm lg:text-base leading-relaxed max-w-lg">
              Hệ thống đa tác nhân CrewAI tự động hóa từ viết kịch bản, vẽ phân cảnh, lồng tiếng tới dựng video theo thời gian thực.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3.5 pt-2">
            <div className="glass-panel p-4 glass-panel-hover border-white/5 space-y-2">
              <div className="w-8 h-8 rounded-lg bg-[#FF5E1E]/10 flex items-center justify-center text-[#FF5E1E]">
                <Cpu className="w-4 h-4" />
              </div>
              <h3 className="text-xs font-bold text-zinc-200">5-Stage AI Pipeline</h3>
              <p className="text-[11px] text-[var(--vc-muted)] leading-normal">
                Brief, Kịch bản, Render ảnh SDXL/Flux và ghép video tự động.
              </p>
            </div>

            <div className="glass-panel p-4 glass-panel-hover border-white/5 space-y-2">
              <div className="w-8 h-8 rounded-lg bg-[#FFAA00]/10 flex items-center justify-center text-[#FFAA00]">
                <Flame className="w-4 h-4" />
              </div>
              <h3 className="text-xs font-bold text-zinc-200">WebSocket Live Stream</h3>
              <p className="text-[11px] text-[var(--vc-muted)] leading-normal">
                Theo dõi tiến độ và logs thực thi từng giây không độ trễ.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-zinc-400">
            <span className="text-[var(--vc-muted)] font-semibold">Tích hợp sẵn:</span>
            <span className="px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/10 font-mono">Hunyuan Video</span>
            <span className="px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/10 font-mono">Flux.1</span>
            <span className="px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/10 font-mono">OpenAI GPT-4o</span>
            <span className="px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/10 font-mono">Gemini 1.5</span>
          </div>
        </div>

        {/* Right Column: High-End Glassmorphism Auth Card */}
        <div className="lg:col-span-5">
          <div className="glass-panel-glow p-7 lg:p-8 space-y-5 relative rounded-3xl">
            {/* Header Badge */}
            <div className="text-center space-y-2">
              <div className="w-12 h-12 mx-auto rounded-2xl flex items-center justify-center bg-gradient-to-br from-[#FF5E1E] to-[#FFAA00] shadow-lg shadow-[#FF5E1E]/30">
                <Film className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-xl font-extrabold text-white">
                {isRegister ? "Đăng Ký Tài Khoản" : "Đăng Nhập Studio"}
              </h2>
              <p className="text-xs text-[var(--vc-muted)]">
                {isRegister ? "Khởi tạo quyền truy cập hệ thống" : "Nhập User + Pass hoặc dán Admin Secret Key vào ô Mật khẩu"}
              </p>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold text-center animate-in fade-in">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-zinc-300 flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5 text-[#FF5E1E]" />
                  Tên Đăng Nhập:
                </label>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Nhập username hoặc tên bất kỳ..."
                  className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-[var(--vc-border)] text-sm text-zinc-100 focus:outline-none focus:border-[#FF5E1E] focus:ring-2 focus:ring-[#FF5E1E]/20 transition"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-zinc-300 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Lock className="w-3.5 h-3.5 text-[#FFAA00]" />
                    Mật Khẩu hoặc Admin Key:
                  </span>
                </label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Nhập mật khẩu hoặc dán ADMIN_SECRET_KEY..."
                  className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-[var(--vc-border)] text-sm text-zinc-100 focus:outline-none focus:border-[#FF5E1E] focus:ring-2 focus:ring-[#FF5E1E]/20 transition"
                />
              </div>

              {isRegister && (
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-zinc-300 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                    Tên Thiết Bị (Device Label):
                  </label>
                  <input
                    type="text"
                    value={deviceLabel}
                    onChange={(e) => setDeviceLabel(e.target.value)}
                    placeholder="Ví dụ: Laptop cá nhân..."
                    className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-[var(--vc-border)] text-sm text-zinc-100 focus:outline-none focus:border-[#FF5E1E] focus:ring-2 focus:ring-[#FF5E1E]/20 transition"
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full gradient-btn py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 cursor-pointer mt-2 disabled:opacity-50"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    {isRegister ? "Đăng Ký Tài Khoản" : "Vào Studio Sản Xuất"}
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            <div className="text-center pt-2 border-t border-[var(--vc-border)]">
              <button
                type="button"
                onClick={() => {
                  setIsRegister(!isRegister);
                  setError("");
                }}
                className="text-xs text-[var(--vc-muted)] hover:text-white transition font-medium"
              >
                {isRegister ? "Đã có tài khoản? Đăng nhập ngay" : "Chưa có tài khoản? Tạo tài khoản mới"}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
