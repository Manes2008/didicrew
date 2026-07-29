import streamlit as st

def inject_custom_css(logged_in=True):
    # Nạp Bootstrap Icons cho trang chính
    st.markdown(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">',
        unsafe_allow_html=True
    )
    
    # Ẩn sidebar nếu chưa đăng nhập
    if not logged_in:
        st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("""
<style>
    :root {
        --vc-radius-sm: 8px;
        --vc-radius-md: 12px;
        --vc-radius-lg: 16px;
        --vc-space-xs: 0.35rem;
        --vc-space-sm: 0.6rem;
        --vc-space-md: 1rem;
        --vc-space-lg: 1.5rem;
        --vc-border: rgba(128, 128, 128, 0.18);
        --vc-border-strong: rgba(128, 128, 128, 0.32);
        --vc-muted: #808495;
        --vc-accent-1: #C2542D;
        --vc-accent-2: #C99A45;
        --vc-accent-soft: rgba(194, 84, 45, 0.10);
        --vc-accent-soft-strong: rgba(194, 84, 45, 0.16);
    }

    .main .block-container {
        padding-top: 1.4rem !important;
        padding-bottom: 3rem !important;
        max-width: 1360px;
    }

    .vc-header {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 0.1rem;
    }
    .vc-logo-mark {
        width: 40px;
        height: 40px;
        border-radius: 11px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 19px;
        color: #fff;
        background: linear-gradient(135deg, var(--vc-accent-1), var(--vc-accent-2));
        box-shadow: 0 3px 10px rgba(194, 84, 45, 0.20);
        flex-shrink: 0;
    }
    .main-title {
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.1;
        background: linear-gradient(90deg, #C2542D, #C99A45);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .sub-title {
        color: var(--vc-muted);
        font-size: 0.9rem;
        margin: 0.15rem 0 1.6rem 3.05rem;
    }

    .vc-eyebrow {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--vc-muted);
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .vc-card {
        border: 1px solid var(--vc-border);
        border-radius: var(--vc-radius-md);
        padding: var(--vc-space-md);
        margin-bottom: var(--vc-space-md);
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--vc-border) !important;
        border-radius: var(--vc-radius-md) !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: var(--vc-radius-md) !important;
    }

    .stButton > button {
        border-radius: var(--vc-radius-sm) !important;
        font-weight: 600 !important;
        transition: all 0.15s ease-in-out !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
    }
    button[kind="primary"],
    button[data-testid="stBaseButton-primary"],
    button[kind="primaryFormSubmit"],
    button[data-testid="stBaseButton-primaryFormSubmit"] {
        background-color: var(--vc-accent-1) !important;
        border-color: var(--vc-accent-1) !important;
        color: #fff !important;
    }
    button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover,
    button[kind="primaryFormSubmit"]:hover,
    button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
        background-color: #A6482A !important;
        border-color: #A6482A !important;
        color: #fff !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.1rem;
    }
    .vc-sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 1.1rem;
        padding-bottom: 0.9rem;
        border-bottom: 1px solid var(--vc-border);
    }
    .vc-sidebar-brand .vc-logo-mark {
        width: 34px;
        height: 34px;
        border-radius: 9px;
        font-size: 16px;
    }
    .vc-sidebar-brand-text {
        font-weight: 800;
        font-size: 1.02rem;
        line-height: 1.15;
    }
    .vc-sidebar-brand-sub {
        font-size: 0.7rem;
        color: var(--vc-muted);
        letter-spacing: 0.03em;
    }
    .vc-sidebar-section {
        margin-bottom: 1.3rem;
    }

    .vc-account-card {
        border: 1px solid var(--vc-border);
        border-radius: var(--vc-radius-md);
        padding: 0.85rem 0.95rem;
        background: var(--vc-accent-soft);
    }
    .vc-account-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.82rem;
        padding: 0.18rem 0;
    }
    .vc-account-row + .vc-account-row {
        border-top: 1px dashed var(--vc-border);
    }
    .vc-account-label {
        color: var(--vc-muted);
    }
    .vc-account-value {
        font-weight: 600;
    }
    .user-badge {
        display: inline-block;
        padding: 0.14rem 0.55rem;
        border-radius: 999px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        background-color: var(--vc-accent-soft-strong);
        color: var(--vc-accent-1);
    }

    nav[data-testid="stSidebarNav"] { display: none; }

    .vc-stage-row {
        border: 1px solid var(--vc-border);
        border-radius: var(--vc-radius-sm);
        padding: 0.55rem 0.8rem;
        margin-bottom: 0.5rem;
        transition: border-color 0.15s ease;
    }
    .vc-stage-row:hover {
        border-color: var(--vc-border-strong);
    }
    .vc-stage-name {
        font-weight: 700;
        font-size: 0.85rem;
    }
    .vc-stage-role-pill {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.1rem 0.5rem;
        border-radius: 999px;
        background: var(--vc-accent-soft);
        color: var(--vc-accent-1);
    }
    .vc-stage-goal {
        color: var(--vc-muted);
        font-size: 0.78rem;
    }

    .vc-result-header {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: var(--vc-muted);
        margin: 0.4rem 0 0.6rem 0;
    }
    hr { margin: 1rem 0 !important; }
    
    /* Login Form styling & animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(24px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    div:has(#login-gate) div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--vc-border) !important;
        border-radius: var(--vc-radius-lg) !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.22) !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(12px) !important;
        padding: 2.4rem !important;
        margin-top: 80px !important;
        animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
</style>
""", unsafe_allow_html=True)
