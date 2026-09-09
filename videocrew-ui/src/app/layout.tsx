import type { Metadata } from "next";
import "./globals.css";
import { AuthGuard } from "@/components/AuthGuard";
import { AppInitializer } from "@/components/AppInitializer";

export const metadata: Metadata = {
  title: "VideoCrew Studio - AI Video Automation",
  description: "Hệ thống tự động hóa sản xuất video đa nền tảng bằng AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className="dark" suppressHydrationWarning>
      <body className="flex min-h-screen bg-[#0f1117] text-[#f0f2f5] antialiased" suppressHydrationWarning>
        <AppInitializer />
        <AuthGuard>{children}</AuthGuard>
      </body>
    </html>
  );
}
