"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { useAuthStore } from "@/stores/useAuthStore";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();

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

  // Da dang nhap -> Render Sidebar + noi dung
  return (
    <>
      <Sidebar />
      <main className="flex-1 p-8 overflow-y-auto max-w-7xl mx-auto w-full">{children}</main>
    </>
  );
}
