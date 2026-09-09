"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Menu, MonitorPlay } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { useAuthStore } from "@/stores/useAuthStore";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isLoginPage = pathname
    ? pathname === "/login" || pathname === "/login/" || pathname.startsWith("/login")
    : false;

  useEffect(() => {
    if (!isAuthenticated) {
      if (!isLoginPage) {
        router.replace("/login");
      }
    } else {
      if (isLoginPage) {
        router.replace("/");
      }
    }
  }, [isAuthenticated, isLoginPage, router]);

  // Tu dong dong mobile menu khi doi route
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  // Loading: Zustand chua hydrate xong (chi xay ra trong mot frame dau tien)
  if (isAuthenticated === null || (typeof isAuthenticated === "undefined")) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-[#0f1117] text-zinc-400 font-medium text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-[#C2542D] border-t-transparent rounded-full animate-spin" />
          Dang xac thuc bao mat...
        </div>
      </div>
    );
  }

  // Trang login: luon render form login
  if (isLoginPage) {
    return <main className="flex-1 w-full min-h-screen flex items-center justify-center">{children}</main>;
  }

  // Chua dang nhap
  if (!isAuthenticated) {
    return null;
  }

  // Da dang nhap -> Render Mobile Header + Sidebar (Desktop & Mobile Drawer) + noi dung
  return (
    <div className="flex flex-col md:flex-row min-h-screen w-full">
      {/* Mobile Top Header */}
      <header className="md:hidden sticky top-0 z-40 flex items-center justify-between px-4 py-3 bg-[#0f1117]/95 backdrop-blur-md border-b border-[var(--vc-border)]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-gradient-to-br from-[#C2542D] to-[#C99A45] shadow-md shadow-[#C2542D]/20">
            <MonitorPlay className="w-4 h-4 text-white" />
          </div>
          <span className="font-extrabold text-sm gradient-text">VideoCrew Studio</span>
        </div>
        <button
          type="button"
          onClick={() => setMobileMenuOpen(true)}
          className="p-2 rounded-xl text-zinc-300 hover:text-white bg-white/[0.05] hover:bg-white/[0.1] border border-white/5 transition"
          aria-label="Mo menu"
        >
          <Menu className="w-5 h-5" />
        </button>
      </header>

      <Sidebar mobileOpen={mobileMenuOpen} onCloseMobile={() => setMobileMenuOpen(false)} />
      <main className="flex-1 p-3.5 sm:p-5 md:p-8 overflow-y-auto max-w-7xl mx-auto w-full">{children}</main>
    </div>
  );
}
