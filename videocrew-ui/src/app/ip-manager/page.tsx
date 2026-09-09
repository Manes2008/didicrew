"use client";

import { useState, useEffect } from "react";
import { apiClient, AllowedIPItem } from "@/lib/api-client";
import { ShieldCheck, Check, X, Trash2, ShieldAlert, Laptop } from "lucide-react";

export default function IPManagerPage() {
  const [ips, setIps] = useState<AllowedIPItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchIPs = () => {
    apiClient.getIPList()
      .then(setIps)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchIPs();
  }, []);

  const handleUpdateStatus = async (id: number, status: string, is_admin?: boolean) => {
    try {
      await apiClient.updateIP(id, status, is_admin);
      fetchIPs();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm("Bạn có chắc chắn muốn xóa địa chỉ IP này?")) {
      await apiClient.deleteIP(id);
      fetchIPs();
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300 max-w-5xl">
      <div>
        <h1 className="text-2xl font-extrabold flex items-center gap-2.5">
          <ShieldCheck className="w-7 h-7 text-[#C2542D]" />
          Quản Lý IP Truy Cập & Phân Quyền Admin
        </h1>
        <p className="text-sm text-[var(--vc-muted)] mt-1">
          Kiểm soát danh sách thiết bị/IP được phép truy cập vào hệ thống sản xuất và gán quyền quản trị viên.
        </p>
      </div>

      <div className="glass-panel p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-[var(--vc-border)] pb-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
            <Laptop className="w-4 h-4 text-[#C99A45]" />
            Danh Sách Thiết Bị & Địa Chỉ IP Đã Ghi Nhận ({ips.length})
          </h2>
          <button
            onClick={fetchIPs}
            className="text-xs text-[#C2542D] hover:underline font-semibold"
          >
            Làm mới danh sách
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[var(--vc-border)] text-[var(--vc-muted)]">
                <th className="py-3 px-3">Địa chỉ IP</th>
                <th className="py-3 px-3">Thiết bị / Ghi chú</th>
                <th className="py-3 px-3">Trạng thái</th>
                <th className="py-3 px-3">Quyền Admin</th>
                <th className="py-3 px-3">Thời gian tạo</th>
                <th className="py-3 px-3 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--vc-border)] text-zinc-300">
              {ips.length > 0 ? (
                ips.map((item) => (
                  <tr key={item.id} className="hover:bg-white/[0.02]">
                    <td className="py-3 px-3 font-mono font-bold text-white">{item.ip_address}</td>
                    <td className="py-3 px-3 text-zinc-400">{item.label || "Không có tên"}</td>
                    <td className="py-3 px-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          item.status === "approved"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : item.status === "pending"
                            ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                            : "bg-red-500/10 text-red-400 border border-red-500/20"
                        }`}
                      >
                        {item.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <button
                        onClick={() => handleUpdateStatus(item.id, item.status, !item.is_admin_ip)}
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-md cursor-pointer transition ${
                          item.is_admin_ip
                            ? "bg-[#C2542D] text-white"
                            : "bg-white/5 text-zinc-400 hover:text-white"
                        }`}
                      >
                        {item.is_admin_ip ? "Admin IP" : "User IP"}
                      </button>
                    </td>
                    <td className="py-3 px-3 text-zinc-500">
                      {new Date(item.created_at).toLocaleDateString("vi-VN")}
                    </td>
                    <td className="py-3 px-3 text-right space-x-2">
                      {item.status !== "approved" && (
                        <button
                          onClick={() => handleUpdateStatus(item.id, "approved")}
                          className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"
                          title="Phê duyệt IP"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                      )}
                      {item.status !== "rejected" && (
                        <button
                          onClick={() => handleUpdateStatus(item.id, "rejected")}
                          className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400 hover:bg-amber-500/20"
                          title="Từ chối IP"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="p-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20"
                        title="Xóa IP"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-zinc-600 italic">
                    Chưa có địa chỉ IP nào trong danh sách.
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
