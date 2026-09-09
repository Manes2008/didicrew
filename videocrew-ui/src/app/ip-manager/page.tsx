"use client";

import { useState, useEffect } from "react";
import { apiClient, AllowedIPItem } from "@/lib/api-client";
import {
  ShieldCheck,
  Check,
  X,
  Trash2,
  Laptop,
  Globe,
  List,
  MapPin,
  Building2,
  Clock,
  Network,
  Loader2,
  ServerOff,
} from "lucide-react";

type GeoInfo = {
  country: string;
  countryCode: string;
  city: string;
  regionName: string;
  isp: string;
  org: string;
  timezone: string;
};

const PRIVATE_RANGES = ["127.", "10.", "192.168.", "::1", "localhost"];

function isPrivateIP(ip: string): boolean {
  return PRIVATE_RANGES.some((prefix) => ip.startsWith(prefix));
}

async function fetchGeoInfo(ip: string): Promise<GeoInfo | null> {
  if (isPrivateIP(ip)) return null;
  try {
    const res = await fetch(
      `http://ip-api.com/json/${ip}?fields=status,country,countryCode,regionName,city,isp,org,timezone`
    );
    const data = await res.json();
    if (data.status === "success") return data as GeoInfo;
    return null;
  } catch {
    return null;
  }
}

export default function IPManagerPage() {
  const [ips, setIps] = useState<AllowedIPItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<"raw" | "friendly">("raw");
  const [geoData, setGeoData] = useState<Record<string, GeoInfo | null>>({});
  const [geoLoading, setGeoLoading] = useState(false);

  const fetchIPs = () => {
    apiClient
      .getIPList()
      .then(setIps)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchIPs();
  }, []);

  const handleSwitchFriendly = async () => {
    setViewMode("friendly");
    if (Object.keys(geoData).length > 0) return;
    setGeoLoading(true);
    const results: Record<string, GeoInfo | null> = {};
    await Promise.all(
      ips.map(async (item) => {
        results[item.ip_address] = await fetchGeoInfo(item.ip_address);
      })
    );
    setGeoData(results);
    setGeoLoading(false);
  };

  const handleUpdateStatus = async (
    id: number,
    status: string,
    is_admin?: boolean
  ) => {
    try {
      await apiClient.updateIP(id, status, is_admin);
      fetchIPs();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm("Ban co chac chan muon xoa dia chi IP nay?")) {
      await apiClient.deleteIP(id);
      fetchIPs();
    }
  };

  const statusBadge = (status: string) => {
    const map: Record<string, string> = {
      approved: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",
      pending: "bg-amber-500/10 text-amber-400 border border-amber-500/20",
      rejected: "bg-red-500/10 text-red-400 border border-red-500/20",
    };
    return (
      <span
        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${
          map[status] || map.rejected
        }`}
      >
        {status.toUpperCase()}
      </span>
    );
  };

  const actionButtons = (item: AllowedIPItem) => (
    <div className="flex items-center gap-1.5 justify-end">
      {item.status !== "approved" && (
        <button
          onClick={() => handleUpdateStatus(item.id, "approved")}
          className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"
          title="Phe duyet IP"
        >
          <Check className="w-3.5 h-3.5" />
        </button>
      )}
      {item.status !== "rejected" && (
        <button
          onClick={() => handleUpdateStatus(item.id, "rejected")}
          className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400 hover:bg-amber-500/20"
          title="Tu choi IP"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
      <button
        onClick={() => handleDelete(item.id)}
        className="p-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20"
        title="Xoa IP"
      >
        <Trash2 className="w-3.5 h-3.5" />
      </button>
    </div>
  );

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in duration-300 max-w-5xl">
      <div>
        <h1 className="text-xl sm:text-2xl font-extrabold flex items-center gap-2.5">
          <ShieldCheck className="w-6 h-6 sm:w-7 sm:h-7 text-[#C2542D] shrink-0" />
          Quan Ly IP Truy Cap & Phan Quyen Admin
        </h1>
        <p className="text-sm text-[var(--vc-muted)] mt-1">
          Kiem soat danh sach thiet bi/IP duoc phep truy cap vao he thong san xuat va gan quyen quan tri vien.
        </p>
      </div>

      <div className="glass-panel p-4 sm:p-6 space-y-4">
        {/* Panel Header */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--vc-border)] pb-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
            <Laptop className="w-4 h-4 text-[#C99A45] shrink-0" />
            Danh Sach Thiet Bi & Dia Chi IP ({ips.length})
          </h2>

          <div className="flex items-center gap-2">
            {/* View Mode Toggle */}
            <div className="flex items-center rounded-xl overflow-hidden border border-[var(--vc-border)] text-xs font-semibold">
              <button
                onClick={() => setViewMode("raw")}
                className={`flex items-center gap-1.5 px-3 py-1.5 transition ${
                  viewMode === "raw"
                    ? "bg-[#C2542D] text-white"
                    : "bg-transparent text-zinc-400 hover:text-white"
                }`}
              >
                <List className="w-3.5 h-3.5" />
                Raw IP
              </button>
              <button
                onClick={handleSwitchFriendly}
                className={`flex items-center gap-1.5 px-3 py-1.5 transition ${
                  viewMode === "friendly"
                    ? "bg-[#C2542D] text-white"
                    : "bg-transparent text-zinc-400 hover:text-white"
                }`}
              >
                {geoLoading ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Globe className="w-3.5 h-3.5" />
                )}
                Than Thien
              </button>
            </div>

            <button
              onClick={fetchIPs}
              className="text-xs text-[#C2542D] hover:underline font-semibold"
            >
              Lam moi
            </button>
          </div>
        </div>

        {/* RAW VIEW */}
        {viewMode === "raw" && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs min-w-[620px]">
              <thead>
                <tr className="border-b border-[var(--vc-border)] text-[var(--vc-muted)]">
                  <th className="py-3 px-3">Dia chi IP</th>
                  <th className="py-3 px-3">Thiet bi / Ghi chu</th>
                  <th className="py-3 px-3">Trang thai</th>
                  <th className="py-3 px-3">Quyen Admin</th>
                  <th className="py-3 px-3">Thoi gian tao</th>
                  <th className="py-3 px-3 text-right">Thao tac</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--vc-border)] text-zinc-300">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-zinc-600">
                      <Loader2 className="w-5 h-5 animate-spin mx-auto" />
                    </td>
                  </tr>
                ) : ips.length > 0 ? (
                  ips.map((item) => (
                    <tr key={item.id} className="hover:bg-white/[0.02]">
                      <td className="py-3 px-3 font-mono font-bold text-white">
                        {item.ip_address}
                      </td>
                      <td className="py-3 px-3 text-zinc-400">
                        {item.label || "Khong co ten"}
                      </td>
                      <td className="py-3 px-3">{statusBadge(item.status)}</td>
                      <td className="py-3 px-3">
                        <button
                          onClick={() =>
                            handleUpdateStatus(item.id, item.status, !item.is_admin_ip)
                          }
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
                      <td className="py-3 px-3 text-right">
                        {actionButtons(item)}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan={6}
                      className="py-8 text-center text-zinc-600 italic"
                    >
                      Chua co dia chi IP nao trong danh sach.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* FRIENDLY VIEW */}
        {viewMode === "friendly" && (
          <div className="space-y-3">
            {geoLoading ? (
              <div className="flex items-center justify-center gap-2 py-10 text-zinc-500 text-sm">
                <Loader2 className="w-5 h-5 animate-spin" />
                Dang tai thong tin dia ly...
              </div>
            ) : ips.length === 0 ? (
              <div className="py-10 text-center text-zinc-600 italic text-sm">
                Chua co dia chi IP nao trong danh sach.
              </div>
            ) : (
              ips.map((item) => {
                const geo = geoData[item.ip_address];
                const isPrivate = isPrivateIP(item.ip_address);
                return (
                  <div
                    key={item.id}
                    className="rounded-xl border border-[var(--vc-border)] bg-zinc-950/50 p-4 hover:border-zinc-600 transition"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      {/* Left: IP Info */}
                      <div className="space-y-2 min-w-0">
                        {/* IP + Label Row */}
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-mono font-bold text-white text-sm">
                            {item.ip_address}
                          </span>
                          {statusBadge(item.status)}
                          <button
                            onClick={() =>
                              handleUpdateStatus(item.id, item.status, !item.is_admin_ip)
                            }
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-md cursor-pointer transition ${
                              item.is_admin_ip
                                ? "bg-[#C2542D] text-white"
                                : "bg-white/5 text-zinc-400 hover:text-white"
                            }`}
                          >
                            {item.is_admin_ip ? "Admin IP" : "User IP"}
                          </button>
                        </div>

                        {/* Device Label */}
                        <div className="flex items-center gap-1.5 text-xs text-zinc-400">
                          <Laptop className="w-3.5 h-3.5 shrink-0 text-[#C99A45]" />
                          <span>{item.label || "Khong co ten thiet bi"}</span>
                        </div>

                        {/* Geo Info */}
                        {isPrivate ? (
                          <div className="flex items-center gap-1.5 text-xs text-zinc-500">
                            <ServerOff className="w-3.5 h-3.5 shrink-0" />
                            <span>Noi bo / Localhost</span>
                          </div>
                        ) : geo ? (
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-xs text-zinc-400 pt-1">
                            <div className="flex items-center gap-1.5">
                              <MapPin className="w-3.5 h-3.5 shrink-0 text-[#C2542D]" />
                              <span>
                                {geo.city}, {geo.regionName}, {geo.country}
                              </span>
                            </div>
                            <div className="flex items-center gap-1.5">
                              <Building2 className="w-3.5 h-3.5 shrink-0 text-[#C99A45]" />
                              <span className="truncate">{geo.isp || geo.org}</span>
                            </div>
                            <div className="flex items-center gap-1.5">
                              <Clock className="w-3.5 h-3.5 shrink-0 text-zinc-500" />
                              <span>{geo.timezone}</span>
                            </div>
                            <div className="flex items-center gap-1.5">
                              <Network className="w-3.5 h-3.5 shrink-0 text-zinc-500" />
                              <span>
                                {new Date(item.created_at).toLocaleString("vi-VN")}
                              </span>
                            </div>
                          </div>
                        ) : (
                          <div className="flex items-center gap-1.5 text-xs text-zinc-600">
                            <Globe className="w-3.5 h-3.5 shrink-0" />
                            <span>Khong the tra cuu vi tri dia ly</span>
                          </div>
                        )}
                      </div>

                      {/* Right: Actions */}
                      <div className="shrink-0">{actionButtons(item)}</div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </div>
  );
}
