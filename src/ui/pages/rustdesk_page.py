import streamlit as st
import time
from src.tools.rustdesk_manager import (
    check_docker_installed,
    get_public_ip,
    get_services_status,
    start_docker_services,
    stop_docker_services,
    get_public_key,
    generate_quick_link,
    get_container_logs,
    validate_relay_host
)

def render_rustdesk_page():
    st.markdown("""
    <div class="vc-header">
        <div class="vc-logo-mark"><i class="bi bi-pc-display"></i></div>
        <h3 style="margin:0; font-weight:800;">Cấu hình RustDesk Server</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Deploy và quản lý RustDesk ID/Relay Server tự host qua Docker cho kết nối ngoài</div>', unsafe_allow_html=True)

    # 1. Kiểm tra Docker
    if not check_docker_installed():
        st.error("Lỗi: Docker Desktop hoặc Docker Daemon chưa được khởi động trên máy tính này. Vui lòng bật Docker trước khi sử dụng tính năng này.")
        return

    # 2. Lấy thông tin trạng thái
    status = get_services_status()
    hbbs_status = status.get("hbbs", "offline")
    hbbr_status = status.get("hbbr", "offline")
    is_running = "up" in hbbs_status.lower() and "up" in hbbr_status.lower()

    # 3. Hiển thị Metrics Trạng thái
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-info-circle"></i> Trạng thái dịch vụ</div>', unsafe_allow_html=True)
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        if is_running:
            st.markdown("""
                <div class="metric-card" style="border-left: 4px solid #27ae60;">
                    <div class="metric-number" style="color:#27ae60;">ONLINE</div>
                    <div class="metric-label">Trạng thái Server</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="metric-card" style="border-left: 4px solid #e74c3c;">
                    <div class="metric-number" style="color:#e74c3c;">OFFLINE</div>
                    <div class="metric-label">Trạng thái Server</div>
                </div>
            """, unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number" style="font-size: 1rem; padding-top: 10px; color:#dde3ed;">{hbbs_status}</div>
                <div class="metric-label">Container HBBS (ID)</div>
            </div>
        """, unsafe_allow_html=True)
    with col_stat3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number" style="font-size: 1rem; padding-top: 10px; color:#dde3ed;">{hbbr_status}</div>
                <div class="metric-label">Container HBBR (Relay)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 4. Panel Điều khiển & Cấu hình
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-sliders"></i> Bảng điều khiển</div>', unsafe_allow_html=True)
    
    # Lấy IP Public tự động nếu chưa có cấu hình trong session
    if "rd_public_ip" not in st.session_state:
        with st.spinner("Đang phát hiện IP Public..."):
            st.session_state["rd_public_ip"] = get_public_ip()

    with st.container(border=True):
        col_cfg1, col_cfg2 = st.columns([2, 1])
        with col_cfg1:
            relay_host_input = st.text_input(
                "Địa chỉ IP Public hoặc Tên miền (Domain) của Host",
                value=st.session_state["rd_public_ip"],
                help="Điền IP Public hiện tại của bạn hoặc tên miền DDNS (ví dụ: no-ip, duckdns) trỏ về máy này."
            )
            
            # Kiểm tra validation trực tiếp
            if relay_host_input:
                if validate_relay_host(relay_host_input):
                    st.success("Định dạng IP/Domain hợp lệ.")
                else:
                    st.error("Lỗi: Định dạng IP hoặc Domain không hợp lệ. Vui lòng kiểm tra lại.")
        
        with col_cfg2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if is_running:
                if st.button("Dừng RustDesk Server", type="secondary", use_container_width=True):
                    with st.spinner("Đang dừng containers..."):
                        success, msg = stop_docker_services()
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                # Disable nút Start nếu host không hợp lệ
                btn_disabled = not validate_relay_host(relay_host_input)
                if st.button("Khởi động RustDesk Server", type="primary", use_container_width=True, disabled=btn_disabled):
                    with st.spinner("Đang cấu hình và chạy docker compose..."):
                        success, msg = start_docker_services(relay_host_input)
                        if success:
                            st.success(msg)
                            time.sleep(2)  # Đợi 2s để sinh key
                            st.rerun()
                        else:
                            st.error(msg)

    # 5. Thông tin kết nối & Đường link nhanh
    if is_running:
        st.markdown('<div class="vc-eyebrow"><i class="bi bi-link-45deg"></i> Thông tin kết nối cho người ngoài</div>', unsafe_allow_html=True)
        public_key = get_public_key()
        quick_link = generate_quick_link(relay_host_input, public_key)

        with st.container(border=True):
            st.markdown(f"**1. Đường link kết nối nhanh (Khuyên dùng):**")
            st.markdown("Người ngoài chỉ cần click vào link dưới đây trên trình duyệt của họ (yêu cầu máy của họ đã cài sẵn RustDesk Client), hệ thống sẽ tự động cấu hình ID Server và Key bảo mật:")
            
            if quick_link:
                st.code(quick_link, language="bash")
                # Hiển thị nút copy link thân thiện
                st.info("Hãy gửi link trên cho đối tác/người dùng bên ngoài để họ truy cập nhanh vào máy của bạn.")
            else:
                st.warning("Đang chờ Server sinh khóa mã hóa (Key). Vui lòng đợi vài giây hoặc tải lại trang.")

            st.markdown("---")
            st.markdown("**2. Cấu hình thủ công trên RustDesk Client:**")
            st.markdown("Nếu không sử dụng link nhanh, người ngoài có thể mở app RustDesk Client, vào mục **Settings -> Network** và điền cấu hình sau:")
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.text_input("ID Server", value=relay_host_input, disabled=True)
                st.text_input("Relay Server", value=relay_host_input, disabled=True)
            with col_info2:
                st.text_input("Public Key (Mã khóa)", value=public_key, disabled=True)

    # 6. Hướng dẫn mở cổng Router
    st.markdown('<div class="vc-eyebrow"><i class="bi bi-shield-exclamation"></i> Hướng dẫn cấu hình mạng (Bắt buộc)</div>', unsafe_allow_html=True)
    with st.expander("Xem hướng dẫn cấu hình Port Forwarding trên Router", expanded=not is_running):
        st.markdown("""
        Để người ngoài có thể kết nối được, bạn **bắt buộc** phải mở cổng trên Modem/Router Internet của bạn trỏ về IP Local của máy tính này.
        """)
        
        # Lấy IP Local của host
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = "192.168.1.X"

        st.info(f"**IP Mạng nội bộ (LAN IP) của máy tính này:** `{local_ip}`")
        
        # Bảng các cổng
        st.markdown("""
        | Cổng (Port) | Giao thức (Protocol) | Mục đích sử dụng | Trạng thái bắt buộc |
        |---|---|---|---|
        | **21115** | TCP | RustDesk Connection Test | Không bắt buộc |
        | **21116** | TCP | RustDesk ID Server | **Bắt buộc** |
        | **21116** | UDP | RustDesk Rendezvous/Nat | **Bắt buộc** |
        | **21117** | TCP | RustDesk Relay Server | **Bắt buộc** |
        
        **Các bước thực hiện:**
        1. Truy cập trang cấu hình Modem (thường là `192.168.1.1` hoặc `192.168.0.1`).
        2. Tìm mục **Port Forwarding** / **Virtual Server** / **NAT**.
        3. Tạo các rule mở cổng `21115`, `21116` (cả TCP và UDP), và `21117` TCP trỏ về địa chỉ IP Local phía trên.
        """)

    # 7. Log Viewer
    if is_running:
        st.markdown('<div class="vc-eyebrow"><i class="bi bi-terminal"></i> Nhật ký hoạt động (Logs)</div>', unsafe_allow_html=True)
        tab_log_hbbs, tab_log_hbbr = st.tabs(["Logs ID Server (hbbs)", "Logs Relay Server (hbbr)"])
        
        with tab_log_hbbs:
            hbbs_logs = get_container_logs("rustdesk-hbbs")
            st.code(hbbs_logs, language="log")
            
        with tab_log_hbbr:
            hbbr_logs = get_container_logs("rustdesk-hbbr")
            st.code(hbbr_logs, language="log")

        if st.button("Làm mới Log"):
            st.rerun()
