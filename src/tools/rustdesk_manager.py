import os
import subprocess
import requests
import re
from pathlib import Path

# Thư mục gốc chứa docker-compose.yml của rustdesk
RUSTDESK_DIR = Path(__file__).resolve().parent.parent.parent / "rustdesk"
KEY_FILE_PATH = RUSTDESK_DIR / "data" / "id_ed25519.pub"

def check_docker_installed() -> bool:
    """Kiểm tra Docker đã được cài đặt và đang chạy hay chưa."""
    try:
        # Chạy thử docker --version để xem có cài lệnh docker không
        res = subprocess.run(["docker", "--version"], capture_output=True, text=True, check=True)
        return "docker" in res.stdout.lower()
    except Exception:
        return False

def get_public_ip() -> str:
    """Lấy địa chỉ IP Public của máy host thông qua các API công cộng."""
    providers = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com"
    ]
    for url in providers:
        try:
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                ip = res.text.strip()
                # Kiểm tra xem có đúng định dạng IPv4 không
                if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                    return ip
        except Exception:
            continue
    return "127.0.0.1"

def validate_relay_host(host: str) -> bool:
    """Validate xem IP hoặc Domain nhập vào có hợp lệ không."""
    if not host or not host.strip():
        return False
    host = host.strip()
    # Validate IPv4
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
        parts = host.split(".")
        return all(0 <= int(p) <= 255 for p in parts)
    # Validate Domain (cho phép localhost)
    if host == "localhost":
        return True
    domain_regex = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$"
    return bool(re.match(domain_regex, host))

def write_env_file(relay_host: str):
    """Ghi đè file .env cấu hình host cho Docker Compose."""
    env_path = RUSTDESK_DIR / ".env"
    env_content = f"RELAY_HOST={relay_host.strip()}\n"
    env_path.write_text(env_content, encoding="utf-8")

def start_docker_services(relay_host: str) -> tuple[bool, str]:
    """Khởi chạy các container của RustDesk Server."""
    if not check_docker_installed():
        return False, "Docker không được cài đặt hoặc docker daemon không chạy."
    
    if not validate_relay_host(relay_host):
        return False, "Địa chỉ IP hoặc Tên miền không hợp lệ."
    
    try:
        # 1. Ghi cấu hình vào .env
        write_env_file(relay_host)
        
        # 2. Chạy docker compose up -d
        # Trên Windows, subprocess có thể cần shell=True để chạy đúng command hoặc sử dụng creationflags
        cmd = ["docker-compose", "up", "-d"]
        
        # Tạo thư mục data trước để tránh docker tự tạo thư mục data của root sở hữu
        data_dir = RUSTDESK_DIR / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        res = subprocess.run(
            cmd,
            cwd=str(RUSTDESK_DIR),
            capture_output=True,
            text=True
        )
        if res.returncode == 0:
            return True, "Khởi động RustDesk Server thành công."
        else:
            return False, f"Lỗi khởi động Docker: {res.stderr or res.stdout}"
    except Exception as e:
        return False, f"Đã xảy ra lỗi: {str(e)}"

def stop_docker_services() -> tuple[bool, str]:
    """Dừng các container của RustDesk Server."""
    if not check_docker_installed():
        return False, "Docker không được cài đặt hoặc daemon không hoạt động."
    try:
        cmd = ["docker-compose", "down"]
        res = subprocess.run(
            cmd,
            cwd=str(RUSTDESK_DIR),
            capture_output=True,
            text=True
        )
        if res.returncode == 0:
            return True, "Đã dừng RustDesk Server thành công."
        else:
            return False, f"Lỗi dừng Docker: {res.stderr or res.stdout}"
    except Exception as e:
        return False, f"Đã xảy ra lỗi: {str(e)}"

def get_services_status() -> dict:
    """Lấy trạng thái chi tiết của hbbs và hbbr containers."""
    status = {"hbbs": "offline", "hbbr": "offline"}
    if not check_docker_installed():
        return status
    try:
        # Lấy danh sách các container đang chạy
        cmd = ["docker", "ps", "--filter", "name=rustdesk", "--format", "{{.Names}}:{{.Status}}"]
        res = subprocess.run(
            cmd,
            cwd=str(RUSTDESK_DIR),
            capture_output=True,
            text=True
        )
        if res.returncode == 0 and res.stdout:
            lines = res.stdout.strip().split("\n")
            for line in lines:
                if ":" in line:
                    name, stat = line.split(":", 1)
                    if "hbbs" in name:
                        status["hbbs"] = stat
                    elif "hbbr" in name:
                        status["hbbr"] = stat
    except Exception:
        pass
    return status

def get_public_key() -> str:
    """Đọc file public key được sinh ra bởi hbbs."""
    if KEY_FILE_PATH.exists():
        try:
            return KEY_FILE_PATH.read_text(encoding="utf-8").strip()
        except Exception:
            return ""
    return ""

def generate_quick_link(relay_host: str, public_key: str) -> str:
    """Tạo URI liên kết nhanh để tự động cấu hình Client."""
    if not relay_host or not public_key:
        return ""
    return f"rustdesk://{relay_host.strip()}?key={public_key.strip()}"

def get_container_logs(container_name: str, tail: int = 30) -> str:
    """Lấy log mới nhất của container chỉ định."""
    if not check_docker_installed():
        return "Docker chưa sẵn sàng."
    try:
        cmd = ["docker", "logs", "--tail", str(tail), container_name]
        res = subprocess.run(
            cmd,
            cwd=str(RUSTDESK_DIR),
            capture_output=True,
            text=True
        )
        # docker logs in ra stderr nhiều hơn stdout nên ta lấy cả hai
        logs = (res.stderr or "") + (res.stdout or "")
        return logs.strip() if logs.strip() else "Không có log."
    except Exception as e:
        return f"Không thể lấy log: {str(e)}"
