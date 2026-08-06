# host_agent.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os
import threading
import subprocess
import glob
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Thêm thư mục hiện tại vào sys.path để import computer_control
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.tools.computer_control import computer_control

class HostControlHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/control":
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                params = json.loads(post_data.decode('utf-8'))
                
                print(f"[HostAgent] Nhận yêu cầu từ API: {params}")
                
                # Chạy computer_control cục bộ trên Windows Host
                result = computer_control(params)
                
                # Trả về kết quả JSON
                response_data = json.dumps({"success": True, "result": result}, ensure_ascii=False)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(response_data.encode('utf-8'))
            except Exception as e:
                print(f"[HostAgent] Lỗi API: {e}")
                response_data = json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(response_data.encode('utf-8'))
        elif self.path == "/sync_project":
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data.decode('utf-8'))
                
                project_id = payload.get("project_id")
                files = payload.get("files", []) # Danh sách các file: {"name": ..., "content_type": ..., "data": ...}
                
                print(f"[HostAgent] Nhận đồng bộ dự án: {project_id} ({len(files)} files)")
                
                if not project_id:
                    raise ValueError("Thiếu project_id")
                
                # Tạo thư mục lưu project
                proj_dir = os.path.abspath(os.path.join("exports", f"project_{project_id}"))
                os.makedirs(proj_dir, exist_ok=True)
                
                import base64
                
                for f_info in files:
                    f_name = f_info.get("name")
                    content_type = f_info.get("content_type", "text")
                    f_data = f_info.get("data", "")
                    
                    if not f_name:
                        continue
                        
                    file_path = os.path.join(proj_dir, f_name)
                    
                    if content_type == "binary":
                        # Giải mã base64
                        bytes_data = base64.b64decode(f_data)
                        with open(file_path, "wb") as f_out:
                            f_out.write(bytes_data)
                    else:
                        # Ghi text thường
                        with open(file_path, "w", encoding="utf-8") as f_out:
                            f_out.write(f_data)
                            
                    print(f"[HostAgent] Đã đồng bộ file: {f_name}")
                
                # Cập nhật lại giao diện Dashboard nếu đang chạy
                global app_instance
                if 'app_instance' in globals() and app_instance:
                    root.after(0, app_instance.refresh_projects_list)
                
                # Trả về kết quả JSON
                response_data = json.dumps({"success": True}, ensure_ascii=False)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(response_data.encode('utf-8'))
            except Exception as e:
                print(f"[HostAgent] Lỗi đồng bộ: {e}")
                response_data = json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(response_data.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_http_server(port=8000):
    server_address = ('', port)
    global httpd
    httpd = HTTPServer(server_address, HostControlHandler)
    print(f"[HostAgent] Server API đang chạy ngầm trên port {port}...")
    try:
        httpd.serve_forever()
    except Exception as e:
        print(f"[HostAgent] Dừng server API do lỗi: {e}")

# ==================== PHẦN GIAO DIỆN GUI TKINTER ====================

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VideoCrew Host Agent Dashboard")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e1e2e")
        
        # Đặt font chữ mặc định
        self.font_title = ("Segoe UI", 12, "bold")
        self.font_normal = ("Segoe UI", 10)
        self.font_bold = ("Segoe UI", 10, "bold")
        
        # Cấu hình màu sắc (Dark Theme)
        self.bg_color = "#1e1e2e"
        self.sidebar_color = "#181825"
        self.accent_color = "#89b4fa"
        self.text_color = "#cdd6f4"
        self.button_color = "#313244"
        
        # Thư mục chứa gói dữ liệu xuất bản
        self.exports_dir = os.path.abspath("exports")
        if not os.path.exists(self.exports_dir):
            os.makedirs(self.exports_dir, exist_ok=True)
            
        self.selected_project = None
        self.image_references = [] # Lưu tham chiếu ảnh để tránh rác bộ nhớ Tkinter
        
        self.setup_ui()
        self.refresh_projects_list()
        
    def setup_ui(self):
        # 1. Sidebar (Danh sách Project)
        self.sidebar = tk.Frame(self.root, bg=self.sidebar_color, width=280)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        lbl_list_title = tk.Label(
            self.sidebar, text="Danh sách xuất bản (exports/)", 
            font=self.font_title, bg=self.sidebar_color, fg=self.accent_color, pady=10
        )
        lbl_list_title.pack(anchor="w", padx=15)
        
        # Nút làm mới danh sách
        btn_refresh = tk.Button(
            self.sidebar, text="Làm mới danh sách", font=self.font_normal,
            bg=self.button_color, fg=self.text_color, activebackground=self.accent_color,
            relief=tk.FLAT, bd=0, command=self.refresh_projects_list
        )
        btn_refresh.pack(fill=tk.X, padx=15, pady=5)
        
        # Listbox hiển thị danh sách các thư mục project
        self.lst_projects = tk.Listbox(
            self.sidebar, font=self.font_normal, bg=self.sidebar_color, fg=self.text_color,
            selectbackground=self.accent_color, selectforeground=self.sidebar_color,
            bd=0, highlightthickness=0
        )
        self.lst_projects.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.lst_projects.bind("<<ListboxSelect>>", self.on_project_select)
        
        # 2. Vùng thông tin chi tiết (bên phải)
        self.detail_area = tk.Frame(self.root, bg=self.bg_color)
        self.detail_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tiêu đề Project được chọn
        self.lbl_proj_title = tk.Label(
            self.detail_area, text="Chọn một dự án để xem chi tiết", 
            font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.text_color
        )
        self.lbl_proj_title.pack(anchor="w", pady=10)
        
        # Trạng thái nạp Veo3
        self.lbl_status = tk.Label(
            self.detail_area, text="Trạng thái nạp: Chưa chọn dự án", 
            font=self.font_normal, bg=self.bg_color, fg="#a6adc8"
        )
        self.lbl_status.pack(anchor="w", pady=5)
        
        # Khung chứa lưới ảnh phân cảnh (Cuộn được)
        self.canvas_frame = tk.Frame(self.detail_area, bg=self.bg_color)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.bg_color, bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Vùng nút chức năng (bên dưới)
        self.btn_frame = tk.Frame(self.detail_area, bg=self.bg_color)
        self.btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        self.btn_open_folder = tk.Button(
            self.btn_frame, text="Mở thư mục xuất dữ liệu", font=self.font_bold,
            bg=self.button_color, fg=self.text_color, activebackground=self.accent_color,
            relief=tk.FLAT, bd=0, padx=20, pady=10, state=tk.DISABLED,
            command=self.open_export_folder
        )
        self.btn_open_folder.pack(side=tk.LEFT, padx=5)
        
        self.btn_push_veo3 = tk.Button(
            self.btn_frame, text="Đẩy tự động vào Veo3", font=self.font_bold,
            bg=self.accent_color, fg=self.sidebar_color, activebackground=self.button_color,
            relief=tk.FLAT, bd=0, padx=25, pady=10, state=tk.DISABLED,
            command=self.push_to_veo3
        )
        self.btn_push_veo3.pack(side=tk.LEFT, padx=5)

    def refresh_projects_list(self):
        self.lst_projects.delete(0, tk.END)
        if not os.path.exists(self.exports_dir):
            return
            
        folders = [f for f in os.listdir(self.exports_dir) if os.path.isdir(os.path.join(self.exports_dir, f))]
        # Sắp xếp các thư mục project
        folders.sort(key=lambda x: [int(c) if c.isdigit() else c for c in x.split("_")])
        
        for folder in folders:
            proj_path = os.path.join(self.exports_dir, folder)
            status_file = os.path.join(proj_path, "push_status.json")
            status_suffix = ""
            if os.path.exists(status_file):
                try:
                    with open(status_file, "r", encoding="utf-8") as sf:
                        status_data = json.load(sf)
                    if status_data.get("pushed"):
                        status_suffix = " (Đã nạp)"
                except:
                    pass
            self.lst_projects.insert(tk.END, f"{folder}{status_suffix}")
            
    def on_project_select(self, event):
        selection = self.lst_projects.curselection()
        if not selection:
            return
            
        raw_name = self.lst_projects.get(selection[0])
        # Loại bỏ hậu tố " (Đã nạp)" nếu có
        folder_name = raw_name.replace(" (Đã nạp)", "")
        self.selected_project = folder_name
        
        # Cập nhật UI chi tiết
        self.lbl_proj_title.config(text=f"Dự án: {folder_name}")
        proj_path = os.path.join(self.exports_dir, folder_name)
        status_file = os.path.join(proj_path, "push_status.json")
        
        if os.path.exists(status_file):
            try:
                with open(status_file, "r", encoding="utf-8") as sf:
                    status_data = json.load(sf)
                self.lbl_status.config(
                    text=f"Trạng thái nạp: Đã đẩy tự động vào Veo3 lúc {status_data.get('pushed_at', '')}",
                    fg="#a6e3a1" # Màu xanh
                )
            except:
                self.lbl_status.config(text="Trạng thái nạp: Chưa đẩy vào Veo3", fg="#f38ba8")
        else:
            self.lbl_status.config(text="Trạng thái nạp: Chưa đẩy vào Veo3", fg="#f38ba8")
            
        # Mở các nút chức năng
        self.btn_open_folder.config(state=tk.NORMAL)
        self.btn_push_veo3.config(state=tk.NORMAL)
        
        # Hiển thị ảnh phân cảnh
        self.render_project_images(proj_path)

    def render_project_images(self, proj_path):
        # Dọn dẹp các ảnh cũ trong scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.image_references.clear()
        
        # Tìm tất cả file ảnh của phân cảnh
        image_files = sorted(glob.glob(os.path.join(proj_path, "scene_*_*.png")) + 
                             glob.glob(os.path.join(proj_path, "scene_*_*.jpg")) + 
                             glob.glob(os.path.join(proj_path, "scene_*_*.jpeg")))
        
        if not image_files:
            lbl_no_img = tk.Label(
                self.scrollable_frame, text="Không tìm thấy ảnh phân cảnh trong gói dữ liệu.",
                font=self.font_normal, bg=self.bg_color, fg="#a6adc8"
            )
            lbl_no_img.pack(pady=20)
            return
            
        # Tạo lưới ảnh 3 cột
        cols_count = 3
        for idx, img_path in enumerate(image_files):
            r = idx // cols_count
            c = idx % cols_count
            
            try:
                # Load và resize ảnh làm thumbnail
                img = Image.open(img_path)
                img.thumbnail((160, 120))
                tk_img = ImageTk.PhotoImage(img)
                self.image_references.append(tk_img) # Giữ tham chiếu ảnh
                
                # Khung chứa cho từng ảnh
                img_card = tk.Frame(self.scrollable_frame, bg=self.sidebar_color, padx=5, pady=5)
                img_card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
                
                lbl_img = tk.Label(img_card, image=tk_img, bg=self.sidebar_color)
                lbl_img.pack()
                
                # Trích xuất scene title gọn gàng
                img_name = os.path.basename(img_path)
                try:
                    parts = img_name.split("_")
                    scene_title = parts[0].capitalize() + " " + parts[1]
                except:
                    scene_title = img_name
                    
                lbl_caption = tk.Label(
                    img_card, text=scene_title, font=("Segoe UI", 9), 
                    bg=self.sidebar_color, fg=self.text_color, wraplength=150
                )
                lbl_caption.pack(pady=3)
            except Exception as e:
                print(f"[WARN] Lỗi load ảnh {img_path}: {e}")

    def open_export_folder(self):
        if not self.selected_project:
            return
        proj_path = os.path.join(self.exports_dir, self.selected_project)
        os.startfile(proj_path)
        
    def push_to_veo3(self):
        if not self.selected_project:
            return
            
        confirm = messagebox.askyesno(
            "Xác nhận", 
            f"Bạn có chắc muốn thực hiện tự động đẩy dự án '{self.selected_project}' vào phần mềm Veo3 không?\n\nChú ý: Không chạm vào chuột/bàn phím trong quá trình giả lập chạy."
        )
        if not confirm:
            return
            
        proj_path = os.path.join(self.exports_dir, self.selected_project)
        
        # Thực hiện đẩy trong luồng riêng để tránh làm đơ giao diện Tkinter
        threading.Thread(target=self.run_automation_flow, args=(self.selected_project, proj_path), daemon=True).start()

    def run_automation_flow(self, project_id, export_dir):
        try:
            # 1. Quét tìm cửa sổ Veo3 bằng Powershell
            win32_scan_script = """
            Add-Type @"
            using System;
            using System.Runtime.InteropServices;
            using System.Text;
            using System.Collections.Generic;
            public class WinEnum {
                [DllImport("user32.dll")]
                static extern bool IsWindowVisible(IntPtr hWnd);
                [DllImport("user32.dll")]
                static extern int GetWindowTextLength(IntPtr hWnd);
                [DllImport("user32.dll")]
                static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
                [DllImport("user32.dll")]
                static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
                delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
                
                public static List<string> GetVisibleWindowTitles() {
                    var list = new List<string>();
                    EnumWindows((hwnd, lParam) => {
                        if (IsWindowVisible(hwnd)) {
                            int len = GetWindowTextLength(hwnd);
                            if (len > 0) {
                                var sb = new StringBuilder(len + 1);
                                GetWindowText(hwnd, sb, sb.Capacity);
                                list.Add(sb.ToString());
                            }
                        }
                        return true;
                    }, IntPtr.Zero);
                    return list;
                }
            }
            "@
            [WinEnum]::GetVisibleWindowTitles()
            """
            
            check_res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", win32_scan_script],
                capture_output=True, text=True, timeout=10
            )
            window_titles = [line.strip() for line in check_res.stdout.split("\n") if line.strip()]
            
            VEO_KEYWORDS = ["veo3", "veo 3", "google veo", "veo"]
            target_title = None
            for kw in VEO_KEYWORDS:
                target_title = next((t for t in window_titles if kw in t.lower()), None)
                if target_title:
                    break
                    
            if not target_title:
                messagebox.showwarning("Cảnh báo", "Không tự động tìm thấy cửa sổ Veo3. Vui lòng khởi động phần mềm Veo3 trước!")
                return
                
            # 2. Thực thi giả lập
            computer_control({"action": "focus_window", "title": target_title})
            computer_control({"action": "wait", "seconds": "1.0"})
            computer_control({"action": "hotkey", "keys": "ctrl+i"})
            computer_control({"action": "wait", "seconds": "1.0"})
            computer_control({"action": "hotkey", "keys": "alt+d"})
            computer_control({"action": "wait", "seconds": "0.5"})
            computer_control({"action": "smart_type", "text": export_dir})
            computer_control({"action": "press", "key": "enter"})
            computer_control({"action": "wait", "seconds": "0.8"})
            computer_control({"action": "press", "key": "tab"})
            computer_control({"action": "wait", "seconds": "0.5"})
            computer_control({"action": "hotkey", "keys": "ctrl+a"})
            computer_control({"action": "wait", "seconds": "0.5"})
            computer_control({"action": "press", "key": "enter"})
            
            # 3. Trích xuất visual prompts và paste hàng loạt
            prompts_text = ""
            vp_path = os.path.join(export_dir, "visual_prompts.txt")
            if os.path.exists(vp_path):
                import re
                with open(vp_path, "r", encoding="utf-8") as vf:
                    vp_content = vf.read()
                matches = re.findall(r"(?:Scene|Cảnh)\s*\d+\s*[:\-–\.]\s*(.*)", vp_content, re.IGNORECASE)
                if matches:
                    prompts_text = "\n".join([m.strip() for m in matches if m.strip()])
                else:
                    prompts_text = vp_content
                    
            if prompts_text:
                computer_control({"action": "wait", "seconds": "2.0"})
                computer_control({"action": "screen_click", "description": "Nhập hàng loạt prompt tương ứng"})
                computer_control({"action": "wait", "seconds": "0.5"})
                computer_control({"action": "clear_field"})
                computer_control({"action": "wait", "seconds": "0.2"})
                computer_control({"action": "paste", "text": prompts_text})
                
            # 4. Ghi trạng thái thành công
            import datetime
            status_file = os.path.join(export_dir, "push_status.json")
            with open(status_file, "w", encoding="utf-8") as sf:
                json.dump({
                    "pushed": True,
                    "pushed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, sf)
                
            # Làm mới giao diện sau khi nạp xong
            self.root.after(0, self.on_push_success, project_id)
        except Exception as err:
            self.root.after(0, self.on_push_failed, str(err))

    def on_push_success(self, project_id):
        messagebox.showinfo("Thành công", f"Đã tự động nạp thành công dự án '{project_id}' vào phần mềm Veo3!")
        self.refresh_projects_list()
        
    def on_push_failed(self, error_msg):
        messagebox.showerror("Lỗi", f"Không thể tự động nạp dữ liệu: {error_msg}")

# ==================== KHỞI CHẠY HỆ THỐNG ====================

if __name__ == '__main__':
    # 1. Khởi động server HTTP API chạy ngầm
    server_thread = threading.Thread(target=run_http_server, args=(8000,), daemon=True)
    server_thread.start()
    
    # 2. Khởi chạy giao diện Desktop Dashboard Tkinter
    root = tk.Tk()
    global app_instance
    app_instance = DashboardApp(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
