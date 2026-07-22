# Admin IP Manager - Trang quan ly IP thiet bi
# Trang nay KHONG bi IP gate chan, nhung YEU CAU Admin Secret Key
# Truy cap: http://localhost:8501/Admin_IP_Manager

import streamlit as st
import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
from src.core.models import init_db, get_db_session, AllowedIP

st.set_page_config(
    page_title="Admin - Quan ly IP Thiet bi | VideoCrew",
    page_icon="shield",
    layout="centered",
)

# Khoi tao DB neu chua
try:
    init_db()
except Exception as e:
    st.error(f"Loi ket noi DB: {e}")
    st.stop()

# ==================== HEADER ====================
st.title("Quan ly IP Thiet bi")
st.caption("Phe duyet hoac tu choi thiet bi truy cap vao VideoCrew Studio")
st.divider()

# ==================== ADMIN AUTH ====================
if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

if not st.session_state["admin_authenticated"]:
    st.subheader("Xac thuc Admin")
    with st.form("admin_login_form"):
        key_input = st.text_input(
            "Nhap Admin Secret Key",
            type="password",
            placeholder="Nhap secret key...",
        )
        submitted = st.form_submit_button("Dang nhap", use_container_width=True)
        if submitted:
            if key_input == config.ADMIN_SECRET_KEY:
                st.session_state["admin_authenticated"] = True
                st.rerun()
            else:
                st.error("Secret key khong chinh xac. Thu lai.")
    st.stop()

# ==================== DASHBOARD HEADER ====================
col_title, col_logout = st.columns([5, 1])
col_title.success("Da xac thuc Admin")
if col_logout.button("Dang xuat"):
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
m1.metric("Tong IP", len(all_ips))
m2.metric("Cho duyet", len(pending),  delta=f"+{len(pending)}" if pending else None, delta_color="inverse")
m3.metric("Da duyet",  len(approved))
m4.metric("Tu choi",   len(rejected))

st.divider()

# ==================== TABS ====================
tab_pending, tab_approved, tab_rejected, tab_add = st.tabs([
    f"Cho duyet  ({len(pending)})",
    f"Da duyet   ({len(approved)})",
    f"Tu choi    ({len(rejected)})",
    "Them IP thu cong",
])

# ----- TAB: CHO DUYET -----
with tab_pending:
    if not pending:
        st.info("Khong co IP nao dang cho duyet.")
    for rec in pending:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            c1.markdown(f"**`{rec.ip_address}`**")
            c1.caption(f"Dang ky luc: {rec.created_at.strftime('%Y-%m-%d %H:%M:%S') if rec.created_at else 'N/A'}")

            if c2.button("Duyet", key=f"ap_{rec.id}", type="primary", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                    if r:
                        r.status = "approved"
                        r.approved_at = datetime.datetime.utcnow()
                        db_a.commit()
                    st.success(f"Da duyet {rec.ip_address}")
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

            if c3.button("Tu choi", key=f"rj_{rec.id}", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                    if r:
                        r.status = "rejected"
                        db_a.commit()
                    st.warning(f"Da tu choi {rec.ip_address}")
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

# ----- TAB: DA DUYET -----
with tab_approved:
    if not approved:
        st.info("Chua co IP nao duoc duyet.")
    for rec in approved:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            c1.markdown(f"**`{rec.ip_address}`**  —  {rec.label or '_Khong co nhan_'}")
            c1.caption(
                f"Duyet luc: {rec.approved_at.strftime('%Y-%m-%d %H:%M:%S') if rec.approved_at else 'N/A'}"
                f"  |  Dang ky luc: {rec.created_at.strftime('%Y-%m-%d %H:%M:%S') if rec.created_at else 'N/A'}"
            )

            if c2.button("Tu choi", key=f"rv_{rec.id}", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                    if r:
                        r.status = "rejected"
                        r.approved_at = None
                        db_a.commit()
                    st.warning(f"Da thu hoi quyen {rec.ip_address}")
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

            if c3.button("Xoa", key=f"dl_{rec.id}", use_container_width=True):
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
        st.info("Chua co IP nao bi tu choi.")
    for rec in rejected:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            c1.markdown(f"**`{rec.ip_address}`**")
            c1.caption(f"Dang ky luc: {rec.created_at.strftime('%Y-%m-%d %H:%M:%S') if rec.created_at else 'N/A'}")

            if c2.button("Phe duyet lai", key=f"rea_{rec.id}", type="primary", use_container_width=True):
                db_a = get_db_session()
                try:
                    r = db_a.query(AllowedIP).filter_by(id=rec.id).first()
                    if r:
                        r.status = "approved"
                        r.approved_at = datetime.datetime.utcnow()
                        db_a.commit()
                    st.success(f"Da phe duyet lai {rec.ip_address}")
                    st.rerun()
                except Exception as ex:
                    db_a.rollback()
                    st.error(str(ex))
                finally:
                    db_a.close()

            if c3.button("Xoa", key=f"dlr_{rec.id}", use_container_width=True):
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
    st.markdown("Them IP thu cong va approve ngay lap tuc.")
    with st.form("add_ip_form"):
        new_ip    = st.text_input("IP Address", placeholder="Vd: 192.168.1.100 hoac 118.69.52.156")
        new_label = st.text_input("Ten thiet bi / Ghi chu (tuy chon)", placeholder="Vd: Laptop van phong, PC nha...")
        auto_approve = st.checkbox("Phe duyet ngay sau khi them", value=True)
        add_submitted = st.form_submit_button("Them IP", use_container_width=True, type="primary")

    if add_submitted:
        if not new_ip or not new_ip.strip():
            st.error("Vui long nhap IP address.")
        else:
            db_a = get_db_session()
            try:
                existing = db_a.query(AllowedIP).filter_by(ip_address=new_ip.strip()).first()
                if existing:
                    st.warning(f"IP `{new_ip.strip()}` da ton tai trong he thong (trang thai: {existing.status}).")
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
                        st.success(f"Da them va phe duyet IP `{new_ip.strip()}` thanh cong!")
                    else:
                        st.success(f"Da them IP `{new_ip.strip()}` vao hang cho duyet.")
                    st.rerun()
            except ValueError as ve:
                st.error(f"Du lieu khong hop le: {ve}")
            except Exception as ex:
                db_a.rollback()
                st.error(f"Loi: {ex}")
            finally:
                db_a.close()

    st.divider()
    st.caption("IP hien tai cua ban (de tham khao):")
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
        st.code("Khong xac dinh duoc")
