# Admin IP Manager - Trang quan ly IP thiet bi
# Trang nay KHONG bi IP gate chan, nhung YEU CAU Admin Secret Key
# Truy cap: http://localhost:8501/Admin_IP_Manager

import streamlit as st
import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
from src.core.models import init_db, get_db_session, AllowedIP, User

st.set_page_config(
    page_title="Admin - Quản lý IP Thiết bị | VideoCrew",
    page_icon="shield",
    layout="centered",
)

# Khoi tao DB neu chua
try:
    init_db()
except Exception as e:
    st.error(f"Lỗi kết nối DB: {e}")
    st.stop()

# ==================== HEADER ====================
st.title("Quản lý IP Thiết bị")
st.caption("Phê duyệt hoặc từ chối thiết bị truy cập vào VideoCrew Studio")
st.divider()

# ==================== ADMIN AUTH ====================
if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

# Tu dong xac thuc neu tai khoan dang dang nhap co quyen admin
if "current_user" in st.session_state and st.session_state["current_user"]["role"] == "admin":
    st.session_state["admin_authenticated"] = True

if not st.session_state["admin_authenticated"]:
    st.subheader("Xác thực Admin")
    with st.form("admin_login_form"):
        key_input = st.text_input(
            "Nhập Admin Secret Key",
            type="password",
            placeholder="Nhập secret key...",
        )
        submitted = st.form_submit_button("Đăng nhập", use_container_width=True)
        if submitted:
            if key_input == config.ADMIN_SECRET_KEY:
                st.session_state["admin_authenticated"] = True
                st.rerun()
            else:
                st.error("Secret key không chính xác. Thử lại.")
    st.stop()


# ==================== DASHBOARD HEADER ====================
col_title, col_logout = st.columns([5, 1])
col_title.success("Đã xác thực Admin")
if col_logout.button("Đăng xuất"):
    st.session_state["admin_authenticated"] = False
    st.rerun()


st.markdown("---")

# Doc du lieu IP tu DB
db = get_db_session()
try:
    all_ips = db.query(AllowedIP).order_by(AllowedIP.created_at.desc()).all()
finally:
    db.close()

pending  = [x for x in all_ips if x.status == "pending"]
approved = [x for x in all_ips if x.status == "approved"]
rejected = [x for x in all_ips if x.status == "rejected"]

# ==================== METRICS ====================
m1, m2, m3, m4 = st.columns(4)
m1.metric("Tổng IP", len(all_ips))
m2.metric("Chờ duyệt", len(pending),  delta=f"+{len(pending)}" if pending else None, delta_color="inverse")
m3.metric("Đã duyệt",  len(approved))
m4.metric("Từ chối",   len(rejected))

st.divider()

tab_pending, tab_approved, tab_rejected, tab_add, tab_users = st.tabs([
    f"Chờ duyệt  ({len(pending)})",
    f"Đã duyệt   ({len(approved)})",
    f"Từ chối    ({len(rejected)})",
    "Thêm IP thủ công",
    "Quản lý User",
])


# ----- TAB: CHO DUYET -----
with tab_pending:
    if not pending:
        st.info("Không có IP nào đang chờ duyệt.")
    for rec in pending:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            c1.markdown(f"**`{rec.ip_address}`**")
            c1.caption(f"Đăng ký lúc: {rec.created_at.strftime('%Y-%m-%d %H:%M:%S') if rec.created_at else 'N/A'}")

            if c2.button("Duyệt", key=f"ap_{rec.id}", type="primary", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                    if r:
                        r.status = "approved"
                        r.approved_at = datetime.datetime.utcnow()
                        db_a.commit()
                    st.success(f"Đã duyệt {rec.ip_address}")
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

            if c3.button("Từ chối", key=f"rj_{rec.id}", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                    if r:
                        r.status = "rejected"
                        db_a.commit()
                    st.warning(f"Đã từ chối {rec.ip_address}")
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

# ----- TAB: DA DUYET -----
with tab_approved:
    if not approved:
        st.info("Chưa có IP nào được duyệt.")
    for rec in approved:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            c1.markdown(f"**`{rec.ip_address}`**  —  {rec.label or '_Không có nhãn_'}")
            c1.caption(
                f"Duyệt lúc: {rec.approved_at.strftime('%Y-%m-%d %H:%M:%S') if rec.approved_at else 'N/A'}"
                f"  |  Đăng ký lúc: {rec.created_at.strftime('%Y-%m-%d %H:%M:%S') if rec.created_at else 'N/A'}"
            )

            if c2.button("Từ chối", key=f"rv_{rec.id}", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                    if r:
                        r.status = "rejected"
                        r.approved_at = None
                        db_a.commit()
                    st.warning(f"Đã thu hồi quyền {rec.ip_address}")
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

            if c3.button("Xóa", key=f"dl_{rec.id}", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                    if r:
                        db_a.delete(r)
                        db_a.commit()
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

# ----- TAB: TU CHOI -----
with tab_rejected:
    if not rejected:
        st.info("Chưa có IP nào bị từ chối.")
    for rec in rejected:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            c1.markdown(f"**`{rec.ip_address}`**")
            c1.caption(f"Đăng ký lúc: {rec.created_at.strftime('%Y-%m-%d %H:%M:%S') if rec.created_at else 'N/A'}")

            if c2.button("Phê duyệt lại", key=f"rea_{rec.id}", type="primary", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                    if r:
                        r.status = "approved"
                        r.approved_at = datetime.datetime.utcnow()
                        db_a.commit()
                    st.success(f"Đã phê duyệt lại {rec.ip_address}")
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

            if c3.button("Xóa", key=f"dlr_{rec.id}", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                    if r:
                        db_a.delete(r)
                        db_a.commit()
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()


# ----- TAB: THEM IP THU CONG -----
with tab_add:
    st.markdown("Thêm IP thủ công và duyệt ngay lập tức.")
    with st.form("add_ip_form"):
        new_ip    = st.text_input("Địa chỉ IP", placeholder="Vd: 192.168.1.100 hoặc 118.69.52.156")
        new_label = st.text_input("Tên thiết bị / Ghi chú (tùy chọn)", placeholder="Vd: Laptop văn phòng, PC nhà...")
        auto_approve = st.checkbox("Phê duyệt ngay sau khi thêm", value=True)
        add_submitted = st.form_submit_button("Thêm IP", use_container_width=True, type="primary")

    if add_submitted:
        if not new_ip or not new_ip.strip():
            st.error("Vui lòng nhập địa chỉ IP.")
        else:
            db_a = get_db_session()
            try:
                existing = db_a.query(AllowedIP).filter_by(ip_address=new_ip.strip()).first()
                if existing:
                    st.warning(f"IP `{new_ip.strip()}` đã tồn tại trong hệ thống (trạng thái: {existing.status}).")
                else:
                    status_val = "approved" if auto_approve else "pending"
                    entry = AllowedIP(
                        ip_address=new_ip.strip(),
                        label=new_label.strip() if new_label else None,
                        status=status_val,
                        approved_at=datetime.datetime.utcnow() if auto_approve else None,
                    )
                    db_a.add(entry)
                    db_a.commit()
                    if auto_approve:
                        st.success(f"Đã thêm và phê duyệt IP `{new_ip.strip()}` thành công!")
                    else:
                        st.success(f"Đã thêm IP `{new_ip.strip()}` vào hàng chờ duyệt.")
                    st.rerun()
            except ValueError as ve:
                st.error(f"Dữ liệu không hợp lệ: {ve}")
            except Exception as ex:
                db_a.rollback()
                st.error(f"Lỗi: {ex}")
            finally:
                db_a.close()

    st.divider()
    st.caption("IP hiện tại của bạn (để tham khảo):")
    try:
        headers = st.context.headers
        current_ip = None
        for h in ["X-Forwarded-For", "X-Real-Ip", "CF-Connecting-IP"]:
            v = headers.get(h)
            if v:
                current_ip = v.split(",")[0].strip()
                break
        st.code(current_ip or "127.0.0.1 (local)")
    except Exception:
        st.code("Không xác định được")


# ----- TAB: QUAN LY USER -----
with tab_users:
    st.markdown("**Danh sách người dùng hệ thống**")
    db_u = get_db_session()
    try:
        users = db_u.query(User).order_by(User.created_at.desc()).all()
    finally:
        db_u.close()

    if not users:
        st.info("Chưa có người dùng nào đăng ký.")
    for u in users:
        with st.container(border=True):
            col_u1, col_u2, col_u3, col_u4 = st.columns([3, 1.5, 1.5, 1])
            status_text = "🟢 Hoạt động" if u.is_active else "🔴 Đã khóa"
            col_u1.markdown(f"👤 **{u.username}** — `{u.role.upper()}` ({status_text})")
            col_u1.caption(f"Ngày tạo: {u.created_at.strftime('%Y-%m-%d %H:%M') if u.created_at else 'N/A'}")

            # Nut thay doi vai tro (Role)
            btn_role_label = "Set User" if u.role == "admin" else "Set Admin"
            if col_u2.button(btn_role_label, key=f"role_user_{u.id}", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(User).filter_by(id=u.id).first()
                    if r:
                        r.role = "user" if r.role == "admin" else "admin"
                        db_a.commit()
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

            # Nut khoa / mo khoa
            btn_lock_label = "Khóa" if u.is_active else "Kích hoạt"
            if col_u3.button(btn_lock_label, key=f"lock_user_{u.id}", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(User).filter_by(id=u.id).first()
                    if r:
                        r.is_active = not r.is_active
                        db_a.commit()
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

            # Nut Xoa user
            if col_u4.button("Xóa", key=f"del_user_{u.id}", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(User).filter_by(id=u.id).first()
                    if r:
                        db_a.delete(r)
                        db_a.commit()
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()



