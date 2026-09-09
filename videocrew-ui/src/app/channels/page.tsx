"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useChannelStore } from "@/stores/useChannelStore";
import { useProductionStore } from "@/stores/useProductionStore";
import { Layers, Plus, Trash2, Edit3, Target, Info, Search, Video, Sparkles, X, Check } from "lucide-react";

export default function ChannelsPage() {
  const router = useRouter();
  const { channels, isLoading, createChannel, updateChannel, deleteChannel, setSelectedChannelId } = useChannelStore();
  const { resetProduction } = useProductionStore();

  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingChannel, setEditingChannel] = useState<{ id: number; name: string; description: string; goal: string } | null>(null);

  // Form states for Create
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [goal, setGoal] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Form states for Edit
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editGoal, setEditGoal] = useState("");
  const [editSubmitting, setEditSubmitting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !goal.trim()) {
      alert("Tên kênh và Mục tiêu không được để trống!");
      return;
    }
    setSubmitting(true);
    try {
      await createChannel({ name, description, goal });
      setName("");
      setDescription("");
      setGoal("");
      setShowCreateModal(false);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleOpenEdit = (ch: any) => {
    setEditingChannel(ch);
    setEditName(ch.name);
    setEditDescription(ch.description || "");
    setEditGoal(ch.goal || "");
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingChannel) return;
    if (!editName.trim() || !editGoal.trim()) {
      alert("Tên kênh và Mục tiêu không được để trống!");
      return;
    }
    setEditSubmitting(true);
    try {
      await updateChannel(editingChannel.id, {
        name: editName,
        description: editDescription,
        goal: editGoal,
      });
      setEditingChannel(null);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setEditSubmitting(false);
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (confirm(`Bạn có chắc chắn muốn xóa kênh "${name}"? Toàn bộ cấu hình của kênh sẽ bị xóa.`)) {
      await deleteChannel(id);
    }
  };

  const handleGoToProduction = (channelId: number) => {
    setSelectedChannelId(channelId);
    resetProduction();
    router.push("/production");
  };

  const filteredChannels = channels.filter((c) =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (c.description && c.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (c.goal && c.goal.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold flex items-center gap-2.5">
            <Layers className="w-7 h-7 text-[#C2542D]" />
            Quản Lý Kênh Video
          </h1>
          <p className="text-sm text-[var(--vc-muted)] mt-1">
            Thiết lập danh mục các kênh YouTube, TikTok, Facebook Reels và định hướng nội dung AI.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="gradient-btn px-4 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 cursor-pointer self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          Thêm Kênh Mới
        </button>
      </div>

      {/* Search Bar */}
      <div className="glass-panel p-3 rounded-2xl border border-[var(--vc-border)] flex items-center gap-3">
        <Search className="w-4 h-4 text-zinc-400 ml-2" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Tìm kiếm kênh theo tên, mô tả hoặc mục tiêu nội dung..."
          className="bg-transparent flex-1 text-sm text-zinc-200 outline-none placeholder:text-zinc-500"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery("")}
            className="p-1 rounded-lg text-zinc-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Channels List Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredChannels.map((ch) => (
          <div key={ch.id} className="glass-panel p-6 glass-panel-hover flex flex-col justify-between space-y-4 rounded-2xl border border-[var(--vc-border)]">
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-amber-500/20 to-orange-600/20 border border-amber-500/30 flex items-center justify-center text-amber-400 font-extrabold text-lg shadow-lg shadow-amber-500/5">
                  {ch.name.charAt(0).toUpperCase()}
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleOpenEdit(ch)}
                    className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/[0.08] transition"
                    title="Chỉnh sửa kênh"
                  >
                    <Edit3 className="w-4 h-4 text-zinc-400 hover:text-amber-400" />
                  </button>
                  <button
                    onClick={() => handleDelete(ch.id, ch.name)}
                    className="p-1.5 rounded-lg text-zinc-400 hover:text-red-400 hover:bg-red-500/10 transition"
                    title="Xóa kênh"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div>
                <h3 className="text-base font-bold text-zinc-100">{ch.name}</h3>
                {ch.description ? (
                  <p className="text-xs text-[var(--vc-muted)] mt-1 line-clamp-2">
                    {ch.description}
                  </p>
                ) : (
                  <p className="text-xs text-zinc-600 italic mt-1">Chưa có mô tả chi tiết</p>
                )}
              </div>

              <div className="p-3.5 rounded-xl bg-black/40 border border-white/5 space-y-1.5">
                <div className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
                  <Target className="w-3.5 h-3.5 text-amber-400" />
                  Mục tiêu nội dung
                </div>
                <div className="text-xs text-zinc-200 font-medium leading-relaxed">{ch.goal}</div>
              </div>
            </div>

            <div className="space-y-3 pt-2 border-t border-[var(--vc-border)]">
              <div className="text-[11px] text-zinc-500 flex justify-between">
                <span>Ngày tạo:</span>
                <span className="font-mono text-zinc-400">{new Date(ch.created_at).toLocaleDateString("vi-VN")}</span>
              </div>

              <button
                type="button"
                onClick={() => handleGoToProduction(ch.id)}
                className="w-full py-2 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-400 text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-sm"
              >
                <Video className="w-3.5 h-3.5" />
                Sản Xuất Video Với Kênh Này
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredChannels.length === 0 && (
        <div className="py-16 text-center space-y-3 glass-panel rounded-2xl border border-[var(--vc-border)]">
          <Layers className="w-10 h-10 text-zinc-600 mx-auto" />
          <h3 className="text-sm font-bold text-zinc-400">Không tìm thấy kênh nào</h3>
          <p className="text-xs text-zinc-500 max-w-sm mx-auto">
            {searchQuery ? "Không có kênh nào khớp với từ khóa tìm kiếm." : "Hãy bắt đầu bằng cách bấm Thêm Kênh Mới để quản lý nội dung video."}
          </p>
        </div>
      )}

      {/* Modal Add Channel */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel p-6 max-w-md w-full max-h-[90vh] overflow-y-auto border border-zinc-700 bg-zinc-950 rounded-2xl space-y-5 shadow-2xl animate-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Plus className="w-5 h-5 text-amber-400" />
                Thêm Kênh Sản Xuất Mới
              </h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 rounded-lg text-zinc-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-zinc-300">Tên Kênh (*):</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Ví dụ: Kênh Công Nghệ AI"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-amber-500 text-white"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-zinc-300">Mô Tả:</label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Mô tả ngắn gọn về ngách nội dung kênh"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-amber-500 text-white"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-zinc-300">Mục Tiêu Kênh (*):</label>
                <textarea
                  rows={3}
                  required
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="Ví dụ: Tạo video ngắn viral về xu hướng AI và công nghệ mới năm 2026"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-amber-500 text-white"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-zinc-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-zinc-400 hover:text-white"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="gradient-btn px-5 py-2 rounded-xl text-xs font-bold"
                >
                  {submitting ? "Đang lưu..." : "Tạo Kênh"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Edit Channel */}
      {editingChannel && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel p-6 max-w-md w-full max-h-[90vh] overflow-y-auto border border-zinc-700 bg-zinc-950 rounded-2xl space-y-5 shadow-2xl animate-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Edit3 className="w-5 h-5 text-amber-400" />
                Chỉnh Sửa Thông Tin Kênh
              </h2>
              <button
                onClick={() => setEditingChannel(null)}
                className="p-1 rounded-lg text-zinc-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleUpdate} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-zinc-300">Tên Kênh (*):</label>
                <input
                  type="text"
                  required
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-amber-500 text-white"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-zinc-300">Mô Tả:</label>
                <input
                  type="text"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-amber-500 text-white"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-zinc-300">Mục Tiêu Kênh (*):</label>
                <textarea
                  rows={3}
                  required
                  value={editGoal}
                  onChange={(e) => setEditGoal(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-[var(--vc-border)] text-sm focus:outline-none focus:border-amber-500 text-white"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-zinc-800">
                <button
                  type="button"
                  onClick={() => setEditingChannel(null)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-zinc-400 hover:text-white"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={editSubmitting}
                  className="gradient-btn px-5 py-2 rounded-xl text-xs font-bold"
                >
                  {editSubmitting ? "Đang lưu..." : "Lưu Thay Đổi"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
