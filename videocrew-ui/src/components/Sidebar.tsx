"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { 
  Film, 
  Layers, 
  Settings, 
  BarChart3, 
  ShieldCheck, 
  MonitorPlay,
  Radio,
  Monitor,
  LogOut,
  LogIn,
  ChevronLeft,
  ChevronRight,
  PanelLeftClose,
  PanelLeft
} from "lucide-react";
import { useState, useEffect } from "react";

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("user");
      if (stored) setCurrentUser(JSON.parse(stored));
      const storedCollapsed = localStorage.getItem("sidebar_collapsed");
      if (storedCollapsed !== null) {
        setIsCollapsed(storedCollapsed === "true");
      }
    } catch (e) {}
  }, []);

  const toggleCollapse = () => {
    const next = !isCollapsed;
    setIsCollapsed(next);
    try {
      localStorage.setItem("sidebar_collapsed", String(next));
    } catch (e) {}
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    setCurrentUser(null);
    router.push("/login");
  };

  const navItems = [
    { href: "/", label: "Tổng quan (Dashboard)", icon: BarChart3 },
    { href: "/production", label: "Sản xuất Video AI", icon: Film, badge: "Live" },
    { href: "/channels", label: "Quản lý Kênh", icon: Layers },
    { href: "/config", label: "Cấu hình AI & Engine", icon: Settings },
    { href: "/analytics", label: "Phân tích Hiệu quả", icon: BarChart3 },
    { href: "/ip-manager", label: "Quản lý IP Admin", icon: ShieldCheck },
    { href: "/rustdesk", label: "Cấu hình RustDesk", icon: Monitor },
  ];

  return (
    <aside className={`border-r border-[var(--vc-border)] bg-[var(--vc-card-bg)] backdrop-blur-xl flex flex-col justify-between p-3 min-h-screen sticky top-0 transition-all duration-300 ${
      isCollapsed ? "w-20" : "w-64"
    }`}>
      {/* Brand Header & Toggle */}
      <div>
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-[var(--vc-border)]">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-10 h-10 min-w-[40px] rounded-xl flex items-center justify-center bg-gradient-to-br from-[#C2542D] to-[#C99A45] shadow-lg shadow-[#C2542D]/20">
              <MonitorPlay className="w-5 h-5 text-white" />
            </div>
            {!isCollapsed && (
              <div className="truncate">
                <h1 className="font-extrabold text-base leading-tight gradient-text truncate">
                  VideoCrew
                </h1>
                <span className="text-[11px] text-[var(--vc-muted)] font-medium">Studio v2.0 Next.js</span>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={toggleCollapse}
            title={isCollapsed ? "Mở rộng Sidebar" : "Thu gọn Sidebar"}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/[0.06] transition"
          >
            {isCollapsed ? <PanelLeft className="w-4 h-4 text-amber-400" /> : <PanelLeftClose className="w-4 h-4 text-zinc-400" />}
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="space-y-1">
          {!isCollapsed && (
            <div className="text-[10px] uppercase font-bold tracking-wider text-[var(--vc-muted)] px-3 mb-2">
              Menu Điều Hướng
            </div>
          )}
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                title={isCollapsed ? item.label : undefined}
                className={`flex items-center ${
                  isCollapsed ? "justify-center px-2" : "justify-between px-3"
                } py-2.5 rounded-xl font-medium text-xs transition-all duration-200 ${
                  isActive
                    ? "bg-[var(--vc-accent-soft)] text-[#C2542D] border border-[var(--vc-accent-soft-strong)] shadow-sm font-bold"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]"
                }`}
              >
                <div className={`flex items-center ${isCollapsed ? "justify-center" : "gap-2.5"} truncate`}>
                  <Icon className={`w-4 h-4 min-w-[16px] ${isActive ? "text-[#C2542D]" : "text-zinc-400"}`} />
                  {!isCollapsed && <span className="truncate">{item.label}</span>}
                </div>
                {!isCollapsed && item.badge && (
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-[#C2542D] text-white animate-pulse">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Account / Engine Status Card */}
      <div className="space-y-2.5 mt-4">
        <div className={`glass-panel ${isCollapsed ? "p-2 text-center" : "p-3"} border-[var(--vc-border)]`}>
          <div className={`flex items-center ${isCollapsed ? "justify-center" : "justify-between"} mb-1`}>
            <span className="text-[11px] font-semibold text-zinc-300 flex items-center gap-1.5">
              <Radio className="w-3 h-3 text-emerald-400 animate-ping" />
              {!isCollapsed && "DidicrewStudio"}
            </span>
            {!isCollapsed && <span className="vc-badge text-[9px] py-0 px-1.5">Online</span>}
          </div>
          {!isCollapsed && (
            <div className="text-[10px] text-[var(--vc-muted)] space-y-0.5 border-t border-[var(--vc-border)] pt-1.5 mt-1">
              <div className="flex justify-between">
                <span>Người dùng:</span>
                <span className="font-semibold text-zinc-200 truncate ml-1">
                  {currentUser?.username || "Didicrew07"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Client IP:</span>
                <span className="font-mono text-zinc-300">127.0.0.1</span>
              </div>
            </div>
          )}
        </div>

        {currentUser ? (
          <button
            onClick={handleLogout}
            title={isCollapsed ? "Đăng Xuất" : undefined}
            className={`w-full flex items-center ${
              isCollapsed ? "justify-center p-2" : "justify-center gap-2 py-2"
            } rounded-xl text-xs font-semibold text-zinc-400 hover:text-red-400 bg-white/[0.03] hover:bg-red-500/10 border border-white/5 transition`}
          >
            <LogOut className="w-3.5 h-3.5" />
            {!isCollapsed && "Đăng Xuất"}
          </button>
        ) : (
          <Link
            href="/login"
            title={isCollapsed ? "Đăng Nhập" : undefined}
            className={`w-full flex items-center ${
              isCollapsed ? "justify-center p-2" : "justify-center gap-2 py-2"
            } rounded-xl text-xs font-semibold text-zinc-300 hover:text-white bg-white/[0.05] hover:bg-white/[0.08] border border-white/10 transition`}
          >
            <LogIn className="w-3.5 h-3.5 text-[#C2542D]" />
            {!isCollapsed && "Đăng Nhập"}
          </Link>
        )}
      </div>
    </aside>
  );
}
