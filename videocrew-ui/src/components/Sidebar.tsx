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
  PanelLeft,
  X
} from "lucide-react";
import { useState, useEffect } from "react";
import { useAuthStore } from "@/stores/useAuthStore";

interface SidebarProps {
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export function Sidebar({ mobileOpen = false, onCloseMobile }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { user: currentUser, isAuthenticated, logout } = useAuthStore();
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  useEffect(() => {
    try {
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
    logout();
    if (onCloseMobile) onCloseMobile();
    window.location.href = "/login";
  };

  const handleNavClick = () => {
    if (onCloseMobile) onCloseMobile();
  };

  const navItems = [
    { href: "/", label: "Tổng Quan Studio", icon: BarChart3 },
    { href: "/production", label: "Sản Xuất Video", icon: Film, badge: "Live" },
    { href: "/channels", label: "Kênh Phân Phối", icon: Layers },
    { href: "/config", label: "Thiết Lập Studio & Model AI", icon: Settings },
    { href: "/analytics", label: "Hiệu Suất Nội Dung", icon: BarChart3 },
    { href: "/ip-manager", label: "Bảo Mật & Phân Quyền", icon: ShieldCheck },
    { href: "/rustdesk", label: "Trạm Dựng Phim Từ Xa", icon: Monitor },
  ];

  const renderNavContent = (collapsed: boolean, isMobile: boolean = false) => (
    <>
      <div>
        <div className={`flex ${collapsed && !isMobile ? "flex-col items-center gap-2.5" : "items-center justify-between"} pb-4 mb-4 border-b border-[var(--vc-border)]`}>
          <div className={`flex items-center ${collapsed && !isMobile ? "justify-center" : "gap-3"} overflow-hidden`}>
            <div className="w-10 h-10 min-w-[40px] rounded-xl flex items-center justify-center bg-gradient-to-br from-[#C2542D] to-[#C99A45] shadow-lg shadow-[#C2542D]/20">
              <MonitorPlay className="w-5 h-5 text-white" />
            </div>
            {(!collapsed || isMobile) && (
              <div className="truncate">
                <h1 className="font-extrabold text-base leading-tight gradient-text truncate">
                  VideoCrew
                </h1>
                <span className="text-[11px] text-[var(--vc-muted)] font-medium">Studio v2.0</span>
              </div>
            )}
          </div>

          {isMobile ? (
            <button
              type="button"
              onClick={onCloseMobile}
              className="p-2 rounded-lg text-zinc-400 hover:text-white hover:bg-white/[0.06] transition"
            >
              <X className="w-5 h-5" />
            </button>
          ) : (
            <button
              type="button"
              onClick={toggleCollapse}
              title={collapsed ? "Mở rộng Sidebar" : "Thu gọn Sidebar"}
              className={`p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/[0.06] transition ${
                collapsed && !isMobile ? "mt-1 w-8 h-8 flex items-center justify-center bg-white/[0.04]" : ""
              }`}
            >
              {collapsed ? <PanelLeft className="w-4 h-4 text-amber-400" /> : <PanelLeftClose className="w-4 h-4 text-zinc-400" />}
            </button>
          )}
        </div>

        {/* Navigation Menu */}
        <nav className="space-y-1">
          {(!collapsed || isMobile) && (
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
                onClick={handleNavClick}
                title={collapsed && !isMobile ? item.label : undefined}
                className={`flex items-center ${
                  collapsed && !isMobile ? "justify-center px-2" : "justify-between px-3"
                } py-2.5 rounded-xl font-medium text-xs transition-all duration-200 ${
                  isActive
                    ? "bg-[var(--vc-accent-soft)] text-[#C2542D] border border-[var(--vc-accent-soft-strong)] shadow-sm font-bold"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]"
                }`}
              >
                <div className={`flex items-center ${collapsed && !isMobile ? "justify-center" : "gap-2.5"} truncate`}>
                  <Icon className={`w-4 h-4 min-w-[16px] ${isActive ? "text-[#C2542D]" : "text-zinc-400"}`} />
                  {(!collapsed || isMobile) && <span className="truncate">{item.label}</span>}
                </div>
                {(!collapsed || isMobile) && item.badge && (
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
        <div className={`glass-panel ${collapsed && !isMobile ? "p-2 text-center" : "p-3"} border-[var(--vc-border)]`}>
          <div className={`flex items-center ${collapsed && !isMobile ? "justify-center" : "justify-between"} mb-1`}>
            <span className="text-[11px] font-semibold text-zinc-300 flex items-center gap-1.5">
              <Radio className="w-3 h-3 text-emerald-400 animate-ping" />
              {(!collapsed || isMobile) && "Trạm Làm Phim"}
            </span>
            {(!collapsed || isMobile) && <span className="vc-badge text-[9px] py-0 px-1.5 text-emerald-400 border-emerald-500/20 bg-emerald-500/10">Sẵn Sàng</span>}
          </div>
          {(!collapsed || isMobile) && (
            <div className="text-[10px] text-[var(--vc-muted)] space-y-0.5 border-t border-[var(--vc-border)] pt-1.5 mt-1">
              <div className="flex justify-between items-center">
                <span>Nhà sáng tạo:</span>
                <span className="font-semibold text-zinc-200 truncate ml-1">
                  {currentUser?.username || "Studio Creator"}
                </span>
              </div>
            </div>
          )}
        </div>

        {isAuthenticated ? (
          <button
            onClick={handleLogout}
            title={collapsed && !isMobile ? "Đăng Xuất" : undefined}
            className={`w-full flex items-center ${
              collapsed && !isMobile ? "justify-center p-2" : "justify-center gap-2 py-2"
            } rounded-xl text-xs font-semibold text-zinc-400 hover:text-red-400 bg-white/[0.03] hover:bg-red-500/10 border border-white/5 transition`}
          >
            <LogOut className="w-3.5 h-3.5" />
            {(!collapsed || isMobile) && "Đăng Xuất"}
          </button>
        ) : (
          <button
            type="button"
            onClick={handleLogout}
            title={collapsed && !isMobile ? "Đăng Nhập" : undefined}
            className={`w-full flex items-center ${
              collapsed && !isMobile ? "justify-center p-2" : "justify-center gap-2 py-2"
            } rounded-xl text-xs font-semibold text-zinc-300 hover:text-white bg-white/[0.05] hover:bg-white/[0.08] border border-white/10 transition`}
          >
            <LogIn className="w-3.5 h-3.5 text-[#C2542D]" />
            {(!collapsed || isMobile) && "Đăng Nhập"}
          </button>
        )}
      </div>
    </>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside className={`hidden md:flex border-r border-[var(--vc-border)] bg-[var(--vc-card-bg)] backdrop-blur-xl flex-col justify-between p-3 min-h-screen sticky top-0 transition-all duration-300 ${
        isCollapsed ? "w-20" : "w-64"
      }`}>
        {renderNavContent(isCollapsed, false)}
      </aside>

      {/* Mobile Drawer Overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex animate-in fade-in duration-200">
          <div
            className="fixed inset-0 bg-black/75 backdrop-blur-sm transition-opacity"
            onClick={onCloseMobile}
          />
          <aside className="relative z-10 w-72 max-w-[85vw] bg-[#12141c] border-r border-[var(--vc-border)] p-4 flex flex-col justify-between h-full shadow-2xl overflow-y-auto">
            {renderNavContent(false, true)}
          </aside>
        </div>
      )}
    </>
  );
}
