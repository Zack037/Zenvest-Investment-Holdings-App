import hashlib
import html
import sqlite3
import textwrap
import uuid
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

APP_NAME = "Zenvest Investment Holdings"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSET_DIR = BASE_DIR / "assets"
DB_PATH = DATA_DIR / "zenvest_portal.db"
RECEIPTS_DIR = DATA_DIR / "receipts"
DATA_DIR.mkdir(exist_ok=True)
ASSET_DIR.mkdir(exist_ok=True)
RECEIPTS_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title=APP_NAME,
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# PREMIUM VISUAL DESIGN
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --navy:#061226;
        --navy2:#102A5C;
        --blue:#1D4ED8;
        --cyan:#0797B7;
        --gold:#D4AF37;
        --gold2:#F5D76E;
        --ink:#071126;
        --text:#0F172A;
        --muted:#475569;
        --soft:#EEF4FB;
        --card:#FFFFFF;
        --green:#15803D;
        --red:#B91C1C;
        --orange:#C2410C;
        --border:#CBD5E1;
    }

    html, body, [class*="css"] {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #EAF1F8 0%, #F8FAFC 46%, #E0F2FE 100%);
        color: var(--text);
    }

    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* Ensure every normal page text remains visible */
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: inherit;
    }
    .stMarkdown, .stText, .stCaption, .stWrite, .stDataFrame, .stTable {
        color: var(--text) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #061226 0%, #0D2450 62%, #113B78 100%);
        border-right: 1px solid rgba(255,255,255,.16);
    }
    section[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,.16) !important;
    }
    section[data-testid="stSidebar"] .badge,
    section[data-testid="stSidebar"] .badge * {
        color: #061226 !important;
        background: #F5D76E !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(90deg, #D4AF37, #F5D76E) !important;
        color: #061226 !important;
        font-weight: 900 !important;
        border: 0 !important;
        box-shadow: 0 12px 25px rgba(0,0,0,.25) !important;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: rgba(255,255,255,.08) !important;
        border: 1px solid rgba(255,255,255,.12) !important;
        border-radius: 12px !important;
        padding: .30rem .45rem !important;
        margin: .15rem 0 !important;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 13px !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 850 !important;
        min-height: 44px;
        box-shadow: 0 10px 22px rgba(15, 23, 42, .12);
        background: #FFFFFF !important;
        color: #061226 !important;
    }
    .stButton>button[kind="primary"], button[kind="primary"] {
        background: linear-gradient(90deg, var(--gold), var(--gold2)) !important;
        color: #061226 !important;
        border: 0 !important;
        box-shadow: 0 16px 32px rgba(212,175,55,.28) !important;
    }
    .stButton>button:hover {
        filter: brightness(1.03);
        transform: translateY(-1px);
        border-color: #94A3B8 !important;
    }

    /* Form inputs: visible and high contrast */
    .stTextInput label, .stNumberInput label, .stTextArea label, .stDateInput label,
    .stSelectbox label, .stRadio label, .stFileUploader label {
        color: #0F172A !important;
        font-weight: 800 !important;
    }
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.6px solid #94A3B8 !important;
        border-radius: 13px !important;
        box-shadow: 0 8px 18px rgba(15,23,42,.06) !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #64748B !important;
        opacity: 1 !important;
    }

    /* Streamlit tabs: no faded/invisible text */
    .stTabs [data-baseweb="tab-list"] {
        gap: .55rem;
        flex-wrap: wrap;
        border-bottom: 1px solid #CBD5E1;
        padding-bottom: .25rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: #FFFFFF !important;
        border-radius: 999px !important;
        border: 1.5px solid #CBD5E1 !important;
        padding: .55rem 1rem !important;
        font-weight: 900 !important;
        color: #0F172A !important;
        box-shadow: 0 8px 16px rgba(15,23,42,.07);
    }
    .stTabs [data-baseweb="tab"] p {
        color: #0F172A !important;
        font-weight: 900 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #061226 !important;
        color: #FFFFFF !important;
        border-color: #061226 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #FFFFFF !important;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        padding: 1rem 1.1rem;
        border-radius: 18px;
        border: 1px solid #CBD5E1;
        box-shadow: 0 14px 32px rgba(15,23,42,.08);
    }
    div[data-testid="stMetric"] label { color: #334155 !important; font-weight: 850; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #061226 !important; font-weight: 900; }

    /* Hero */
    .hero {
        background: radial-gradient(circle at 15% 10%, rgba(245,215,110,.34), transparent 25%),
                    linear-gradient(135deg, #061226 0%, #113B78 48%, #0797B7 100%);
        color: white;
        border-radius: 28px;
        padding: 2.1rem 2.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 24px 55px rgba(7,17,38,.25);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,.14);
    }
    .hero * { color: #FFFFFF !important; }
    .hero:after {
        content: "";
        position:absolute;
        right:-90px;
        top:-120px;
        width:330px;
        height:330px;
        background: rgba(255,255,255,.08);
        border-radius:50%;
    }
    .hero-title { font-size: 2.35rem; font-weight: 950; line-height: 1.08; margin: 0 0 .55rem; letter-spacing: -.04em; }
    .hero-subtitle { color:#EAF2FF !important; font-size: 1.02rem; line-height:1.65; max-width: 900px; }
    .hero-chip {
        display:inline-block;
        background: rgba(255,255,255,.18);
        border:1px solid rgba(255,255,255,.28);
        padding:.40rem .78rem;
        border-radius:999px;
        margin:.25rem .35rem .25rem 0;
        font-weight:900;
        font-size:.82rem;
        color:#FFFFFF !important;
    }

    /* Login page */
    .login-wrap {
        min-height: calc(100vh - 7rem);
        display:flex;
        align-items:center;
    }
    .login-hero {
        background: radial-gradient(circle at 20% 10%, rgba(245,215,110,.36), transparent 26%),
                    linear-gradient(135deg, #061226 0%, #133B78 58%, #0797B7 100%);
        color:#FFFFFF;
        border-radius:30px;
        padding:2.3rem;
        box-shadow: 0 28px 70px rgba(7,17,38,.28);
        border: 1px solid rgba(255,255,255,.16);
        overflow:hidden;
    }
    .login-hero * { color:#FFFFFF !important; }
    .login-title { font-size:2.55rem; line-height:1.08; font-weight:950; letter-spacing:-.045em; margin-bottom:.8rem; }
    .login-subtitle { color:#EAF2FF !important; font-size:1.05rem; line-height:1.7; margin-bottom:1rem; }
    .login-card {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
        color:var(--text);
        border-radius:28px;
        padding:1.45rem;
        box-shadow:0 24px 60px rgba(15,23,42,.16);
        border:2px solid rgba(212,175,55,.32);
    }
    .login-card * { color: #0F172A !important; }
    .brand-row { display:flex; gap:.75rem; align-items:center; margin-bottom:1rem; }
    .logo-dot {
        width:48px; height:48px; border-radius:15px;
        background:linear-gradient(135deg, var(--gold), var(--gold2));
        display:grid; place-items:center; color:#061226 !important; font-size:1.4rem; font-weight:950;
        box-shadow:0 10px 24px rgba(212,175,55,.28);
    }
    .brand-name { font-size:1.25rem; font-weight:950; color:#061226 !important; }
    .brand-small { font-size:.86rem; color:#475569 !important; font-weight:850; }

    /* Cards and sections */
    .panel, .card {
        background: #FFFFFF;
        color: var(--text);
        border: 1px solid #CBD5E1;
        border-radius: 22px;
        padding: 1.25rem 1.35rem;
        margin: .55rem 0 1rem;
        box-shadow: 0 14px 34px rgba(15,23,42,.08);
    }
    .panel *, .card * { color: #0F172A !important; }
    .card-muted { background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 18px; padding: 1rem; }

    .kpi-grid { display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap:1rem; margin:1rem 0; }
    .kpi-card {
        background: linear-gradient(180deg, #FFFFFF, #F8FAFC);
        border:1px solid #CBD5E1;
        border-radius:20px;
        padding:1.05rem;
        box-shadow:0 12px 30px rgba(15,23,42,.08);
        min-height:126px;
        border-top: 4px solid #D4AF37;
    }
    .kpi-card * { color: #0F172A !important; }
    .kpi-icon {
        width:42px; height:42px; border-radius:14px; display:grid; place-items:center;
        background:#DBEAFE; color:#1E3A8A !important; font-weight:950; margin-bottom:.55rem;
    }
    .kpi-label { color:#334155 !important; font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; font-weight:950; }
    .kpi-value { font-size:1.65rem; color:#061226 !important; font-weight:950; margin-top:.22rem; }
    .kpi-note { color:#475569 !important; font-size:.84rem; margin-top:.2rem; }

    .section-title { font-size:1.32rem; font-weight:950; color:#061226 !important; letter-spacing:-.025em; margin:1rem 0 .5rem; }
    .section-subtitle { color:#475569 !important; font-size:.94rem; margin:-.2rem 0 .8rem; }
    .project-card {
        background: #FFFFFF;
        border:1px solid #CBD5E1;
        border-radius:24px;
        padding:1.2rem 1.25rem;
        margin:.75rem 0 1rem;
        box-shadow:0 16px 38px rgba(15,23,42,.08);
        border-left:7px solid var(--gold);
    }
    .project-card * { color:#0F172A !important; }
    .project-title { font-size:1.28rem; color:#061226 !important; font-weight:950; letter-spacing:-.025em; margin-bottom:.18rem; }
    .project-meta { color:#475569 !important; font-size:.88rem; font-weight:850; margin-bottom:.55rem; }

    .badge {
        display:inline-flex; align-items:center; gap:.25rem; border-radius:999px; padding:.30rem .75rem;
        font-weight:900; font-size:.76rem; margin:.18rem .25rem .2rem 0;
    }
    .badge-blue { background:#DBEAFE; color:#1E3A8A !important; }
    .badge-green { background:#DCFCE7; color:#166534 !important; }
    .badge-orange { background:#FFEDD5; color:#9A3412 !important; }
    .badge-red { background:#FEE2E2; color:#991B1B !important; }
    .badge-gray { background:#E2E8F0; color:#334155 !important; }

    .business-section {
        background: #FFFFFF;
        border:1px solid #CBD5E1;
        border-radius:22px;
        padding:1rem 1.1rem;
        box-shadow:0 12px 30px rgba(15,23,42,.06);
        margin:.6rem 0;
        border-top:4px solid #0797B7;
    }
    .business-section h3 { margin:0 0 .4rem; font-size:1.08rem; color:#061226 !important; font-weight:950; }
    .business-section p { color:#334155 !important; line-height:1.65; margin:.2rem 0; }

    .product-card {
        background:#FFFFFF;
        border:1px solid #CBD5E1;
        border-radius:22px;
        padding:1.05rem;
        box-shadow:0 12px 30px rgba(15,23,42,.08);
        min-height:240px;
        border-top:4px solid #D4AF37;
    }
    .product-card * { color:#0F172A !important; }
    .product-placeholder {
        background:linear-gradient(135deg, #DBEAFE, #FEF3C7);
        border-radius:18px; height:110px; display:grid; place-items:center; color:#061226 !important; font-size:2rem; margin-bottom:.8rem;
    }

    .table-card {
        background:#FFFFFF;
        border-radius:22px;
        padding:1rem;
        border:1px solid #CBD5E1;
        box-shadow:0 12px 30px rgba(15,23,42,.07);
    }
    .table-card * { color:#0F172A !important; }

    .alert-box { background:#FFFBEB; border:1px solid #FDE68A; color:#92400E !important; border-radius:18px; padding:1rem; margin:.8rem 0; }
    .success-box { background:#ECFDF5; border:1px solid #BBF7D0; color:#14532D !important; border-radius:18px; padding:1rem; margin:.8rem 0; }
    .danger-box { background:#FEF2F2; border:1px solid #FECACA; color:#7F1D1D !important; border-radius:18px; padding:1rem; margin:.8rem 0; }
    .image-card img { border-radius:22px !important; box-shadow:0 15px 40px rgba(15,23,42,.16); }
    .footer-note { color:#334155 !important; font-size:.84rem; padding:1rem 0; font-weight:700; }

    /* Dataframes should remain readable */
    [data-testid="stDataFrame"] { background:#FFFFFF !important; border-radius:18px !important; }
    [data-testid="stDataFrame"] * { color:#0F172A !important; }

    @media (max-width: 900px) {
        .kpi-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }
        .login-title, .hero-title { font-size:1.85rem; }
        .login-hero { padding:1.35rem; }
        .hero { padding:1.4rem; }
    }
    @media (max-width: 640px) {
        .kpi-grid { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# =========================================================
# FINAL HIGH-CONTRAST VISIBILITY OVERRIDES
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --primary-navy:#06162F;
        --primary-blue:#0B3B75;
        --accent-gold:#E4B834;
        --accent-green:#16A34A;
        --accent-red:#DC2626;
        --page-bg:#EEF5FF;
        --text-main:#081526;
        --text-soft:#334155;
        --card-bg:#FFFFFF;
    }
    .stApp {
        background: linear-gradient(135deg, #EEF5FF 0%, #FFFFFF 52%, #E0F2FE 100%) !important;
        color: var(--text-main) !important;
    }
    .main .block-container { padding-top: 1.4rem !important; max-width: 1500px !important; }
    .stMarkdown, .stMarkdown p, .stText, .stCaption, .stWrite,
    label, .stSelectbox label, .stTextInput label, .stNumberInput label,
    .stTextArea label, .stDateInput label, .stFileUploader label { color: #081526 !important; }
    .login-hero-final {
        background: linear-gradient(135deg, #06162F 0%, #0B3B75 58%, #057A9C 100%) !important;
        border-radius: 30px !important; padding: 2.4rem 2.2rem !important;
        box-shadow: 0 28px 70px rgba(6,22,47,.28) !important;
        border: 1px solid rgba(255,255,255,.18) !important; min-height: 390px !important;
        overflow: hidden !important; position: relative !important;
    }
    .login-hero-final:before { content:""; position:absolute; right:-90px; top:-100px; width:280px; height:280px; background: rgba(228,184,52,.18); border-radius:50%; }
    .login-hero-final * { color: #FFFFFF !important; position: relative; z-index: 1; }
    .login-hero-final .gold-line { width: 92px; height: 7px; border-radius: 999px; background: #E4B834; margin-bottom: 1.3rem; }
    .login-hero-title-final { font-size: 2.65rem !important; line-height: 1.05 !important; font-weight: 950 !important; letter-spacing: -.045em !important; margin: 0 0 1rem !important; color: #FFFFFF !important; }
    .login-hero-subtitle-final { font-size: 1.08rem !important; line-height: 1.7 !important; max-width: 760px !important; margin-bottom: 1.3rem !important; color: #EAF6FF !important; font-weight: 650 !important; }
    .chip-final { display:inline-flex; align-items:center; gap:.35rem; background: rgba(255,255,255,.14) !important; border: 1px solid rgba(255,255,255,.28) !important; color: #FFFFFF !important; padding: .5rem .8rem; border-radius: 999px; margin: .25rem .25rem .25rem 0; font-weight: 900; font-size: .86rem; }
    .access-header-final { background: #FFFFFF !important; border: 2px solid #CBD5E1 !important; border-radius: 26px !important; padding: 1.25rem 1.35rem !important; margin-bottom: 1rem !important; box-shadow: 0 18px 45px rgba(15,23,42,.12) !important; }
    .access-header-final * { color: #081526 !important; }
    .access-brand-final { display:flex; align-items:center; gap:.85rem; }
    .access-logo-final { width:54px; height:54px; border-radius:16px; background: linear-gradient(135deg, #E4B834, #F8DB62); color:#06162F !important; display:grid; place-items:center; font-size:1.5rem; font-weight:950; box-shadow: 0 10px 22px rgba(228,184,52,.28); }
    .access-title-final { font-size:1.35rem; font-weight:950; color:#06162F !important; margin-bottom:.1rem; }
    .access-subtitle-final { font-size:.9rem; font-weight:850; color:#334155 !important; }
    .stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #CBD5E1 !important; }
    .stTabs [data-baseweb="tab"] { background: #FFFFFF !important; color: #06162F !important; border: 2px solid #CBD5E1 !important; box-shadow: 0 8px 16px rgba(15,23,42,.08) !important; }
    .stTabs [data-baseweb="tab"] p { color:#06162F !important; font-weight:950 !important; }
    .stTabs [aria-selected="true"] { background: #06162F !important; border-color: #06162F !important; box-shadow: 0 10px 22px rgba(6,22,47,.22) !important; }
    .stTabs [aria-selected="true"] p { color:#FFFFFF !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div { background: #FFFFFF !important; color: #081526 !important; border: 2px solid #64748B !important; border-radius: 14px !important; min-height: 46px !important; }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus { border-color: #0B3B75 !important; box-shadow: 0 0 0 3px rgba(11,59,117,.15) !important; }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder { color:#475569 !important; opacity:1 !important; }
    .stButton>button { background: #0B3B75 !important; color: #FFFFFF !important; border: 0 !important; border-radius: 14px !important; font-weight: 950 !important; min-height: 46px !important; box-shadow: 0 12px 28px rgba(11,59,117,.20) !important; }
    .stButton>button[kind="primary"], button[kind="primary"] { background: linear-gradient(90deg, #E4B834, #F8DB62) !important; color: #06162F !important; border: 0 !important; font-weight: 950 !important; box-shadow: 0 16px 34px rgba(228,184,52,.28) !important; }
    .stButton>button:hover { filter: brightness(1.06) !important; transform: translateY(-1px); }
    .panel, .card, .project-card, .business-section, .product-card, .table-card, div[data-testid="stMetric"] { background: #FFFFFF !important; color: #081526 !important; border: 2px solid #D7E2F0 !important; box-shadow: 0 16px 38px rgba(15,23,42,.10) !important; }
    .panel *, .card *, .project-card *, .business-section *, .product-card *, .table-card * { color: #081526 !important; }
    .kpi-card { background: #FFFFFF !important; border: 2px solid #D7E2F0 !important; border-top: 6px solid #0B3B75 !important; box-shadow: 0 16px 38px rgba(15,23,42,.10) !important; }
    .kpi-card:nth-child(2) { border-top-color: #E4B834 !important; }
    .kpi-card:nth-child(3) { border-top-color: #16A34A !important; }
    .kpi-card:nth-child(4) { border-top-color: #DC2626 !important; }
    .kpi-label, .kpi-note, .project-meta, .section-subtitle { color:#334155 !important; }
    .kpi-value, .project-title, .section-title { color:#06162F !important; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #06162F 0%, #08285A 100%) !important; }
    section[data-testid="stSidebar"] * { color:#FFFFFF !important; }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { background: rgba(255,255,255,.08) !important; border: 1px solid rgba(255,255,255,.18) !important; border-radius: 12px !important; }
    section[data-testid="stSidebar"] .stButton>button { background: #E4B834 !important; color:#06162F !important; }
    [data-testid="stDataFrame"], [data-testid="stTable"] { background:#FFFFFF !important; color:#081526 !important; border-radius:16px !important; }
    [data-testid="stDataFrame"] * { color:#081526 !important; }
    @media (max-width: 900px) { .login-hero-title-final { font-size: 2rem !important; } .login-hero-final { min-height:auto !important; padding:1.55rem !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# INTERACTION MODULE VISUALS
# =========================================================
st.markdown(
    """
    <style>
    .interaction-card {
        background:#FFFFFF !important;
        border:2px solid #D7E2F0 !important;
        border-left:7px solid #E4B834 !important;
        border-radius:22px !important;
        padding:1rem 1.15rem !important;
        margin:.75rem 0 1rem !important;
        box-shadow:0 14px 32px rgba(15,23,42,.09) !important;
    }
    .interaction-card * { color:#081526 !important; }
    .chat-thread {
        background:#F8FAFC !important;
        border:1px solid #CBD5E1 !important;
        border-radius:20px !important;
        padding:1rem !important;
        margin:.75rem 0 !important;
    }
    .chat-bubble {
        border-radius:18px !important;
        padding:.85rem 1rem !important;
        margin:.45rem 0 !important;
        border:1px solid #CBD5E1 !important;
        line-height:1.55 !important;
    }
    .chat-member { background:#FFFFFF !important; border-left:6px solid #0B3B75 !important; }
    .chat-admin { background:#ECFDF5 !important; border-left:6px solid #16A34A !important; }
    .chat-bot { background:#FFFBEB !important; border-left:6px solid #E4B834 !important; }
    .chat-live-status {
        display:flex; align-items:center; gap:.55rem; flex-wrap:wrap;
        background:#ECFDF5 !important; border:1.5px solid #86EFAC !important; border-left:7px solid #16A34A !important;
        border-radius:18px !important; padding:.75rem 1rem !important; margin:.65rem 0 !important;
        color:#064E3B !important; font-weight:950 !important;
    }
    .chat-live-dot {
        width:12px; height:12px; border-radius:999px; background:#22C55E; display:inline-block;
        box-shadow:0 0 0 6px rgba(34,197,94,.18);
    }
    .chat-alert-badge {
        display:inline-flex; align-items:center; justify-content:center; min-width:28px; height:28px;
        padding:0 .45rem; border-radius:999px; background:#DC2626 !important; color:#FFFFFF !important;
        font-weight:950 !important; box-shadow:0 10px 22px rgba(220,38,38,.25) !important;
    }
    .chat-notify-banner {
        background:#FEF2F2 !important; border:2px solid #FCA5A5 !important; border-left:8px solid #DC2626 !important;
        border-radius:18px !important; padding:.85rem 1rem !important; margin:.7rem 0 !important;
        color:#7F1D1D !important; font-weight:950 !important;
    }
    .chat-notify-banner * { color:#7F1D1D !important; }
    .conversation-row {
        background:#FFFFFF !important; border:1.5px solid #CBD5E1 !important; border-radius:16px !important;
        padding:.7rem .85rem !important; margin:.45rem 0 !important; box-shadow:0 8px 18px rgba(15,23,42,.06) !important;
    }
    .conversation-row * { color:#081526 !important; }
    .small-muted { color:#475569 !important; font-size:.82rem !important; font-weight:750 !important; }
    .ops-card {
        background:#FFFFFF !important; border:2px solid #CBD5E1 !important; border-radius:22px !important;
        padding:1rem 1.15rem !important; margin:.75rem 0 1rem !important; box-shadow:0 16px 34px rgba(15,23,42,.10) !important;
    }
    .ops-card * { color:#081526 !important; }
    .ops-steps { display:flex; gap:.45rem; flex-wrap:wrap; margin:.6rem 0 .2rem; }
    .ops-step { padding:.35rem .65rem; border-radius:999px; background:#E2E8F0; color:#0F172A !important; font-weight:900; font-size:.78rem; }
    .ops-step-done { background:#DCFCE7 !important; color:#14532D !important; }
    .ops-step-current { background:#FEF3C7 !important; color:#92400E !important; }
    .notification-card {
        background:#F8FAFC !important; border:1.5px solid #CBD5E1 !important; border-left:6px solid #1D4ED8 !important;
        border-radius:18px !important; padding:.85rem 1rem !important; margin:.55rem 0 !important;
    }
    .notification-card * { color:#081526 !important; }
    .global-chat-spacer { height: 190px; }
    .floating-chat-panel {
        position: fixed !important;
        right: 1.25rem !important;
        bottom: 5.6rem !important;
        width: min(430px, calc(100vw - 2rem)) !important;
        max-height: 54vh !important;
        overflow-y: auto !important;
        z-index: 999990 !important;
        background:#FFFFFF !important;
        border:2px solid #CBD5E1 !important;
        border-top:7px solid #16A34A !important;
        border-radius:24px !important;
        padding:.9rem 1rem !important;
        box-shadow:0 24px 70px rgba(2,6,23,.28) !important;
    }
    .floating-chat-panel * { color:#081526 !important; }
    .floating-chat-title { display:flex; justify-content:space-between; align-items:center; gap:.75rem; font-weight:950; font-size:1.03rem; }
    .floating-chat-subtitle { color:#475569 !important; font-weight:800; font-size:.82rem; margin:.18rem 0 .55rem; }
    .floating-chat-messages { margin-top:.45rem; }
    .floating-chat-bubble {
        border-radius:16px !important; padding:.58rem .7rem !important; margin:.38rem 0 !important;
        border:1px solid #CBD5E1 !important; font-size:.88rem !important; line-height:1.35 !important;
    }
    .floating-chat-bubble-member { background:#EFF6FF !important; border-left:5px solid #1D4ED8 !important; margin-left:2.1rem !important; }
    .floating-chat-bubble-staff { background:#ECFDF5 !important; border-left:5px solid #16A34A !important; margin-right:2.1rem !important; }
    .floating-chat-bubble-bot { background:#FFFBEB !important; border-left:5px solid #E4B834 !important; margin-right:2.1rem !important; }
    .floating-chat-time { display:block; color:#64748B !important; font-size:.72rem !important; font-weight:800 !important; margin-top:.15rem; }
    .floating-chat-empty { background:#F8FAFC !important; border:1px dashed #94A3B8 !important; border-radius:16px !important; padding:.75rem !important; font-weight:800 !important; }
    .floating-chat-input-note {
        position: fixed !important; right: 1.25rem !important; bottom: 4.25rem !important; z-index:999991 !important;
        width:min(430px, calc(100vw - 2rem)) !important; background:#06162F !important; color:#FFFFFF !important;
        border-radius:999px !important; padding:.38rem .75rem !important; font-weight:900 !important; font-size:.78rem !important;
        box-shadow:0 10px 26px rgba(2,6,23,.18) !important; text-align:center !important;
    }
    .floating-chat-input-note * { color:#FFFFFF !important; }
    @media (max-width: 760px) {
        .floating-chat-panel { left:.65rem !important; right:.65rem !important; bottom:5.2rem !important; width:auto !important; max-height:47vh !important; }
        .floating-chat-input-note { left:.65rem !important; right:.65rem !important; width:auto !important; bottom:4rem !important; }
        .global-chat-spacer { height: 230px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# =========================================================
# PUBLIC LANDING WEBSITE VISUALS
# =========================================================
st.markdown(
    """
    <style>
    .public-topbar {
        position: sticky; top: 0; z-index: 999;
        background:#FFFFFF !important; border:1px solid #E2E8F0 !important;
        border-radius:0 0 22px 22px !important; padding:.75rem 1rem !important;
        box-shadow:0 12px 30px rgba(15,23,42,.10) !important; margin:-1.35rem 0 1rem !important;
        display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap;
    }
    .public-brand { display:flex; align-items:center; gap:.7rem; }
    .public-logo { width:46px; height:46px; border-radius:14px; display:grid; place-items:center;
        background:linear-gradient(135deg,#06162F,#0B3B75); color:#F8DB62 !important; font-weight:950; font-size:1.35rem;
        box-shadow:0 10px 22px rgba(6,22,47,.20);
    }
    .public-brand-title { font-size:1.24rem; font-weight:950; color:#06162F !important; letter-spacing:-.03em; }
    .public-brand-sub { font-size:.78rem; color:#475569 !important; font-weight:850; }
    .public-hero {
        min-height:420px; border-radius:0 0 32px 32px; margin:-1rem 0 1.2rem; padding:4.2rem 2rem 1.25rem; overflow:hidden; position:relative;
        background:
          linear-gradient(180deg, rgba(6,22,47,.18), rgba(6,22,47,.76)),
          radial-gradient(circle at 15% 20%, rgba(248,219,98,.45), transparent 23%),
          linear-gradient(135deg, #06162F 0%, #0B3B75 44%, #057A9C 100%);
        box-shadow:0 28px 70px rgba(6,22,47,.25);
    }
    .public-hero:after { content:""; position:absolute; inset:0; background:linear-gradient(90deg, rgba(255,255,255,.08) 1px, transparent 1px), linear-gradient(rgba(255,255,255,.06) 1px, transparent 1px); background-size:42px 42px; opacity:.28; }
    .public-hero-inner { position:relative; z-index:1; max-width:1120px; }
    .public-hero h1 { color:#FFFFFF !important; font-size:2.75rem; line-height:1.06; letter-spacing:-.05em; font-weight:950; max-width:860px; margin:0 0 .65rem; }
    .public-hero p { color:#EAF6FF !important; font-size:1.08rem; line-height:1.65; max-width:900px; font-weight:650; }
    .public-search { background:#FFFFFF !important; border-radius:999px !important; padding:.85rem 1.2rem !important; max-width:1110px; margin:1.45rem auto 1rem; display:flex; align-items:center; gap:.7rem; box-shadow:0 20px 45px rgba(2,6,23,.24); border:1px solid rgba(255,255,255,.85); }
    .public-search * { color:#475569 !important; font-weight:850; }
    .public-service-grid { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:.8rem; margin:1.15rem 0 .4rem; }
    .public-service-card { background:rgba(6,22,47,.72) !important; border:1px solid rgba(255,255,255,.18); border-radius:20px; padding:.9rem .65rem; min-height:112px; text-align:center; backdrop-filter:blur(10px); box-shadow:0 14px 34px rgba(2,6,23,.20); }
    .public-service-card * { color:#FFFFFF !important; }
    .public-service-icon { font-size:1.65rem; margin-bottom:.25rem; }
    .public-service-title { font-size:.83rem; font-weight:950; line-height:1.25; }
    .public-section { background:#FFFFFF !important; border:1.5px solid #D7E2F0 !important; border-radius:26px; padding:1.25rem 1.35rem; margin:1rem 0; box-shadow:0 16px 38px rgba(15,23,42,.08); }
    .public-section * { color:#081526 !important; }
    .public-section-title { font-size:1.45rem; font-weight:950; color:#06162F !important; letter-spacing:-.035em; margin-bottom:.25rem; }
    .public-section-subtitle { color:#475569 !important; font-weight:750; line-height:1.6; margin-bottom:.75rem; }
    .public-feature-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; }
    .public-feature-card { background:#F8FAFC !important; border:1.5px solid #D7E2F0; border-radius:22px; padding:1.05rem; min-height:170px; border-top:5px solid #0B3B75; }
    .public-feature-card:nth-child(2) { border-top-color:#E4B834; }
    .public-feature-card:nth-child(3) { border-top-color:#16A34A; }
    .public-feature-card:nth-child(4) { border-top-color:#057A9C; }
    .public-feature-card:nth-child(5) { border-top-color:#DC2626; }
    .public-feature-card:nth-child(6) { border-top-color:#7C3AED; }
    .public-feature-card * { color:#081526 !important; }
    .public-feature-icon { font-size:1.8rem; margin-bottom:.25rem; }
    .public-feature-title { font-weight:950; font-size:1.05rem; color:#06162F !important; }
    .public-feature-text { color:#475569 !important; line-height:1.55; font-weight:650; font-size:.9rem; }
    .public-rate-card { background:linear-gradient(135deg,#06162F,#0B3B75) !important; border-radius:26px; padding:1.35rem; box-shadow:0 22px 52px rgba(6,22,47,.22); border:1px solid rgba(255,255,255,.18); }
    .public-rate-card * { color:#FFFFFF !important; }
    .public-rate-value { font-size:2.1rem; font-weight:950; color:#F8DB62 !important; letter-spacing:-.04em; }
    .public-muted { color:#EAF6FF !important; line-height:1.6; font-weight:650; }
    .demo-rate-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.75rem; margin-top:1rem; }
    .demo-rate-box { background:rgba(255,255,255,.12) !important; border:1px solid rgba(255,255,255,.28); border-radius:18px; padding:.85rem; }
    .demo-rate-name { font-weight:950; font-size:.96rem; }
    .demo-rate-percent { font-size:1.55rem; font-weight:950; color:#F8DB62 !important; margin:.2rem 0; }
    .demo-rate-small { color:#EAF6FF !important; font-size:.82rem; line-height:1.45; font-weight:700; }
    .public-flow-grid { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:.75rem; margin-top:.9rem; }
    .public-flow-card { background:#F8FAFC !important; border:1.5px solid #D7E2F0; border-radius:18px; padding:.9rem .75rem; min-height:142px; }
    .public-flow-number { width:30px; height:30px; border-radius:999px; display:grid; place-items:center; background:#0B3B75 !important; color:#FFFFFF !important; font-weight:950; margin-bottom:.45rem; }
    .public-flow-title { font-weight:950; color:#06162F !important; font-size:.95rem; }
    .public-flow-text { color:#475569 !important; line-height:1.45; font-size:.82rem; font-weight:650; margin-top:.25rem; }
    .public-demo-strip { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.85rem; margin:1rem 0; }
    .public-demo-stat { background:#FFFFFF !important; border:1.5px solid #D7E2F0; border-radius:20px; padding:1rem; box-shadow:0 14px 34px rgba(15,23,42,.07); }
    .public-demo-stat .label { color:#64748B !important; font-weight:850; font-size:.82rem; }
    .public-demo-stat .value { color:#06162F !important; font-weight:950; font-size:1.35rem; margin-top:.25rem; }
    .public-demo-stat .note { color:#475569 !important; font-weight:650; font-size:.82rem; margin-top:.25rem; }
    .public-footer { background:#06162F !important; border-radius:26px 26px 0 0; padding:1.4rem; margin:1.5rem 0 -2rem; }
    .public-footer * { color:#FFFFFF !important; }
    @media (max-width: 1000px) { .public-service-grid { grid-template-columns:repeat(3,minmax(0,1fr)); } .public-feature-grid { grid-template-columns:1fr 1fr; } .public-flow-grid { grid-template-columns:repeat(3,minmax(0,1fr)); } .demo-rate-grid, .public-demo-strip { grid-template-columns:1fr 1fr; } .public-hero h1 { font-size:2.1rem; } }
    @media (max-width: 640px) { .public-service-grid, .public-feature-grid, .public-flow-grid, .demo-rate-grid, .public-demo-strip { grid-template-columns:1fr; } .public-hero { padding:2.8rem 1rem 1rem; } .public-hero h1 { font-size:1.75rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DATABASE HELPERS
# =========================================================
def esc(value):
    return html.escape("" if value is None else str(value))


def render_html(markup: str):
    """Render HTML safely without Markdown treating indented tags as code blocks."""
    st.markdown(textwrap.dedent(markup).strip(), unsafe_allow_html=True)


def money(value):
    try:
        return f"KES {float(value):,.0f}"
    except Exception:
        return "KES 0"


def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256((password or "").encode("utf-8")).hexdigest()


def execute(sql: str, params=()):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid


def execute_many(sql: str, rows):
    with connect() as conn:
        conn.executemany(sql, rows)
        conn.commit()


def query_df(sql: str, params=()):
    with connect() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def fetch_one(sql: str, params=()):
    with connect() as conn:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None


def table_count(table: str) -> int:
    with connect() as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def init_db():
    with connect() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                member_role TEXT DEFAULT 'Standard Member',
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS login_tokens (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_used_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                location TEXT DEFAULT 'Nakuru',
                status TEXT DEFAULT 'Upcoming',
                visibility TEXT DEFAULT 'Members Only',
                start_date TEXT,
                end_date TEXT,
                vision TEXT,
                goal TEXT,
                team_summary TEXT,
                executive_summary TEXT,
                idea_description TEXT,
                market_analysis TEXT,
                organization_management TEXT,
                products_summary TEXT,
                marketing_strategy TEXT,
                financial_plan TEXT,
                operational_plan TEXT,
                budget_target REAL DEFAULT 0,
                funding_required REAL DEFAULT 0,
                expected_revenue REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                project_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                price REAL DEFAULT 0,
                status TEXT DEFAULT 'Active',
                image_hint TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                tx_type TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT,
                tx_date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                active INTEGER DEFAULT 1
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS investment_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT DEFAULT 'M-Pesa',
                mpesa_number TEXT,
                payment_phone TEXT,
                account_name TEXT,
                mpesa_receipt TEXT,
                receipt_file TEXT,
                payment_date TEXT,
                payment_details TEXT,
                member_note TEXT,
                status TEXT DEFAULT 'Submitted',
                admin_label TEXT DEFAULT 'New',
                admin_note TEXT,
                reviewed_by INTEGER,
                reviewed_at TEXT,
                finance_tx_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id),
                FOREIGN KEY(member_id) REFERENCES users(id),
                FOREIGN KEY(reviewed_by) REFERENCES users(id),
                FOREIGN KEY(finance_tx_id) REFERENCES transactions(id)
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                sender_role TEXT,
                sender_name TEXT,
                message_text TEXT NOT NULL,
                is_auto INTEGER DEFAULT 0,
                admin_reply_to_id INTEGER,
                handled_by INTEGER,
                status TEXT DEFAULT 'Open',
                staff_read_at TEXT,
                member_read_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(sender_id) REFERENCES users(id),
                FOREIGN KEY(admin_reply_to_id) REFERENCES chat_messages(id),
                FOREIGN KEY(handled_by) REFERENCES users(id)
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS people_directory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                role_title TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                note TEXT,
                visible_to_members INTEGER DEFAULT 1,
                added_by INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(added_by) REFERENCES users(id)
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS investment_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                investment_request_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                old_status TEXT,
                new_status TEXT,
                note TEXT,
                actor_id INTEGER,
                actor_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(investment_request_id) REFERENCES investment_requests(id),
                FOREIGN KEY(actor_id) REFERENCES users(id)
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT,
                category TEXT DEFAULT 'General',
                related_id INTEGER,
                is_read INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(member_id) REFERENCES users(id)
            )
            """
        )
        chat_cols = {row[1] for row in c.execute("PRAGMA table_info(chat_messages)").fetchall()}
        if "staff_read_at" not in chat_cols:
            c.execute("ALTER TABLE chat_messages ADD COLUMN staff_read_at TEXT")
        if "member_read_at" not in chat_cols:
            c.execute("ALTER TABLE chat_messages ADD COLUMN member_read_at TEXT")

        user_cols = {row[1] for row in c.execute("PRAGMA table_info(users)").fetchall()}
        if "member_role" not in user_cols:
            c.execute("ALTER TABLE users ADD COLUMN member_role TEXT DEFAULT 'Standard Member'")
        conn.commit()
    seed_defaults()
    migrate_chairman_role()
    ensure_public_website_demo_content()
    reset_editable_records_once()
    auto_close_projects()


def reset_editable_records_once():
    """
    One-time clean reset for v24.
    Removes user/member-created operational records while preserving the app structure,
    staff/admin accounts, projects, products, milestones, FAQs, settings, contacts, and assets.
    """
    marker_key = "editable_records_reset_v24_done"
    if get_setting(marker_key, "") == "yes":
        return

    with connect() as conn:
        c = conn.cursor()

        # Delete any finance transactions that were created from accepted investment requests.
        finance_ids = [
            row[0]
            for row in c.execute(
                "SELECT finance_tx_id FROM investment_requests WHERE finance_tx_id IS NOT NULL"
            ).fetchall()
            if row[0] is not None
        ]
        if finance_ids:
            placeholders = ",".join(["?"] * len(finance_ids))
            c.execute(f"DELETE FROM transactions WHERE id IN ({placeholders})", finance_ids)

        # Clear editable/member operational records.
        c.execute("DELETE FROM investment_activity")
        c.execute("DELETE FROM investment_requests")
        c.execute("DELETE FROM notifications")
        c.execute("DELETE FROM chat_messages")

        # Remove login tokens because member accounts are being reset.
        c.execute("DELETE FROM login_tokens")

        # Remove all Member accounts, including pending/rejected/abandoned/suspended/demo members.
        c.execute("DELETE FROM users WHERE role='Member'")

        # Keep the reset marker so the app does not keep wiping newly-created records.
        c.execute(
            "INSERT INTO settings(setting_key, setting_value) VALUES(?, ?) "
            "ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value",
            (marker_key, "yes"),
        )
        conn.commit()

    # Best-effort cleanup of uploaded receipt files.
    try:
        for receipt_path in RECEIPTS_DIR.glob("*"):
            if receipt_path.is_file():
                receipt_path.unlink()
    except Exception:
        pass


def get_project_id_by_code(code: str):
    row = fetch_one("SELECT id FROM projects WHERE code=?", (code,))
    return row["id"] if row else None


def seed_defaults():
    if table_count("users") == 0:
        users = [
            ("chairman", hash_password("chairman123"), "Chairman", "Zacharia Thinji", "zachariathinji@gmail.com", "+254790240112", "active"),
            ("manager", hash_password("manager123"), "Manager", "Zenvest Manager", "", "", "active"),
            ("secretary", hash_password("secretary123"), "Secretary", "Zenvest Secretary", "", "", "active"),
        ]
        execute_many("INSERT INTO users(username,password_hash,role,full_name,email,phone,status) VALUES(?,?,?,?,?,?,?)", users)

    if table_count("settings") == 0:
        settings = [
            ("company_name", "Zenvest Investment Holdings"),
            ("whatsapp", "+254790240112"),
            ("chairman_email", "zachariathinji@gmail.com"),
            ("support_message", "Our support team will respond shortly. If the chatbot cannot answer, contact us by WhatsApp or email."),
            ("business_hours", "Monday to Saturday, 8:00 AM to 6:00 PM"),
            ("portal_slogan", "Structured projects, transparent performance, and shareholder growth."),
            ("support_staff_user_id", ""),
        ]
        execute_many("INSERT INTO settings(setting_key, setting_value) VALUES(?,?)", settings)

    required_settings = [
        ("mpesa_till_paybill", "Add official Till/Paybill here"),
        ("mpesa_account_name", "Zenvest Investment Holdings"),
        ("mpesa_account_number", "Use project code or member username as account reference"),
        ("payment_instructions", "Pay using the official Zenvest M-Pesa/Till/Paybill, then submit amount, sender number, receipt/reference, and receipt upload for admin verification."),
        ("chat_online_note", "Simple chat: type in the message bar and press Enter. No extra send button is needed."),
        ("support_staff_user_id", ""),
        ("public_hero_title", "Investment opportunities, products and performance in one secure portal"),
        ("public_hero_subtitle", "Explore sample investment plans, public project previews, products, performance highlights, support contacts, and registration before entering the protected member portal."),
        ("public_investment_rate", "Starter 8%–12% · Balanced 13%–18% · Expansion 19%–25%"),
        ("public_rate_note", "Public demo profit examples: KES 10,000 at 8%–12% may show KES 800–1,200; KES 25,000 at 13%–18% may show KES 3,250–4,500; KES 50,000 at 19%–25% may show KES 9,500–12,500. Actual project terms are shown per opportunity before a member submits payment."),
        ("public_about", "Zenvest Investment Holdings is a structured investment and project-management portal that presents public opportunities, products, performance summaries, member registration, secure payment verification, and accountable support in one place."),
        ("public_services_intro", "Visitors can view public investment categories, sample returns, products, project previews, performance summaries, and support information. Private actions such as investing, submitting payment receipts, and viewing account records require secure login."),
    ]
    execute_many("INSERT OR IGNORE INTO settings(setting_key, setting_value) VALUES(?,?)", required_settings)

    if table_count("projects") == 0:
        today = date.today()
        end = date(today.year, 12, 31)
        execute(
            """
            INSERT INTO projects(
                code,title,location,status,visibility,start_date,end_date,vision,goal,team_summary,
                executive_summary,idea_description,market_analysis,organization_management,products_summary,
                marketing_strategy,financial_plan,operational_plan,budget_target,funding_required,expected_revenue
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                "PRJ-001",
                "Nakuru Business Expansion Plan",
                "Nakuru",
                "Active",
                "Members Only",
                str(today),
                str(end),
                "To build a trusted investment and business-growth platform that connects members, products, projects, and long-term value creation.",
                "To present upcoming investment projects, monitor their performance, and convert completed projects into transparent success or profit/loss records.",
                "The project is led by the Zenvest Chairman with support from the Manager, Secretary, and operational team.",
                "This project introduces a structured business opportunity in Nakuru with clear goals, management accountability, financial monitoring, product visibility, and investor communication.",
                "The business idea is based in Nakuru and designed as a scalable investment project. It combines business planning, product/service display, market positioning, performance tracking, and investor reporting into one live portal.",
                "The opportunity is positioned between company capability, customer value, and competitor gaps. It focuses on unique value, strong management, clear product offers, and transparent performance reporting.",
                "The organization is structured around a Chairman, Manager, Secretary, members, and operational contributors. Each role supports project control, records, updates, accountability, and member communication.",
                "Products and services are controlled dynamically from the staff panel. Active products appear to members/customers, while paused, expired, or removed products are hidden from public display but retained for internal records.",
                "Marketing will focus on investor confidence, customer trust, partnership building, product visibility, fair pricing, and long-term customer retention.",
                "The financial plan tracks budget, funding requirements, revenue forecast, cash flow, expenses, profit/loss, and performance progress using live dashboard infographics.",
                "The operational plan covers execution, location, suppliers/vendors, equipment, daily operations, production process, milestones, and timeline management.",
                500000,
                350000,
                750000,
            ),
        )

    if table_count("products") == 0:
        pid = get_project_id_by_code("PRJ-001") or 1
        products = [
            ("PRD-001", pid, "Investment Membership Package", "Member participation package linked to upcoming Zenvest projects.", 10000, "Active", "membership package"),
            ("PRD-002", pid, "Business Project Share Unit", "Share-style project unit for members interested in selected business opportunities.", 25000, "Active", "investment unit"),
            ("PRD-003", pid, "Product Showcase Slot", "Admin-controlled product/service display slot for future products added to the portal.", 5000, "Paused", "future product"),
        ]
        execute_many("INSERT INTO products(code,project_id,name,description,price,status,image_hint) VALUES(?,?,?,?,?,?,?)", products)

    if table_count("transactions") == 0:
        pid = get_project_id_by_code("PRJ-001") or 1
        txs = [
            (pid, "Funding", 125000, "Initial member funding", str(date.today())),
            (pid, "Revenue", 85000, "Early sales/returns", str(date.today())),
            (pid, "Expense", 42000, "Operations and setup costs", str(date.today())),
        ]
        execute_many("INSERT INTO transactions(project_id,tx_type,amount,note,tx_date) VALUES(?,?,?,?,?)", txs)

    if table_count("milestones") == 0:
        pid = get_project_id_by_code("PRJ-001") or 1
        milestones = [
            (pid, "Business plan approved", "Chairman and staff review the business plan outline.", str(date.today()), "Completed"),
            (pid, "Product list launched", "Active products/services are added to the portal.", str(date.today()), "In Progress"),
            (pid, "Funding target review", "Review funding raised against the target.", str(date.today()), "Pending"),
        ]
        execute_many("INSERT INTO milestones(project_id,title,description,due_date,status) VALUES(?,?,?,?,?)", milestones)

    if table_count("faqs") == 0:
        faqs = [
            ("How can I invest?", "Log in as a member, open Investment Opportunities, choose a project, press the investment form, accept the opportunity, enter the amount, M-Pesa number, receipt/reference, and submit it for admin review.", 1),
            ("Where is the business located?", "The current business/project location is Nakuru.", 1),
            ("How do I contact support?", "Use the Support Chatbot send button. Your message will reach the Customer Support panel. You can also use WhatsApp +254790240112 or email the chairman.", 1),
            ("Can products change?", "Yes. Products are managed by staff and automatically update when active, paused, expired, or removed.", 1),
            ("How do I know my payment was received?", "After you submit payment details, staff can mark it as Seen, Payment Received, Accepted, More Info Needed, or Rejected. You can track the status under My Investments.", 1),
        ]
        execute_many("INSERT INTO faqs(question,answer,active) VALUES(?,?,?)", faqs)

    if table_count("people_directory") == 0:
        chairman = fetch_one("SELECT id FROM users WHERE username='chairman'")
        chairman_id = chairman["id"] if chairman else None
        people = [
            ("Zacharia Thinji", "Chairman / Chairman", "+254790240112", "zachariathinji@gmail.com", "Main leadership and investment contact.", 1, chairman_id),
            ("Zenvest Manager", "Manager", "", "", "Receives member messages and payment follow-ups.", 1, chairman_id),
            ("Zenvest Secretary", "Secretary", "", "", "Supports member records and communication.", 1, chairman_id),
        ]
        execute_many("INSERT INTO people_directory(full_name,role_title,phone,email,note,visible_to_members,added_by) VALUES(?,?,?,?,?,?,?)", people)


# =========================================================
# SETTINGS / AUTH HELPERS
# =========================================================
def get_setting(key: str, default=""):
    row = fetch_one("SELECT setting_value FROM settings WHERE setting_key=?", (key,))
    return row["setting_value"] if row else default


def update_setting(key: str, value: str):
    execute("INSERT INTO settings(setting_key,setting_value) VALUES(?,?) ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value", (key, value))


def ensure_public_website_demo_content():
    """Replace old placeholder public text with complete visitor-ready demo content."""
    defaults = {
        "public_hero_title": "Investment opportunities, products and performance in one secure portal",
        "public_hero_subtitle": "Explore sample investment plans, public project previews, products, performance highlights, support contacts, and registration before entering the protected member portal.",
        "public_investment_rate": "Starter 8%–12% · Balanced 13%–18% · Expansion 19%–25%",
        "public_rate_note": "Public demo profit examples: KES 10,000 at 8%–12% may show KES 800–1,200; KES 25,000 at 13%–18% may show KES 3,250–4,500; KES 50,000 at 19%–25% may show KES 9,500–12,500. Actual project terms are shown per opportunity before a member submits payment.",
        "public_about": "Zenvest Investment Holdings is a structured investment and project-management portal that presents public opportunities, products, performance summaries, member registration, secure payment verification, and accountable support in one place.",
        "public_services_intro": "Visitors can view public investment categories, sample returns, products, project previews, performance summaries, and support information. Private actions such as investing, submitting payment receipts, and viewing account records require secure login.",
    }
    placeholder_words = ["Admin editable", "can be edited", "rate / return guidance", "Public rates are indicative"]
    for key, value in defaults.items():
        current = get_setting(key, "")
        if not current or any(word.lower() in current.lower() for word in placeholder_words):
            update_setting(key, value)


def auto_close_projects():
    today = date.today().isoformat()
    execute("UPDATE projects SET status='Passed' WHERE end_date IS NOT NULL AND end_date < ? AND status NOT IN ('Completed','Passed','Cancelled')", (today,))


def authenticate(login_value: str, password: str, allowed_roles=None):
    """Authenticate by username OR email. Only active accounts can sign in."""
    login_value = (login_value or "").strip()
    if not login_value:
        return None
    row = fetch_one(
        """
        SELECT * FROM users
        WHERE status='active'
          AND (lower(username)=lower(?) OR (email IS NOT NULL AND email!='' AND lower(email)=lower(?)))
        ORDER BY CASE WHEN lower(username)=lower(?) THEN 0 ELSE 1 END
        LIMIT 1
        """,
        (login_value, login_value, login_value),
    )
    if not row:
        return None
    if row["password_hash"] != hash_password(password):
        return None
    if allowed_roles and row["role"] not in allowed_roles:
        return None
    return row


def qp_get(key: str, default=""):
    try:
        return st.query_params.get(key, default)
    except Exception:
        try:
            return st.experimental_get_query_params().get(key, [default])[0]
        except Exception:
            return default


def qp_set(**kwargs):
    """Set query params while keeping existing ones unless explicitly removed."""
    try:
        for k, v in kwargs.items():
            if v is None:
                if k in st.query_params:
                    del st.query_params[k]
            else:
                st.query_params[k] = str(v)
    except Exception:
        params = {}
        try:
            params = dict(st.experimental_get_query_params())
        except Exception:
            params = {}
        for k, v in kwargs.items():
            if v is None:
                params.pop(k, None)
            else:
                params[k] = [str(v)]
        try:
            st.experimental_set_query_params(**{k: (v[0] if isinstance(v, list) else v) for k, v in params.items()})
        except Exception:
            pass


def create_login_token(user_id: int) -> str:
    token = uuid.uuid4().hex + uuid.uuid4().hex
    execute("INSERT INTO login_tokens(token,user_id,last_used_at) VALUES(?,?,?)", (token, int(user_id), utc_now_text()))
    return token


def restore_user_from_token():
    token = (qp_get("auth", "") or "").strip()
    if not token:
        return None
    row = fetch_one(
        """
        SELECT u.* FROM login_tokens lt
        JOIN users u ON u.id=lt.user_id
        WHERE lt.token=? AND u.status='active'
        LIMIT 1
        """,
        (token,),
    )
    if row:
        execute("UPDATE login_tokens SET last_used_at=? WHERE token=?", (utc_now_text(), token))
    return row


def remember_login(user):
    st.session_state["user"] = user
    token = create_login_token(int(user["id"]))
    qp_set(auth=token)


def current_user():
    user = st.session_state.get("user")
    if user:
        return user
    user = restore_user_from_token()
    if user:
        st.session_state["user"] = user
    return user


def logout():
    token = (qp_get("auth", "") or "").strip()
    if token:
        execute("DELETE FROM login_tokens WHERE token=?", (token,))
    st.session_state.pop("user", None)
    qp_set(auth=None, page=None, project_id=None, chat_id=None)
    st.rerun()


def is_staff(user):
    return bool(user and user.get("role") in ["Chairman", "Manager", "Secretary"])


def can_manage_staff(user):
    return bool(user and user.get("role") == "Chairman")


def staff_role_names():
    return ["Chairman", "Manager", "Secretary"]


def member_role_options():
    """Business-facing member categories used by staff to classify members without changing system access."""
    return [
        "Standard Member",
        "Investment Member",
        "Premium Investor",
        "VIP Investor",
        "Project Partner",
        "Prospective Member",
        "Dormant / Monitoring",
    ]


def member_role_badge(role_name: str):
    role_name = role_name or "Standard Member"
    return f'<span class="status-badge">{esc(role_name)}</span>'


def table_exists(table_name: str) -> bool:
    """Return True if a SQLite table exists in the current database."""
    row = fetch_one("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return bool(row)


def ensure_people_directory_table():
    """Create the names/contact directory table and migrate old typo table if present."""
    execute(
        """
        CREATE TABLE IF NOT EXISTS people_directory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            role_title TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            note TEXT,
            visible_to_members INTEGER DEFAULT 1,
            added_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(added_by) REFERENCES users(id)
        )
        """
    )
    # v28 briefly used an accidental table name. Keep existing records if someone already ran that version.
    if table_exists("people_directory"):
        execute(
            """
            INSERT INTO people_directory(full_name, role_title, phone, email, note, visible_to_members, added_by, created_at)
            SELECT full_name, role_title, phone, email, note, visible_to_members, added_by, created_at
            FROM people_directory
            WHERE NOT EXISTS (
                SELECT 1 FROM people_directory pd
                WHERE pd.full_name=people_directory.full_name
                  AND pd.role_title=people_directory.role_title
                  AND IFNULL(pd.email,'')=IFNULL(people_directory.email,'')
            )
            """
        )


def migrate_chairman_role():
    """Upgrade older databases from Director/director to Chairman/chairman without losing records."""
    ensure_people_directory_table()
    execute("UPDATE users SET role='Chairman' WHERE role='Director'")
    existing_chairman = fetch_one("SELECT id FROM users WHERE lower(username)='chairman' LIMIT 1")
    old_director = fetch_one("SELECT id FROM users WHERE lower(username)='director' LIMIT 1")
    if old_director and not existing_chairman:
        execute("UPDATE users SET username='chairman', password_hash=? WHERE id=?", (hash_password("chairman123"), int(old_director["id"])))
    execute("UPDATE people_directory SET role_title=REPLACE(role_title, 'Director', 'Chairman') WHERE role_title LIKE '%Director%'")


def get_support_staff_id():
    """Return the staff user selected by the Chairman to handle customer support replies."""
    saved = (get_setting("support_staff_user_id", "") or "").strip()
    if saved.isdigit():
        row = fetch_one("SELECT id FROM users WHERE id=? AND role IN ('Chairman','Manager','Secretary') AND status='active'", (int(saved),))
        if row:
            return int(row["id"])
    row = fetch_one("SELECT id FROM users WHERE role='Manager' AND status='active' ORDER BY id LIMIT 1")
    if not row:
        row = fetch_one("SELECT id FROM users WHERE role='Chairman' AND status='active' ORDER BY id LIMIT 1")
    if not row:
        row = fetch_one("SELECT id FROM users WHERE role='Secretary' AND status='active' ORDER BY id LIMIT 1")
    if row:
        update_setting("support_staff_user_id", str(int(row["id"])))
        return int(row["id"])
    return None


def support_staff_label():
    sid = get_support_staff_id()
    if not sid:
        return "Not assigned"
    row = fetch_one("SELECT full_name, role FROM users WHERE id=?", (sid,))
    if not row:
        return "Not assigned"
    return f"{row['full_name']} ({row['role']})"


def can_reply_support(user):
    """Only the Chairman-selected customer-support admin can reply to public/member chats."""
    return bool(user and get_support_staff_id() == int(user["id"]))


def set_page(page_key: str, **extra):
    payload = {"page": page_key}
    payload.update(extra)
    qp_set(**payload)


def quick_nav_button(label: str, page_key: str, key: str, **extra):
    if st.button(label, key=key, use_container_width=True):
        set_page(page_key, **extra)
        st.rerun()


def nav_index(page_key: str, keys: list[str], default_index: int = 0):
    try:
        return keys.index(page_key)
    except Exception:
        return default_index


# =========================================================
# DISPLAY COMPONENTS
# =========================================================
def status_badge(status: str):
    s = (status or "").lower()
    if s in ["active", "completed", "passed", "success", "received", "payment received", "accepted", "replied", "closed"]:
        cls = "badge-green"
    elif s in ["upcoming", "in progress", "pending", "paused", "ending soon", "submitted", "seen", "new", "open", "more info needed", "receipt checked"]:
        cls = "badge-orange"
    elif s in ["cancelled", "loss", "expired", "removed", "rejected"]:
        cls = "badge-red"
    else:
        cls = "badge-gray"
    return f'<span class="badge {cls}">{esc(status or "Unknown")}</span>'


def role_badge(role: str):
    return f'<span class="badge badge-blue">{esc(role)}</span>'


def hero(title, subtitle="", chips=None):
    chip_html = "".join([f'<span class="hero-chip">{esc(c)}</span>' for c in (chips or [])])
    render_html(f'''
<div class="hero">
  <div class="hero-title">{esc(title)}</div>
  <div class="hero-subtitle">{esc(subtitle)}</div>
  <div>{chip_html}</div>
</div>
''')


def kpi_grid(items):
    cards = []
    for icon, label, value, note in items:
        cards.append(
            f'<div class="kpi-card">'
            f'<div class="kpi-icon">{esc(icon)}</div>'
            f'<div class="kpi-label">{esc(label)}</div>'
            f'<div class="kpi-value">{esc(value)}</div>'
            f'<div class="kpi-note">{esc(note)}</div>'
            f'</div>'
        )
    render_html('<div class="kpi-grid">' + ''.join(cards) + '</div>')


def panel(title=None, body=None):
    title_html = f'<div class="section-title">{esc(title)}</div>' if title else ""
    body_html = f'<div style="color:#475569; line-height:1.65;">{esc(body)}</div>' if body else ""
    render_html(f'<div class="panel">{title_html}{body_html}</div>')


def business_section(title, text):
    render_html(f'''
<div class="business-section">
  <h3>{esc(title)}</h3>
  <p>{esc(text or 'Not added yet.')}</p>
</div>
''')


def data_card(title, value, note=""):
    render_html(f'''
<div class="card">
  <div class="kpi-label">{esc(title)}</div>
  <div class="kpi-value">{esc(value)}</div>
  <div class="kpi-note">{esc(note)}</div>
</div>
''')

def get_project(project_id: int):
    return fetch_one("SELECT * FROM projects WHERE id=?", (project_id,))


def project_list(include_all=False):
    if include_all:
        return query_df("SELECT id, code, title FROM projects ORDER BY created_at DESC")
    return query_df("SELECT id, code, title FROM projects WHERE status NOT IN ('Cancelled') ORDER BY created_at DESC")


def project_selectbox(label="Select project", include_all=True, key=None):
    df = project_list(include_all=include_all)
    if df.empty:
        st.info("No project exists yet.")
        return None
    labels = [f"{r['code']} — {r['title']}" for _, r in df.iterrows()]
    selected = st.selectbox(label, labels, key=key)
    return int(df.iloc[labels.index(selected)]["id"])


def get_project_performance(project_id: int):
    df = query_df("SELECT tx_type, amount FROM transactions WHERE project_id=?", (project_id,))
    if df.empty:
        return 0, 0, 0, 0
    funding = float(df.loc[df["tx_type"] == "Funding", "amount"].sum())
    revenue = float(df.loc[df["tx_type"] == "Revenue", "amount"].sum())
    expense = float(df.loc[df["tx_type"] == "Expense", "amount"].sum())
    net = revenue - expense
    return funding, revenue, expense, net


def funding_progress(project, funding):
    target = float(project.get("funding_required") or project.get("budget_target") or 0)
    if target <= 0:
        return 0
    return min(max(funding / target, 0), 1)


def days_remaining(end_date):
    if not end_date:
        return None
    try:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        return (end - date.today()).days
    except Exception:
        return None


def project_card(project, show_button=False, button_label="Open project", staff_view=False, key_prefix="project"):
    funding, revenue, expense, net = get_project_performance(int(project["id"]))
    progress = funding_progress(project, funding)
    days = days_remaining(project.get("end_date"))
    result_badge = status_badge("Profit" if net > 0 else "Loss" if net < 0 else "Break-even")
    time_text = str(days) + " days left" if days is not None and days >= 0 else "Ended" if days is not None else "Not set"
    render_html(f'''
<div class="project-card">
  <div class="project-meta">{esc(project['code'])} · {esc(project.get('location') or 'Nakuru')} · Expected end: {esc(project.get('end_date') or 'Not set')}</div>
  <div class="project-title">{esc(project['title'])}</div>
  <div>{status_badge(project.get('status'))}{status_badge(project.get('visibility'))}{result_badge}</div>
  <p style="color:#475569; line-height:1.6; margin:.75rem 0;">{esc(project.get('executive_summary') or project.get('goal') or '')}</p>
  <div style="height:10px; background:#E2E8F0; border-radius:999px; overflow:hidden; margin:.8rem 0;">
    <div style="height:10px; width:{progress*100:.1f}%; background:linear-gradient(90deg, #D4AF37, #0A8CAD); border-radius:999px;"></div>
  </div>
  <div style="display:flex; gap:1rem; flex-wrap:wrap; color:#334155; font-weight:750; font-size:.9rem;">
    <span>Funding: {esc(money(funding))}</span>
    <span>Target: {esc(money(project.get('funding_required') or project.get('budget_target') or 0))}</span>
    <span>Revenue: {esc(money(revenue))}</span>
    <span>Expenses: {esc(money(expense))}</span>
    <span>Net: {esc(money(net))}</span>
    <span>Time: {esc(time_text)}</span>
  </div>
</div>
''')
    if show_button:
        if st.button(button_label, key=f"{key_prefix}_{project['id']}"):
            st.session_state["selected_project_id"] = int(project["id"])
            target_page = "projects" if staff_view else "opportunities"
            set_page(target_page, project_id=int(project["id"]))
            st.rerun()



# =========================================================
# INVESTMENT REQUEST / PAYMENT HELPERS
# =========================================================
def save_uploaded_receipt(uploaded_file, member_id, project_id):
    if uploaded_file is None:
        return ""
    safe_name = Path(uploaded_file.name).name.replace(" ", "_")
    unique_name = f"receipt_m{member_id}_p{project_id}_{uuid.uuid4().hex[:10]}_{safe_name}"
    path = RECEIPTS_DIR / unique_name
    path.write_bytes(uploaded_file.getbuffer())
    return str(path.relative_to(BASE_DIR))


def get_investment_requests(where="", params=()):
    sql = """
        SELECT ir.*, pr.code AS project_code, pr.title AS project_title,
               u.full_name AS member_name, u.username AS member_username,
               u.email AS member_email, u.phone AS member_registered_phone,
               reviewer.full_name AS reviewed_by_name
        FROM investment_requests ir
        JOIN projects pr ON pr.id = ir.project_id
        JOIN users u ON u.id = ir.member_id
        LEFT JOIN users reviewer ON reviewer.id = ir.reviewed_by
    """
    if where:
        sql += " WHERE " + where
    sql += " ORDER BY ir.created_at DESC"
    return query_df(sql, params)



def create_notification(member_id, title, body, category="General", related_id=None):
    if not member_id:
        return None
    return execute(
        """
        INSERT INTO notifications(member_id,title,body,category,related_id,is_read)
        VALUES(?,?,?,?,?,0)
        """,
        (int(member_id), title, body, category, related_id),
    )


def get_member_notifications(member_id, unread_only=False, limit=10):
    where = "member_id=?"
    params = [int(member_id)]
    if unread_only:
        where += " AND is_read=0"
    return query_df(
        f"SELECT * FROM notifications WHERE {where} ORDER BY created_at DESC LIMIT ?",
        tuple(params + [int(limit)]),
    )


def mark_member_notifications_read(member_id):
    execute("UPDATE notifications SET is_read=1 WHERE member_id=?", (int(member_id),))


def log_investment_activity(request_id, action, old_status, new_status, note, actor):
    actor_id = int(actor["id"]) if actor and actor.get("id") else None
    actor_name = actor.get("full_name") if actor else "System"
    return execute(
        """
        INSERT INTO investment_activity(investment_request_id,action,old_status,new_status,note,actor_id,actor_name)
        VALUES(?,?,?,?,?,?,?)
        """,
        (int(request_id), action, old_status, new_status, note, actor_id, actor_name),
    )


def get_investment_activity(request_id):
    return query_df(
        "SELECT * FROM investment_activity WHERE investment_request_id=? ORDER BY created_at ASC, id ASC",
        (int(request_id),),
    )


def investment_status_flow(current_status):
    steps = ["Submitted", "Seen", "Receipt Checked", "Payment Received", "Accepted"]
    current = current_status if current_status in steps else "Submitted"
    try:
        idx = steps.index(current)
    except ValueError:
        idx = 0
    html_steps = []
    for i, step in enumerate(steps):
        cls = "ops-step-done" if i < idx else "ops-step-current" if i == idx else ""
        html_steps.append(f'<span class="ops-step {cls}">{esc(step)}</span>')
    return '<div class="ops-steps">' + ''.join(html_steps) + '</div>'


def update_investment_request(row, new_status, actor, admin_label=None, admin_note="", record_funding=False, action="Status update"):
    row = dict(row)
    old_status = row.get("status") or "Submitted"
    request_id = int(row["id"])
    member_id = int(row["member_id"])
    project_id = int(row["project_id"])
    admin_label = admin_label or new_status
    finance_tx_id = row.get("finance_tx_id")
    if pd.isna(finance_tx_id):
        finance_tx_id = None
    note_text = admin_note if admin_note is not None else (row.get("admin_note") or "")

    if record_funding and not finance_tx_id and new_status in ["Payment Received", "Received", "Accepted"]:
        finance_tx_id = execute(
            "INSERT INTO transactions(project_id, tx_type, amount, note, tx_date) VALUES(?,?,?,?,?)",
            (
                project_id,
                "Funding",
                float(row.get("amount") or 0),
                f"Investment request #{request_id}: {row.get('member_name','Member')} - {admin_label}",
                row.get("payment_date") or str(date.today()),
            ),
        )

    reviewed_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    execute(
        """
        UPDATE investment_requests
        SET status=?, admin_label=?, admin_note=?, reviewed_by=?, reviewed_at=?, finance_tx_id=?
        WHERE id=?
        """,
        (new_status, admin_label, note_text, int(actor["id"]), reviewed_at, finance_tx_id, request_id),
    )
    log_investment_activity(request_id, action, old_status, new_status, note_text, actor)

    title = f"Investment {new_status}"
    body = f"Your investment request #{request_id} for {row.get('project_code')} ({money(row.get('amount') or 0)}) is now marked as {new_status}."
    if note_text:
        body += f" Admin note: {note_text}"
    create_notification(member_id, title, body, category="Investment", related_id=request_id)
    return finance_tx_id


def quick_investment_operation_buttons(row, user, note_key_prefix="inv_note"):
    row = dict(row)
    request_id = int(row["id"])
    default_note = row.get("admin_note") or ""
    st.markdown("**One-click operations**")
    note = st.text_area("Optional admin note used for the button you click", value=default_note, key=f"{note_key_prefix}_{request_id}")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    actions = [
        (c1, "Mark Seen", "Seen", "Seen", False, "Admin marked the request as seen."),
        (c2, "Check Receipt", "Receipt Checked", "Receipt Checked", False, "Admin checked the receipt/reference."),
        (c3, "Receive Payment", "Payment Received", "Payment Received", True, "Admin marked payment received and recorded funding if needed."),
        (c4, "Accept Investment", "Accepted", "Accepted", True, "Admin accepted the investment and recorded funding if needed."),
        (c5, "Need Info", "More Info Needed", "Need Member Reply", False, "Admin requested more information from the member."),
        (c6, "Reject", "Rejected", "Rejected", False, "Admin rejected the request."),
    ]
    for col, label, status, admin_label, record_funding, action in actions:
        if col.button(label, key=f"{label.lower().replace(' ', '_')}_{request_id}", use_container_width=True):
            update_investment_request(row, status, user, admin_label=admin_label, admin_note=note, record_funding=record_funding, action=action)
            st.toast(f"Request #{request_id} updated to {status}")
            st.rerun()


def render_investment_activity(request_id):
    activity = get_investment_activity(request_id)
    if activity.empty:
        st.caption("No activity log yet. The first admin action will appear here.")
        return
    st.markdown("**Activity / audit trail**")
    for _, a in activity.iterrows():
        render_html(f"""
<div class="notification-card">
  <div><b>{esc(a['action'])}</b> {status_badge(a['old_status'])} &rarr; {status_badge(a['new_status'])}</div>
  <div class="small-muted">By {esc(a['actor_name'] or 'System')} - {esc(a['created_at'])}</div>
  <div>{esc(a['note'] or '')}</div>
</div>
""")


def member_notifications_panel(user, compact=False):
    notes = get_member_notifications(int(user["id"]), unread_only=False, limit=6 if compact else 20)
    unread = get_member_notifications(int(user["id"]), unread_only=True, limit=50)
    if notes.empty:
        return
    st.markdown('<div class="section-title">Notifications</div>', unsafe_allow_html=True)
    if len(unread) > 0 and st.button("Mark notifications as read", key="mark_notifications_read"):
        mark_member_notifications_read(int(user["id"]))
        st.rerun()
    for _, n in notes.iterrows():
        badge = status_badge("New") if int(n.get("is_read") or 0) == 0 else status_badge("Seen")
        render_html(f"""
<div class="notification-card">
  <div>{badge} <b>{esc(n['title'])}</b></div>
  <div>{esc(n['body'] or '')}</div>
  <div class="small-muted">{esc(n['category'])} - {esc(n['created_at'])}</div>
</div>
""")


def member_investment_action(project_id: int, user):
    project = get_project(project_id)
    if not project or not user:
        return
    st.markdown('<div class="section-title">Accept / Invest in this project</div>', unsafe_allow_html=True)
    render_html(f'''
<div class="interaction-card">
  <div class="project-title">Submit your investment interest and payment details</div>
  <p style="color:#475569; line-height:1.65; margin:.45rem 0 0;">
    Use this form after reviewing the project. Your request goes to the admin side, where staff can mark it as
    Seen, Payment Received, Accepted, More Info Needed, or Rejected.
  </p>
</div>
''')
    render_html(f'''
<div class="ops-card">
  <div class="project-title">Official payment instructions</div>
  <p style="line-height:1.65; margin:.45rem 0;"><b>M-Pesa/Till/Paybill:</b> {esc(get_setting("mpesa_till_paybill", "Add official Till/Paybill here"))}<br>
  <b>Account name:</b> {esc(get_setting("mpesa_account_name", "Zenvest Investment Holdings"))}<br>
  <b>Account/reference:</b> {esc(get_setting("mpesa_account_number", "Use project code or member username as account reference"))}</p>
  <div class="small-muted">{esc(get_setting("payment_instructions", "Submit payment details for admin verification."))}</div>
</div>
''')
    with st.form(f"member_investment_form_{project_id}", clear_on_submit=True):
        accepted = st.checkbox("I have reviewed this project and I accept that I want to invest / participate.", value=False)
        c1, c2, c3 = st.columns(3)
        amount = c1.number_input("Investment amount (KES)", min_value=0.0, value=0.0, step=100.0)
        payment_method = c2.selectbox("Payment method", ["M-Pesa", "Bank Transfer", "Cash", "Cheque", "Other"])
        payment_date = c3.date_input("Payment / intended payment date", value=date.today())
        c4, c5, c6 = st.columns(3)
        mpesa_number = c4.text_input("M-Pesa number / sender number")
        payment_phone = c5.text_input("Payment phone or contact phone", value=user.get("phone") or "")
        account_name = c6.text_input("Account / sender name", value=user.get("full_name") or "")
        c7, c8 = st.columns([1, 1])
        mpesa_receipt = c7.text_input("M-Pesa receipt / transaction reference")
        receipt_file = c8.file_uploader("Upload receipt image/PDF (optional)", type=["png", "jpg", "jpeg", "pdf"])
        payment_details = st.text_area("Payment details", placeholder="Example: Paid via M-Pesa to company till/paybill, or will pay after admin confirmation.")
        member_note = st.text_area("Message to admin", placeholder="Any extra details you want the customer support to see.")
        submitted = st.form_submit_button("Accept project and send investment request", type="primary")
        if submitted:
            if not accepted:
                st.error("Please tick the acceptance box before submitting.")
            elif amount <= 0:
                st.error("Please enter an investment amount greater than zero.")
            elif payment_method == "M-Pesa" and not (mpesa_number.strip() and mpesa_receipt.strip()):
                st.error("For M-Pesa, please enter the sender number and receipt/reference code so admin can verify it accurately.")
            else:
                receipt_path = save_uploaded_receipt(receipt_file, int(user["id"]), project_id)
                request_id = execute(
                    """
                    INSERT INTO investment_requests(
                        project_id, member_id, amount, payment_method, mpesa_number, payment_phone,
                        account_name, mpesa_receipt, receipt_file, payment_date, payment_details,
                        member_note, status, admin_label
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        project_id, int(user["id"]), amount, payment_method, mpesa_number,
                        payment_phone, account_name, mpesa_receipt, receipt_path, str(payment_date),
                        payment_details, member_note, "Submitted", "New",
                    ),
                )
                log_investment_activity(request_id, "Member submitted investment request", "", "Submitted", member_note, user)
                create_notification(int(user["id"]), "Investment submitted", f"Your request #{request_id} for {project.get('code')} has been submitted and is waiting for admin review.", category="Investment", related_id=request_id)
                st.success("Investment request submitted instantly. Admin will review your payment details and update the status.")
                st.rerun()

    mine = get_investment_requests("ir.member_id=? AND ir.project_id=?", (int(user["id"]), project_id))
    if not mine.empty:
        st.markdown('<div class="section-title">My submissions for this project</div>', unsafe_allow_html=True)
        display_cols = [
            "created_at", "project_code", "amount", "payment_method", "mpesa_number",
            "mpesa_receipt", "status", "admin_label", "admin_note", "reviewed_by_name", "reviewed_at"
        ]
        st.dataframe(mine[display_cols], use_container_width=True, hide_index=True)


def investment_requests_page(user):
    hero("Investment Requests & Payments", "Review member project acceptances, payment details, M-Pesa numbers, receipts, and admin status labels.", ["Seen", "Payment received", "Accepted", "Admin notes"])
    df = get_investment_requests()
    open_count = len(df[df["status"].isin(["Submitted", "Seen", "More Info Needed"])]) if not df.empty else 0
    received_count = len(df[df["status"].isin(["Received", "Payment Received"])]) if not df.empty else 0
    accepted_count = len(df[df["status"] == "Accepted"]) if not df.empty else 0
    total_amount = float(df["amount"].sum()) if not df.empty else 0
    kpi_grid([
        ("🧾", "Total Requests", str(len(df)), "All submitted investments"),
        ("👀", "Needs Review", str(open_count), "Submitted / seen / info needed"),
        ("✅", "Received", str(received_count), "Payment marked received"),
        ("💰", "Requested Amount", money(total_amount), "All requests combined"),
    ])
    if df.empty:
        st.info("No member investment requests yet.")
        return

    status_filter = st.multiselect(
        "Filter by status",
        ["Submitted", "Seen", "Receipt Checked", "Payment Received", "Received", "Accepted", "More Info Needed", "Rejected"],
        default=["Submitted", "Seen", "Receipt Checked", "Payment Received", "Received", "Accepted", "More Info Needed"],
    )
    if status_filter:
        filtered = df[df["status"].isin(status_filter)]
    else:
        filtered = df

    table_cols = ["id", "created_at", "project_code", "project_title", "member_name", "amount", "payment_method", "mpesa_number", "mpesa_receipt", "status", "admin_label"]
    st.markdown('<div class="table-card">', unsafe_allow_html=True)
    st.dataframe(filtered[table_cols], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Admin payment interaction panel</div>', unsafe_allow_html=True)
    for _, r in filtered.iterrows():
        with st.expander(f"#{int(r['id'])} · {r['project_code']} · {r['member_name']} · {money(r['amount'])} · {r['status']}"):
            render_html(f'''
<div class="interaction-card">
  <div><b>Project:</b> {esc(r['project_code'])} — {esc(r['project_title'])}</div>
  <div><b>Member:</b> {esc(r['member_name'])} (@{esc(r['member_username'])}) · {esc(r['member_email'] or '')} · {esc(r['member_registered_phone'] or '')}</div>
  <div><b>Amount:</b> {esc(money(r['amount']))} · <b>Method:</b> {esc(r['payment_method'])}</div>
  <div><b>M-Pesa / Sender No:</b> {esc(r['mpesa_number'] or '')} · <b>Payment phone:</b> {esc(r['payment_phone'] or '')}</div>
  <div><b>Account / Sender name:</b> {esc(r['account_name'] or '')}</div>
  <div><b>Receipt / Reference:</b> {esc(r['mpesa_receipt'] or '')} · <b>Payment date:</b> {esc(r['payment_date'] or '')}</div>
  <div style="margin-top:.55rem;"><b>Payment details:</b><br>{esc(r['payment_details'] or '')}</div>
  <div style="margin-top:.55rem;"><b>Member note:</b><br>{esc(r['member_note'] or '')}</div>
  <div style="margin-top:.55rem;">{status_badge(r['status'])}{status_badge(r['admin_label'])}</div>
  <div class="small-muted">Reviewed by: {esc(r['reviewed_by_name'] or 'Not reviewed yet')} · Reviewed at: {esc(r['reviewed_at'] or '')}</div>
</div>
''')
            if r.get("receipt_file"):
                receipt_path = BASE_DIR / r["receipt_file"]
                st.caption(f"Receipt file: {r['receipt_file']}")
                if receipt_path.exists() and receipt_path.is_file():
                    st.download_button(
                        "Download uploaded receipt",
                        data=receipt_path.read_bytes(),
                        file_name=receipt_path.name,
                        key=f"receipt_download_{int(r['id'])}",
                    )
            render_html(investment_status_flow(r["status"]))
            quick_investment_operation_buttons(r, user)
            render_investment_activity(int(r["id"]))
            st.divider()
            with st.expander("Manual full edit / correction", expanded=False):
                with st.form(f"investment_admin_form_{int(r['id'])}"):
                    c1, c2 = st.columns(2)
                    status_options = ["Submitted", "Seen", "Receipt Checked", "Payment Received", "Received", "Accepted", "More Info Needed", "Rejected"]
                    label_options = ["New", "Seen", "Receipt Checked", "Payment Received", "Accepted", "Need Member Reply", "Rejected", "Record Only"]
                    new_status = c1.selectbox(
                        "Payment / investment status",
                        status_options,
                        index=status_options.index(r["status"] if r["status"] in status_options else "Submitted"),
                    )
                    admin_label = c2.selectbox(
                        "Admin label",
                        label_options,
                        index=label_options.index(r.get("admin_label")) if r.get("admin_label") in label_options else 0,
                    )
                    admin_note = st.text_area("Admin note / payment interaction comment", value=r.get("admin_note") or "")
                    already_recorded = not pd.isna(r.get("finance_tx_id")) and bool(r.get("finance_tx_id"))
                    record_funding = st.checkbox("Record this as project Funding transaction when saving", value=(new_status in ["Payment Received", "Received", "Accepted"] and not already_recorded))
                    submitted = st.form_submit_button("Save admin payment interaction", type="primary")
                    if submitted:
                        update_investment_request(
                            r,
                            new_status,
                            user,
                            admin_label=admin_label,
                            admin_note=admin_note,
                            record_funding=record_funding,
                            action="Manual admin correction / full edit",
                        )
                        st.success("Investment/payment interaction updated and logged.")
                        st.rerun()
            with st.expander("Edit amount/payment details or delete investment request", expanded=False):
                with st.form(f"investment_detail_edit_{int(r['id'])}"):
                    c1, c2, c3 = st.columns(3)
                    amount_edit = c1.number_input("Amount", min_value=0.0, value=float(r.get("amount") or 0), step=100.0, key=f"amount_edit_{int(r['id'])}")
                    method_edit = c2.selectbox("Payment method", ["M-Pesa", "Bank Transfer", "Cash", "Cheque", "Other"], index=["M-Pesa", "Bank Transfer", "Cash", "Cheque", "Other"].index(r.get("payment_method") if r.get("payment_method") in ["M-Pesa", "Bank Transfer", "Cash", "Cheque", "Other"] else "M-Pesa"), key=f"method_edit_{int(r['id'])}")
                    pay_date_edit = c3.text_input("Payment date", value=r.get("payment_date") or "", key=f"pay_date_edit_{int(r['id'])}")
                    c4, c5 = st.columns(2)
                    mpesa_edit = c4.text_input("M-Pesa / sender number", value=r.get("mpesa_number") or "", key=f"mpesa_edit_{int(r['id'])}")
                    receipt_edit = c5.text_input("Receipt / reference", value=r.get("mpesa_receipt") or "", key=f"receipt_edit_{int(r['id'])}")
                    details_edit = st.text_area("Payment details", value=r.get("payment_details") or "", key=f"details_edit_{int(r['id'])}")
                    member_note_edit = st.text_area("Member note", value=r.get("member_note") or "", key=f"membernote_edit_{int(r['id'])}")
                    save_edit = st.form_submit_button("Save investment detail changes", type="primary")
                    if save_edit:
                        execute(
                            """
                            UPDATE investment_requests
                            SET amount=?, payment_method=?, payment_date=?, mpesa_number=?, mpesa_receipt=?, payment_details=?, member_note=?
                            WHERE id=?
                            """,
                            (amount_edit, method_edit, pay_date_edit, mpesa_edit, receipt_edit, details_edit, member_note_edit, int(r["id"])),
                        )
                        log_investment_activity(int(r["id"]), "Admin edited investment/payment details", r.get("status"), r.get("status"), "Amount/details/payment reference edited", user)
                        st.success("Investment details updated.")
                        st.rerun()
                if st.button("Delete this investment request", key=f"delete_investment_{int(r['id'])}"):
                    log_investment_activity(int(r["id"]), "Admin deleted investment request", r.get("status"), "Deleted", "Deleted from investment request list", user)
                    execute("DELETE FROM investment_requests WHERE id=?", (int(r["id"]),))
                    st.warning("Investment request deleted.")
                    st.rerun()

def member_investments_page(user):
    hero("My Investments", "Track your submitted project acceptances, payment details, admin labels, admin decisions, and audit history.", ["Submitted", "Seen", "Received", "Accepted"])
    member_notifications_panel(user, compact=True)
    df = get_investment_requests("ir.member_id=?", (int(user["id"]),))
    if df.empty:
        st.info("You have not submitted an investment request yet. Open Investment Opportunities and accept a project to invest.")
        return
    kpi_grid([
        ("🧾", "My Requests", str(len(df)), "All submitted requests"),
        ("💰", "Total Amount", money(df["amount"].sum()), "Amount submitted"),
        ("✅", "Accepted", str(len(df[df["status"] == "Accepted"])), "Approved by admin"),
        ("👀", "Under Review", str(len(df[df["status"].isin(["Submitted", "Seen", "Receipt Checked", "More Info Needed"])])), "Waiting / needs action"),
    ])
    for _, r in df.iterrows():
        render_html(f'''
<div class="interaction-card">
  <div class="project-meta">{esc(r['created_at'])} · {esc(r['project_code'])}</div>
  <div class="project-title">{esc(r['project_title'])}</div>
  <div>{status_badge(r['status'])}{status_badge(r['admin_label'])}</div>
  <p style="color:#475569; line-height:1.6; margin:.6rem 0;">
    Amount: <b>{esc(money(r['amount']))}</b> · Method: <b>{esc(r['payment_method'])}</b> · M-Pesa/Sender: <b>{esc(r['mpesa_number'] or '')}</b> · Receipt/Ref: <b>{esc(r['mpesa_receipt'] or '')}</b>
  </p>
  <div class="small-muted"><b>Admin note:</b> {esc(r['admin_note'] or 'No admin note yet.')}</div>
  <div class="small-muted"><b>Reviewed:</b> {esc(r['reviewed_at'] or 'Not reviewed yet')}</div>
</div>
''')
        render_html(investment_status_flow(r["status"]))
        with st.expander(f"Activity history for request #{int(r['id'])}", expanded=False):
            render_investment_activity(int(r["id"]))


# =========================================================
# CHAT / SUPPORT INTERACTION HELPERS
# =========================================================
def live_fragment(run_every="2s"):
    """Native Streamlit partial rerun. It updates only this chat area, not the whole page."""
    fragment = getattr(st, "fragment", None)
    if fragment:
        return fragment(run_every=run_every)
    return lambda fn: fn


def faq_answer_for(question: str):
    faqs = query_df("SELECT question, answer FROM faqs WHERE active=1")
    q_low = (question or "").lower()
    for _, row in faqs.iterrows():
        words = [w for w in row["question"].lower().replace("?", "").split() if len(w) > 3]
        if words and any(word in q_low for word in words):
            return row["answer"]
    return None


def utc_now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_chat_message(sender_id, sender_role, sender_name, text, is_auto=0, admin_reply_to_id=None, status="Open", handled_by=None):
    return execute(
        """
        INSERT INTO chat_messages(sender_id,sender_role,sender_name,message_text,is_auto,admin_reply_to_id,status,handled_by)
        VALUES(?,?,?,?,?,?,?,?)
        """,
        (sender_id, sender_role, sender_name, text, int(is_auto), admin_reply_to_id, status, handled_by),
    )


def chat_member_thread_df(member_id: int):
    return query_df(
        """
        SELECT * FROM chat_messages
        WHERE sender_id=? OR admin_reply_to_id IN (SELECT id FROM chat_messages WHERE sender_id=? AND sender_role='Member')
        ORDER BY created_at ASC, id ASC
        """,
        (int(member_id), int(member_id)),
    )


def member_unread_chat_count(member_id: int) -> int:
    row = fetch_one(
        """
        SELECT COUNT(*) AS n
        FROM chat_messages
        WHERE is_auto=0
          AND sender_role IN ('Chairman','Manager','Secretary','Admin')
          AND member_read_at IS NULL
          AND admin_reply_to_id IN (SELECT id FROM chat_messages WHERE sender_id=? AND sender_role='Member')
        """,
        (int(member_id),),
    )
    return int(row["n"] if row else 0)


def staff_unread_chat_count() -> int:
    row = fetch_one(
        """
        SELECT COUNT(*) AS n
        FROM chat_messages
        WHERE sender_role IN ('Member','Public')
          AND is_auto=0
          AND staff_read_at IS NULL
          AND status NOT IN ('Closed')
        """
    )
    return int(row["n"] if row else 0)


def mark_member_chat_read(member_id: int):
    execute(
        """
        UPDATE chat_messages
        SET member_read_at=?
        WHERE member_read_at IS NULL
          AND is_auto=0
          AND sender_role IN ('Chairman','Manager','Secretary','Admin')
          AND admin_reply_to_id IN (SELECT id FROM chat_messages WHERE sender_id=? AND sender_role='Member')
        """,
        (utc_now_text(), int(member_id)),
    )


def mark_staff_chat_read(message_id: int, staff_id: int):
    execute(
        "UPDATE chat_messages SET staff_read_at=COALESCE(staff_read_at, ?), handled_by=COALESCE(handled_by, ?) WHERE id=?",
        (utc_now_text(), int(staff_id), int(message_id)),
    )


def browser_notification_widget(kind: str, unread_count: int, title: str, body: str):
    """Show visual badge and attempt browser notification/title badge when unread count increases."""
    unread_count = int(unread_count or 0)
    prev_key = f"_{kind}_last_unread_count"
    prev = int(st.session_state.get(prev_key, 0) or 0)
    if unread_count > prev:
        try:
            st.toast(f"🔔 {unread_count} new message(s)")
        except Exception:
            pass
    st.session_state[prev_key] = unread_count
    if unread_count <= 0:
        return
    safe_title = str(title).replace("\\", "\\\\").replace("'", "\\'")
    safe_body = str(body).replace("\\", "\\\\").replace("'", "\\'")
    components.html(
        f"""
<script>
(function() {{
  const key = 'zenvest_{kind}_unread_seen';
  const current = {unread_count};
  const title = '{safe_title}';
  const body = '{safe_body}';
  try {{ window.parent.document.title = '(' + current + ') ' + window.parent.document.title.replace(/^\\(\\d+\\) /, ''); }} catch(e) {{}}
  try {{
    const previous = parseInt(localStorage.getItem(key) || '0');
    if ('Notification' in window) {{
      if (Notification.permission === 'default') {{ Notification.requestPermission(); }}
      if (current > previous && Notification.permission === 'granted') {{ new Notification(title, {{ body: body }}); }}
    }}
    localStorage.setItem(key, String(current));
  }} catch(e) {{}}
}})();
</script>
""",
        height=0,
    )


def chat_badge_text(count: int) -> str:
    return f" 🔴 {int(count)}" if int(count or 0) > 0 else ""


def render_chat_bubble(row):
    role = row.get("sender_role") or "Bot"
    cls = "chat-bot" if row.get("is_auto") else "chat-admin" if role in ["Chairman", "Manager", "Secretary", "Admin"] else "chat-member"
    render_html(f"""
<div class="chat-bubble {cls}">
  <div style="font-weight:950;">{esc(row.get('sender_name') or role)} <span class="small-muted">· {esc(role)} · {esc(row.get('created_at') or '')}</span></div>
  <div>{esc(row.get('message_text') or '')}</div>
</div>
""")


def send_member_chat_message(user, clean_text: str):
    clean_text = (clean_text or "").strip()
    if not clean_text:
        return False
    message_id = add_chat_message(int(user["id"]), "Member", user.get("full_name") or user.get("username"), clean_text, is_auto=0, status="Open")
    answer = faq_answer_for(clean_text)
    if answer:
        bot_text = answer + "\n\nYour message has also been sent to the customer support panel for follow-up."
    else:
        bot_text = "Thank you. Your message has been sent to the customer support. Once the customer-support admin sees it, he/she will respond."
    add_chat_message(None, "Bot", "Zenvest Bot", bot_text, is_auto=1, admin_reply_to_id=message_id, status="Auto Reply")
    st.session_state["member_last_sent_at"] = utc_now_text()
    return True


def global_member_chat_widget(user):
    """Disabled in v22. Use the simple Support Chat page instead."""
    return


def render_member_chat_thread(member_id: int):
    thread = chat_member_thread_df(member_id)
    if thread.empty:
        st.info("No messages yet. Start by typing your first message below.")
    else:
        st.markdown('<div class="chat-thread">', unsafe_allow_html=True)
        for _, row in thread.iterrows():
            render_chat_bubble(dict(row))
        st.markdown('</div>', unsafe_allow_html=True)
        mark_member_chat_read(member_id)


@live_fragment(run_every="2s")
def live_member_chat_area(member_id: int):
    unread = member_unread_chat_count(member_id)
    if unread:
        st.success(f"🔔 {unread} new staff reply/message(s).")
    render_member_chat_thread(member_id)


def chatbot_widget(user=None, staff=False):
    """Simple live member chat page."""
    user = user or current_user()
    st.markdown('<div class="section-title">Support Chat</div>', unsafe_allow_html=True)

    if staff:
        st.info("Staff replies are handled in the Member Messages tab. This area only tests FAQ auto-answers.")
        user_q = st.text_input("Test FAQ question", placeholder="Example: How can I invest?", key="staff_chat_test_q")
        if st.button("Test chatbot answer", type="primary", key="staff_test_faq_answer"):
            answer = faq_answer_for(user_q)
            if answer:
                st.markdown(f'<div class="success-box"><b>Answer:</b><br>{esc(answer)}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-box">{esc(get_setting("support_message"))}</div>', unsafe_allow_html=True)
        return

    if not user:
        st.info("Please log in to send a message.")
        return

    member_id = int(user["id"])
    render_html(f"""
<div class="ops-card">
  <div class="project-title">💬 Message the Zenvest Customer Support</div>
  <p style="line-height:1.65;margin:.35rem 0;">Type your message below. Press <b>Enter</b> to send. The message saves instantly, and the chat thread updates in this chat area without full-page blinking.</p>
  <div class="small-muted">WhatsApp: {esc(get_setting("whatsapp", "+254790240112"))} · Email: {esc(get_setting("chairman_email", ""))} · Hours: {esc(get_setting("business_hours", ""))}</div>
</div>
""")

    live_member_chat_area(member_id)

    message = st.chat_input("Type your message and press Enter", key=f"member_live_chat_{member_id}")
    if message is not None:
        if send_member_chat_message(user, message):
            st.toast("Message sent to customer support.")
            st.rerun()
        else:
            st.warning("Please type a message before sending.")



@live_fragment(run_every="2s")
def live_admin_conversation_area(msg_id: int):
    thread = query_df(
        "SELECT * FROM chat_messages WHERE id=? OR admin_reply_to_id=? ORDER BY created_at ASC, id ASC",
        (int(msg_id), int(msg_id)),
    )
    st.markdown('<div class="chat-thread">', unsafe_allow_html=True)
    for _, msg in thread.iterrows():
        render_chat_bubble(dict(msg))
    st.markdown('</div>', unsafe_allow_html=True)


def admin_chat_center(user):
    """Simple staff inbox with live conversation panel. Only assigned customer support can reply."""
    st.markdown('<div class="section-title">Public & Member Messages Inbox</div>', unsafe_allow_html=True)
    assigned_label = support_staff_label()
    if can_reply_support(user):
        st.success(f"You are the assigned customer-support admin: {assigned_label}. You can reply to chats.")
    else:
        st.info(f"Assigned customer-support admin: {assigned_label}. You can view messages, but only the assigned support admin can reply or close conversations.")
    unread = staff_unread_chat_count()
    if unread:
        st.success(f"🔔 {unread} unread member message(s).")
    else:
        st.info("No unread member messages right now.")

    base = query_df(
        """
        SELECT cm.*, u.email AS member_email, u.phone AS member_phone, u.username AS member_username
        FROM chat_messages cm
        LEFT JOIN users u ON u.id = cm.sender_id
        WHERE cm.sender_role IN ('Member','Public') AND cm.is_auto=0
        ORDER BY CASE WHEN cm.staff_read_at IS NULL AND cm.status!='Closed' THEN 0 ELSE 1 END,
                 cm.created_at DESC, cm.id DESC
        """
    )
    if base.empty:
        st.info("No public or member messages yet.")
        return

    open_count = len(base[base["status"].isin(["Open", "Seen"])])
    replied_count = len(base[base["status"] == "Replied"])
    kpi_grid([
        ("🔴", "Unread", str(unread), "Need staff attention"),
        ("💬", "Total", str(len(base)), "Public/member conversations"),
        ("👀", "Open / Seen", str(open_count), "Not closed"),
        ("✅", "Replied", str(replied_count), "Staff responded"),
    ])

    def label_for(row):
        unread_mark = "🔴 " if pd.isna(row.get("staff_read_at")) and row.get("status") != "Closed" else ""
        snippet = (row.get("message_text") or "").replace("\n", " ")[:70]
        return f"{unread_mark}#{int(row['id'])} · {row.get('sender_name') or 'Member'} · {row.get('status') or 'Open'} · {snippet}"

    labels = [label_for(row) for _, row in base.iterrows()]
    selected_id_qp = qp_get("chat_id", "")
    default_index = 0
    if selected_id_qp:
        for i, (_, row) in enumerate(base.iterrows()):
            if str(int(row["id"])) == str(selected_id_qp):
                default_index = i
                break
    selected_label = st.selectbox("Select a public/member message", labels, index=default_index, key="admin_live_chat_select")
    selected_pos = labels.index(selected_label)
    r = dict(base.iloc[selected_pos])
    msg_id = int(r["id"])
    qp_set(chat_id=msg_id)

    render_html(f"""
<div class="conversation-row">
  <b>{esc(r.get('sender_name') or 'Member')}</b><br>
  Type: {esc(r.get('sender_role') or 'Message')} · Username: {esc(r.get('member_username') or 'Public visitor')} · Phone: {esc(r.get('member_phone') or 'See message/contact')} · Email: {esc(r.get('member_email') or 'See message/contact')}<br>
  <span class="small-muted">Conversation #{msg_id} · Status: {esc(r.get('status') or 'Open')} · Created: {esc(r.get('created_at') or '')}</span>
</div>
""")

    live_admin_conversation_area(msg_id)

    if can_reply_support(user):
        mark_staff_chat_read(msg_id, int(user["id"]))
        c1, c2, c3 = st.columns(3)
        if c1.button("Mark seen", key=f"simple_seen_{msg_id}"):
            execute("UPDATE chat_messages SET status=?, handled_by=?, staff_read_at=COALESCE(staff_read_at, ?) WHERE id=?", ("Seen", int(user["id"]), utc_now_text(), msg_id))
            st.success("Message marked seen.")
            st.rerun()
        if c2.button("Close", key=f"simple_close_{msg_id}"):
            execute("UPDATE chat_messages SET status=?, handled_by=?, staff_read_at=COALESCE(staff_read_at, ?) WHERE id=?", ("Closed", int(user["id"]), utc_now_text(), msg_id))
            st.success("Conversation closed.")
            st.rerun()
        if c3.button("Reopen", key=f"simple_reopen_{msg_id}"):
            execute("UPDATE chat_messages SET status=?, handled_by=? WHERE id=?", ("Open", int(user["id"]), msg_id))
            st.success("Conversation reopened.")
            st.rerun()

        reply_text = st.chat_input("Type reply and press Enter", key=f"admin_live_reply_{msg_id}")
        if reply_text is not None:
            reply_text = reply_text.strip()
            if reply_text:
                add_chat_message(int(user["id"]), user.get("role"), user.get("full_name"), reply_text, is_auto=0, admin_reply_to_id=msg_id, status="Replied", handled_by=int(user["id"]))
                execute("UPDATE chat_messages SET status=?, handled_by=?, staff_read_at=COALESCE(staff_read_at, ?) WHERE id=?", ("Replied", int(user["id"]), utc_now_text(), msg_id))
                st.toast("Reply sent.")
                st.rerun()

    else:
        st.warning("Reply controls are locked. Ask the Chairman to assign you as Customer Support if you need to respond to chats.")

    with st.expander("All member messages", expanded=False):
        st.dataframe(base[["id", "created_at", "sender_name", "member_username", "message_text", "status", "staff_read_at"]], use_container_width=True, hide_index=True)


# =========================================================
# NAMES / CONTACT DIRECTORY HELPERS
# =========================================================
def show_visible_directory(member_view=True):
    where = "WHERE visible_to_members=1" if member_view else ""
    df = query_df(f"SELECT full_name, role_title, phone, email, note, created_at FROM people_directory {where} ORDER BY role_title, full_name")
    if df.empty:
        st.info("No names or contacts have been added yet.")
        return
    for _, r in df.iterrows():
        render_html(f'''
<div class="interaction-card">
  <div class="project-title">{esc(r['full_name'])}</div>
  <div>{status_badge(r['role_title'])}</div>
  <p style="color:#475569; line-height:1.6; margin:.45rem 0;">{esc(r['note'] or '')}</p>
  <div class="small-muted">Phone: {esc(r['phone'] or '')} · Email: {esc(r['email'] or '')}</div>
</div>
''')


def names_directory_page(user):
    hero("Names & Contacts Directory", "Chairman, Manager, and Secretary can add important names, roles, payment contacts, and member-visible contact information.", ["Chairman adds names", "Staff can add too", "Visible to members"])
    with st.form("add_directory_name", clear_on_submit=True):
        c1, c2 = st.columns(2)
        full_name = c1.text_input("Full name")
        role_title = c2.text_input("Role / label", placeholder="Chairman, Manager, Payment Contact, Investor, Agent")
        c3, c4 = st.columns(2)
        phone = c3.text_input("Phone")
        email = c4.text_input("Email")
        note = st.text_area("Note / responsibility")
        visible = st.checkbox("Visible to members", value=True)
        submitted = st.form_submit_button("Add name/contact", type="primary")
        if submitted:
            if not full_name or not role_title:
                st.error("Full name and role/label are required.")
            else:
                execute(
                    "INSERT INTO people_directory(full_name,role_title,phone,email,note,visible_to_members,added_by) VALUES(?,?,?,?,?,?,?)",
                    (full_name, role_title, phone, email, note, 1 if visible else 0, int(user["id"])),
                )
                st.success("Name/contact added.")
                st.rerun()

    df = query_df(
        """
        SELECT pd.id, pd.full_name, pd.role_title, pd.phone, pd.email, pd.note, pd.visible_to_members, pd.created_at,
               u.full_name AS added_by_name
        FROM people_directory pd
        LEFT JOIN users u ON u.id = pd.added_by
        ORDER BY pd.created_at DESC
        """
    )
    if not df.empty:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if can_manage_staff(user):
            st.markdown('<div class="section-title">Chairman quick visibility control</div>', unsafe_allow_html=True)
            labels = [f"#{int(r['id'])} — {r['full_name']} ({r['role_title']})" for _, r in df.iterrows()]
            selected = st.selectbox("Select contact", labels)
            selected_id = int(df.iloc[labels.index(selected)]["id"])
            new_visibility = st.selectbox("Visibility", ["Visible to members", "Staff only"])
            c1, c2 = st.columns(2)
            if c1.button("Update visibility", type="primary"):
                execute("UPDATE people_directory SET visible_to_members=? WHERE id=?", (1 if new_visibility == "Visible to members" else 0, selected_id))
                st.success("Visibility updated.")
                st.rerun()
            if c2.button("Delete selected contact"):
                execute("DELETE FROM people_directory WHERE id=?", (selected_id,))
                st.warning("Contact removed.")
                st.rerun()

# =========================================================
# LOGIN SCREEN
# =========================================================


# =========================================================
# PUBLIC-FACING WEBSITE PAGES
# =========================================================
def public_set_page(page_key: str):
    qp_set(public=page_key, page=None, project_id=None, chat_id=None)


def public_nav_button(label: str, page_key: str, key: str, primary=False):
    if st.button(label, key=key, use_container_width=True, type="primary" if primary else "secondary"):
        public_set_page(page_key)
        st.rerun()


def public_header():
    render_html(f'''
<div class="public-topbar">
  <div class="public-brand">
    <div class="public-logo">Z</div>
    <div>
      <div class="public-brand-title">{esc(APP_NAME)}</div>
      <div class="public-brand-sub">Public website · Member portal · Staff operations</div>
    </div>
  </div>
  <div class="public-brand-sub">Public pages are open. Confidential records require login.</div>
</div>
''')
    nav_cols = st.columns([1,1,1,1,1,1,1,1])
    nav_items = [
        ("Home", "home"),
        ("Investments", "investments"),
        ("Products", "products"),
        ("Performance", "performance"),
        ("About", "about"),
        ("Support", "support"),
        ("Sign in", "login"),
        ("Register", "register"),
    ]
    for col, (label, key) in zip(nav_cols, nav_items):
        with col:
            public_nav_button(label, key, f"public_nav_{key}", primary=(key == "register"))


def public_footer():
    render_html(f'''
<div class="public-footer">
  <div style="font-size:1.15rem;font-weight:950;">{esc(APP_NAME)}</div>
  <div style="line-height:1.65;margin-top:.35rem;">Public services, project previews, products, performance information, and support contacts are visible here. Secure member and admin functions are protected behind login.</div>
  <div style="margin-top:.65rem;font-weight:850;">WhatsApp: {esc(get_setting('whatsapp', '+254790240112'))} · Email: {esc(get_setting('chairman_email', ''))} · Hours: {esc(get_setting('business_hours', ''))}</div>
</div>
''')


def public_hero():
    title = get_setting("public_hero_title", "Investment opportunities, products and performance in one secure portal")
    subtitle = get_setting("public_hero_subtitle", "Explore sample investment plans, public project previews, products, performance highlights, support contacts, and registration before entering the protected member portal.")
    render_html(f'''
<div class="public-hero">
  <div class="public-hero-inner">
    <h1>{esc(title)}</h1>
    <p>{esc(subtitle)}</p>
    <div class="public-search"><span>🔎</span><span>Search public services: investment opportunities, products, performance, support, registration...</span></div>
    <div class="public-service-grid">
      <div class="public-service-card"><div class="public-service-icon">📈</div><div class="public-service-title">View Investment Information</div></div>
      <div class="public-service-card"><div class="public-service-icon">📦</div><div class="public-service-title">Browse Products & Services</div></div>
      <div class="public-service-card"><div class="public-service-icon">🏁</div><div class="public-service-title">Check Performance Summary</div></div>
      <div class="public-service-card"><div class="public-service-icon">💬</div><div class="public-service-title">Ask Support Chatbot</div></div>
      <div class="public-service-card"><div class="public-service-icon">📝</div><div class="public-service-title">Register as Member</div></div>
      <div class="public-service-card"><div class="public-service-icon">🔐</div><div class="public-service-title">Secure Member Login</div></div>
    </div>
  </div>
</div>
''')


def public_quick_links():
    st.markdown('<div class="public-section"><div class="public-section-title">Open a public service</div><div class="public-section-subtitle">Each display acts like a link to its matching feature. Private actions such as accepting investments, uploading receipts, viewing member records, and admin controls require login.</div></div>', unsafe_allow_html=True)
    cols = st.columns(6)
    buttons = [
        ("📈 Investments", "investments"),
        ("📦 Products", "products"),
        ("🏁 Performance", "performance"),
        ("💬 Chatbot", "support"),
        ("ℹ️ About", "about"),
        ("🔐 Login", "login"),
    ]
    for col, (label, page) in zip(cols, buttons):
        with col:
            public_nav_button(label, page, f"public_quick_{page}")


def public_services_grid():
    render_html(f'''
<div class="public-section">
  <div class="public-section-title">Public services offered</div>
  <div class="public-section-subtitle">{esc(get_setting('public_services_intro', ''))}</div>
  <div class="public-feature-grid">
    <div class="public-feature-card"><div class="public-feature-icon">📈</div><div class="public-feature-title">Investment information</div><div class="public-feature-text">Public investment rate guidance, opportunity previews, and instructions. Members sign in to accept projects and submit payment details.</div></div>
    <div class="public-feature-card"><div class="public-feature-icon">📦</div><div class="public-feature-title">Products & services</div><div class="public-feature-text">Active product and service offers are visible to visitors, with full details and member actions available after secure login.</div></div>
    <div class="public-feature-card"><div class="public-feature-icon">🏁</div><div class="public-feature-title">Performance overview</div><div class="public-feature-text">Public performance summaries show project progress and general financial direction. Detailed records remain protected.</div></div>
    <div class="public-feature-card"><div class="public-feature-icon">💬</div><div class="public-feature-title">Chatbot & support</div><div class="public-feature-text">Visitors and approved members can ask support questions. Replies are handled by the Chairman-assigned customer-support admin.</div></div>
    <div class="public-feature-card"><div class="public-feature-icon">🔐</div><div class="public-feature-title">Member portal</div><div class="public-feature-text">Approved members can track investments, receipts, notifications, and support conversations.</div></div>
    <div class="public-feature-card"><div class="public-feature-icon">🧑‍💼</div><div class="public-feature-title">Staff operations</div><div class="public-feature-text">Chairman, Manager, and Secretary accounts manage members, projects, products, investments, chats, and reports.</div></div>
  </div>
</div>
''')


def public_rate_panel():
    render_html(f"""
<div class="public-rate-card">
  <div style="font-weight:950;font-size:1.15rem;">Sample investment profit display</div>
  <div class="public-rate-value">{esc(get_setting('public_investment_rate', '8%–25% sample projected profit ranges'))}</div>
  <div class="public-muted">{esc(get_setting('public_rate_note', 'Demo public examples only. Final project terms, timelines, risks, and accepted amounts are confirmed inside the secure member portal before payment submission.'))}</div>
  <div class="demo-rate-grid">
    <div class="demo-rate-box">
      <div class="demo-rate-name">Starter Growth</div>
      <div class="demo-rate-percent">8%–12%</div>
      <div class="demo-rate-small">Example: KES 10,000 may display a sample projected profit range of KES 800–1,200.</div>
    </div>
    <div class="demo-rate-box">
      <div class="demo-rate-name">Balanced Project</div>
      <div class="demo-rate-percent">13%–18%</div>
      <div class="demo-rate-small">Example: KES 25,000 may display a sample projected profit range of KES 3,250–4,500.</div>
    </div>
    <div class="demo-rate-box">
      <div class="demo-rate-name">Expansion Project</div>
      <div class="demo-rate-percent">19%–25%</div>
      <div class="demo-rate-small">Example: KES 50,000 may display a sample projected profit range of KES 9,500–12,500.</div>
    </div>
  </div>
</div>
""")


def public_demo_stats_strip():
    render_html("""
<div class="public-demo-strip">
  <div class="public-demo-stat"><div class="label">Sample member entry</div><div class="value">KES 10,000+</div><div class="note">Members choose a project and submit payment evidence after login.</div></div>
  <div class="public-demo-stat"><div class="label">Sample profit display</div><div class="value">8%–25%</div><div class="note">Projected examples are shown publicly; final terms appear per project.</div></div>
  <div class="public-demo-stat"><div class="label">Verification flow</div><div class="value">Seen → Accepted</div><div class="note">Admin checks receipt, confirms payment, then records funding.</div></div>
  <div class="public-demo-stat"><div class="label">Performance view</div><div class="value">Profit/Loss</div><div class="note">Completed projects show funding, revenue, expenses and result.</div></div>
</div>
""")


def public_investment_flow():
    render_html("""
<div class="public-section">
  <div class="public-section-title">How the investment process works</div>
  <div class="public-section-subtitle">This public flow explains the full user journey. Confidential amounts, receipts, private records, and admin decisions stay protected behind login.</div>
  <div class="public-flow-grid">
    <div class="public-flow-card"><div class="public-flow-number">1</div><div class="public-flow-title">View opportunity</div><div class="public-flow-text">Visitor opens public investment previews, rates, products, and performance summaries.</div></div>
    <div class="public-flow-card"><div class="public-flow-number">2</div><div class="public-flow-title">Register or login</div><div class="public-flow-text">A member signs in using username or email. New users submit registration for approval.</div></div>
    <div class="public-flow-card"><div class="public-flow-number">3</div><div class="public-flow-title">Accept project</div><div class="public-flow-text">Approved member selects a project, enters investment amount, and confirms interest.</div></div>
    <div class="public-flow-card"><div class="public-flow-number">4</div><div class="public-flow-title">Submit payment</div><div class="public-flow-text">Member enters M-Pesa number, sender name, receipt/reference, date, and upload notes.</div></div>
    <div class="public-flow-card"><div class="public-flow-number">5</div><div class="public-flow-title">Admin verifies</div><div class="public-flow-text">Staff marks Seen, Receipt Checked, Payment Received, Accepted, Need Info, or Rejected.</div></div>
    <div class="public-flow-card"><div class="public-flow-number">6</div><div class="public-flow-title">Track performance</div><div class="public-flow-text">Member follows status, notifications, project funding progress, and completed results.</div></div>
  </div>
</div>
""")


def public_home_page():
    public_hero()
    public_quick_links()
    public_demo_stats_strip()
    c1, c2 = st.columns([1.1, .9], gap="large")
    with c1:
        public_services_grid()
        public_investment_flow()
    with c2:
        public_rate_panel()
        st.markdown("### Public support")
        public_support_chatbot(compact=True)
    public_footer()


def public_investments_page():
    hero("Public Investment Information", "View sample profit ranges, project previews, investment flow, and payment guidance. Log in as a member to accept a project and submit payment details securely.", ["Sample rates", "Project previews", "Secure member actions"])
    public_rate_panel()
    public_investment_flow()
    df = query_df("SELECT * FROM projects WHERE status NOT IN ('Cancelled') ORDER BY created_at DESC")
    if df.empty:
        st.info("No public investment information is available yet.")
    else:
        st.markdown('<div class="section-title">Project previews</div>', unsafe_allow_html=True)
        for _, row in df.iterrows():
            r = dict(row)
            funding, revenue, expense, net = get_project_performance(int(r["id"]))
            progress = funding_progress(r, funding)
            render_html(f'''
<div class="project-card">
  <div class="project-meta">{esc(r.get('code'))} · {esc(r.get('location') or 'Nakuru')} · {esc(r.get('status'))}</div>
  <div class="project-title">{esc(r.get('title'))}</div>
  <p style="line-height:1.65;color:#475569;">{esc(r.get('executive_summary') or r.get('goal') or 'Public investment project preview.')}</p>
  <div style="height:10px;background:#E2E8F0;border-radius:999px;overflow:hidden;margin:.75rem 0;"><div style="height:10px;width:{progress*100:.1f}%;background:linear-gradient(90deg,#E4B834,#057A9C);"></div></div>
  <p style="font-weight:850;color:#0B3B75;">Demo return display: 13%–18% projected range · Funding progress: {progress*100:.1f}%</p>
  <div>{status_badge('Login required to invest')}{status_badge(r.get('visibility'))}</div>
</div>
''')
    c1, c2 = st.columns(2)
    with c1:
        public_nav_button("Sign in to accept investment", "login", "public_invest_login", primary=True)
    with c2:
        public_nav_button("Register as a member", "register", "public_invest_register")


def public_products_page():
    hero("Products & Services", "Browse the public product and service catalogue. Active offers are visible to visitors, while private purchase, member, and payment records remain protected.", ["Product catalogue", "Service details", "Member portal protected"])
    show_products(public_only=True)
    public_nav_button("Sign in for member-only product details", "login", "public_product_login", primary=True)


def public_performance_page():
    hero("Public Performance Overview", "See public funding progress, profit/loss examples, sample return ranges, and completed project outcomes. Full member receipts and admin records require login.", ["Performance", "Profit/Loss", "Completed results"])
    public_rate_panel()
    public_demo_stats_strip()
    public_investment_flow()
    df = query_df("SELECT * FROM projects WHERE status NOT IN ('Cancelled') ORDER BY created_at DESC")
    if df.empty:
        st.info("No project performance has been published yet.")
        return
    total_funding = total_revenue = total_expense = 0.0
    for _, row in df.iterrows():
        funding, revenue, expense, net = get_project_performance(int(row["id"]))
        total_funding += funding
        total_revenue += revenue
        total_expense += expense
    kpi_grid([
        ("💰", "Public Funding Summary", money(total_funding), "Recorded project funding"),
        ("📈", "Revenue Summary", money(total_revenue), "Public performance indicator"),
        ("📉", "Expense Summary", money(total_expense), "Public cost indicator"),
        ("🏁", "Net Summary", money(total_revenue-total_expense), "Revenue less expenses"),
    ])
    for _, row in df.iterrows():
        r = dict(row)
        funding, revenue, expense, net = get_project_performance(int(r["id"]))
        progress = funding_progress(r, funding)
        render_html(f'''
<div class="business-section">
  <h3>{esc(r.get('title'))}</h3>
  <div>{status_badge(r.get('status'))}{status_badge('Public summary')}</div>
  <p>Funding progress: {progress*100:.1f}% · Public net result: {esc(money(net))} · Expected end date: {esc(r.get('end_date') or 'Not set')}</p>
</div>
''')
    public_nav_button("Login to view detailed performance dashboard", "login", "public_perf_login", primary=True)


def public_about_page():
    hero("About Zenvest", "A public overview of Zenvest Investment Holdings. Secure member and staff areas remain protected behind login.", ["About", "Services", "Operations"])
    render_html(f'''
<div class="public-section">
  <div class="public-section-title">Who we are</div>
  <div class="public-section-subtitle">{esc(get_setting('public_about', ''))}</div>
</div>
''')
    public_services_grid()
    public_investment_flow()
    public_rate_panel()



def public_chat_thread_df(root_id: int):
    return query_df(
        "SELECT * FROM chat_messages WHERE id=? OR admin_reply_to_id=? ORDER BY created_at ASC, id ASC",
        (int(root_id), int(root_id)),
    )


def send_public_chat_message(visitor_name: str, visitor_contact: str, clean_text: str):
    clean_text = (clean_text or "").strip()
    if not clean_text:
        return None
    name = (visitor_name or "Public Visitor").strip() or "Public Visitor"
    contact = (visitor_contact or "").strip()
    message_body = clean_text
    if contact:
        message_body += f"\n\nVisitor contact: {contact}"
    message_id = add_chat_message(None, "Public", name, message_body, is_auto=0, status="Open")
    answer = faq_answer_for(clean_text)
    if answer:
        bot_text = answer + "\n\nYour enquiry has also been sent to customer support."
    else:
        bot_text = "Thank you. Your public enquiry has been sent to customer support. The assigned support admin will respond here as soon as possible."
    add_chat_message(None, "Bot", "Zenvest Bot", bot_text, is_auto=1, admin_reply_to_id=message_id, status="Auto Reply")
    st.session_state["public_chat_root_id"] = int(message_id)
    return int(message_id)


@live_fragment(run_every="2s")
def live_public_chat_area(root_id: int):
    thread = public_chat_thread_df(root_id)
    if thread.empty:
        st.info("No public chat messages yet.")
        return
    st.markdown('<div class="chat-thread">', unsafe_allow_html=True)
    for _, row in thread.iterrows():
        render_chat_bubble(dict(row))
    st.markdown('</div>', unsafe_allow_html=True)

def public_support_chatbot(compact=False):
    if not compact:
        hero("Public Chatbot & Support", "Visitors and members can send enquiries before login. Replies are handled only by the Chairman-assigned customer-support admin.", ["Public enquiries", "FAQ bot", "Customer support"])
    render_html(f'''
<div class="public-section">
  <div class="public-section-title">Ask Zenvest support</div>
  <div class="public-section-subtitle">This chat is open to the public before login. Type your enquiry and our chatbot will acknowledge it instantly. The selected customer-support admin can reply from the staff portal.</div>
</div>
''')
    root_id = st.session_state.get("public_chat_root_id")
    if root_id:
        live_public_chat_area(int(root_id))
    else:
        st.info("Start a public enquiry by entering your name/contact and typing your first message.")

    c1, c2 = st.columns(2)
    with c1:
        visitor_name = st.text_input("Your name", value=st.session_state.get("public_visitor_name", ""), key="public_visitor_name_input")
    with c2:
        visitor_contact = st.text_input("Email or phone / WhatsApp", value=st.session_state.get("public_visitor_contact", ""), key="public_visitor_contact_input")
    st.session_state["public_visitor_name"] = visitor_name
    st.session_state["public_visitor_contact"] = visitor_contact

    prompt = "Type your public enquiry and press Enter" if not compact else "Ask support and press Enter"
    msg = st.chat_input(prompt, key="public_live_chat_compact" if compact else "public_live_chat_full")
    if msg is not None:
        sent_id = send_public_chat_message(visitor_name, visitor_contact, msg)
        if sent_id:
            st.toast("Enquiry sent to customer support.")
            st.rerun()
        else:
            st.warning("Please type a message before sending.")


    render_html(f'''
<div class="card">
  <b>Contact support</b><br>
  Assigned support admin: {esc(support_staff_label())}<br>
  WhatsApp: {esc(get_setting('whatsapp', '+254790240112'))}<br>
  Email: {esc(get_setting('chairman_email', ''))}<br>
  Hours: {esc(get_setting('business_hours', ''))}
</div>
''')
    if not compact:
        c1, c2 = st.columns(2)
        with c1:
            public_nav_button("Sign in for member records", "login", "public_support_login", primary=True)
        with c2:
            public_nav_button("Register for member access", "register", "public_support_register")


def public_auth_page(register_hint=False):
    if register_hint:
        st.info("Open the Register tab below to submit a member access request. Staff must approve it before you can access confidential member features.")
    else:
        st.info("Sign in is required for confidential member records, investment acceptance, payment receipts, and admin operations. Public enquiries can be sent from Support before login.")
    login_screen()


def public_site_router():
    public_header()
    page = qp_get("public", "home") or "home"
    if page == "home":
        public_home_page()
    elif page == "investments":
        public_investments_page()
    elif page == "products":
        public_products_page()
    elif page == "performance":
        public_performance_page()
    elif page == "about":
        public_about_page()
    elif page == "support":
        public_support_chatbot(compact=False)
    elif page == "register":
        public_auth_page(register_hint=True)
    elif page == "login":
        public_auth_page(register_hint=False)
    else:
        public_home_page()


def login_screen():
    col1, col2 = st.columns([1.18, .82], gap="large")
    slogan = get_setting('portal_slogan', 'Structured projects, transparent performance, and shareholder growth.')

    with col1:
        render_html(f'''
<div class="login-hero-final">
  <div class="gold-line"></div>
  <div class="login-hero-title-final">{esc(APP_NAME)}</div>
  <div class="login-hero-subtitle-final">
    {esc(slogan)} This portal brings together investment opportunities, upcoming projects, products,
    member records, financial performance, and customer support in one secure system.
  </div>
  <div>
    <span class="chip-final">📍 Nakuru</span>
    <span class="chip-final">📈 Investment Performance</span>
    <span class="chip-final">💼 Business Projects</span>
    <span class="chip-final">🤝 Member Portal</span>
  </div>
</div>
''')
        if (ASSET_DIR / "nakuru_location.jpg").exists():
            st.image(str(ASSET_DIR / "nakuru_location.jpg"), use_container_width=True, caption="Nakuru business location")

    with col2:
        render_html('''
<div class="access-header-final">
  <div class="access-brand-final">
    <div class="access-logo-final">Z</div>
    <div>
      <div class="access-title-final">Access portal</div>
      <div class="access-subtitle-final">Chairman · Manager · Secretary · Member</div>
    </div>
  </div>
</div>
''')
        tab1, tab2, tab3 = st.tabs(["Staff Login", "Member Login", "Register"])
        with tab1:
            username = st.text_input("Staff username or email", placeholder="chairman, manager, secretary, or email", key="staff_username")
            password = st.text_input("Staff password", type="password", key="staff_password")
            if st.button("Login as Staff", type="primary", use_container_width=True):
                user = authenticate(username, password, ["Chairman", "Manager", "Secretary"])
                if user:
                    remember_login(user)
                    set_page("dashboard")
                    st.rerun()
                st.error("Invalid staff username/email or inactive staff account.")
        with tab2:
            username = st.text_input("Member username or email", key="member_username")
            password = st.text_input("Member password", type="password", key="member_password")
            if st.button("Login as Member", type="primary", use_container_width=True):
                user = authenticate(username, password, ["Member"])
                if user:
                    remember_login(user)
                    set_page("dashboard")
                    st.rerun()
                st.error("Invalid member username/email, inactive account, or account still pending approval.")
        with tab3:
            with st.form("registration_form", clear_on_submit=True):
                full_name = st.text_input("Full name")
                username = st.text_input("Preferred username")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                password = st.text_input("Create password", type="password")
                submitted = st.form_submit_button("Submit registration request")
                if submitted:
                    if not full_name or not username or not password:
                        st.error("Full name, username, and password are required.")
                    else:
                        try:
                            execute("INSERT INTO users(username,password_hash,role,full_name,email,phone,status) VALUES(?,?,?,?,?,?,?)", (username, hash_password(password), "Member", full_name, email, phone, "pending"))
                            st.success("Registration submitted. Staff will approve your account.")
                        except sqlite3.IntegrityError:
                            st.error("That username already exists. Choose another username.")


# =========================================================
# BUSINESS PLAN / PROJECT DISPLAY
# =========================================================
def show_products(project_id=None, public_only=True):
    if project_id:
        sql = "SELECT * FROM products WHERE project_id=?"
        params = [project_id]
        if public_only:
            sql += " AND status='Active'"
        sql += " ORDER BY created_at DESC"
        df = query_df(sql, tuple(params))
    else:
        sql = "SELECT p.*, pr.code AS project_code, pr.title AS project_title FROM products p LEFT JOIN projects pr ON p.project_id=pr.id"
        if public_only:
            sql += " WHERE p.status='Active'"
        sql += " ORDER BY p.created_at DESC"
        df = query_df(sql)
    if df.empty:
        st.info("No products/services available yet.")
        return
    cols = st.columns(3)
    for idx, row in df.iterrows():
        with cols[idx % 3]:
            render_html(f"""
<div class="product-card">
  <div class="product-placeholder">📦</div>
  <div class="project-meta">{esc(row['code'])} · {esc(row['status'])}</div>
  <div class="project-title">{esc(row['name'])}</div>
  <p style="color:#475569; line-height:1.55; min-height:58px;">{esc(row.get('description') or '')}</p>
  <div style="font-size:1.18rem; font-weight:900; color:#0F172A;">{esc(money(row.get('price') or 0))}</div>
  <div style="color:#64748B; font-size:.82rem; margin-top:.4rem;">Visual idea: {esc(row.get('image_hint') or 'product/service image')}</div>
</div>
""")


def show_financial_dashboard(project_id: int):
    project = get_project(project_id)
    if not project:
        st.info("Select a project first.")
        return
    funding, revenue, expense, net = get_project_performance(project_id)
    progress = funding_progress(project, funding)
    days = days_remaining(project.get("end_date"))
    kpi_grid([
        ("💰", "Funding Raised", money(funding), "Contributions recorded"),
        ("📈", "Revenue", money(revenue), "Income generated"),
        ("📉", "Expenses", money(expense), "Costs recorded"),
        ("🏁", "Profit / Loss", money(net), "Revenue less expenses"),
    ])
    st.progress(progress, text=f"Funding progress: {progress*100:.1f}%")
    if days is not None:
        if days >= 0:
            st.info(f"Expected end date: {project.get('end_date')} · {days} day(s) remaining.")
        else:
            st.warning(f"Expected end date passed on {project.get('end_date')}. The project is ready for completed-project review.")
    tx = query_df("SELECT tx_date, tx_type, amount, note FROM transactions WHERE project_id=? ORDER BY tx_date", (project_id,))
    if tx.empty:
        st.info("No financial records have been added yet.")
        return
    grouped = tx.groupby("tx_type", as_index=False)["amount"].sum()
    fig = px.bar(grouped, x="tx_type", y="amount", text_auto=True, title="Financial performance by category")
    fig.update_layout(template="plotly_white", height=360, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="table-card">', unsafe_allow_html=True)
    st.dataframe(tx, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


def show_milestones(project_id: int):
    df = query_df("SELECT * FROM milestones WHERE project_id=? ORDER BY due_date", (project_id,))
    if df.empty:
        st.info("No milestones have been added yet.")
        return
    for _, r in df.iterrows():
        render_html(f"""
<div class="business-section">
  <h3>{esc(r['title'])}</h3>
  <div>{status_badge(r['status'])}<span class="badge badge-gray">Due: {esc(r['due_date'] or 'Not set')}</span></div>
  <p>{esc(r['description'] or '')}</p>
</div>
""")


def show_project_full(project_id: int, staff_view=False):
    project = get_project(project_id)
    if not project:
        st.warning("Project not found.")
        return
    project_card(project)
    tabs = st.tabs(["Summary", "Idea", "Market", "Management", "Products", "Marketing", "Financial", "Operations", "Milestones"])
    with tabs[0]:
        business_section("Executive Summary", project.get("executive_summary"))
        c1, c2 = st.columns(2)
        with c1:
            business_section("Vision", project.get("vision"))
        with c2:
            business_section("Goal", project.get("goal"))
        business_section("Team Behind the Project", project.get("team_summary"))
    with tabs[1]:
        c1, c2 = st.columns([1, 1])
        with c1:
            business_section("Description of the Idea", project.get("idea_description"))
            business_section("Location", f"The business/project location is {project.get('location') or 'Nakuru'}.")
            business_section("Long-Term Vision", project.get("vision"))
        with c2:
            if (ASSET_DIR / "nakuru_location.jpg").exists():
                st.image(str(ASSET_DIR / "nakuru_location.jpg"), caption="Business location: Nakuru", use_container_width=True)
    with tabs[2]:
        c1, c2 = st.columns([1, 1])
        with c1:
            business_section("Market Analysis", project.get("market_analysis"))
            business_section("Competitive Advantage", "The idea is evaluated through company capability, customer value, competitor gaps, opportunities, target customers, pricing, and differentiation.")
        with c2:
            if (ASSET_DIR / "market_analysis_growth.png").exists():
                st.image(str(ASSET_DIR / "market_analysis_growth.png"), caption="Market positioning and competitive advantage", use_container_width=True)
    with tabs[3]:
        c1, c2 = st.columns([1, 1])
        with c1:
            business_section("Organization and Management", project.get("organization_management"))
            business_section("Roles", "Chairman controls strategic direction and staff accounts. Manager supports project operations and performance. Secretary supports records, members, documents, and communication.")
        with c2:
            if (ASSET_DIR / "management_team_structure.jpg").exists():
                st.image(str(ASSET_DIR / "management_team_structure.jpg"), caption="Management team / organization structure", use_container_width=True)
    with tabs[4]:
        business_section("Product or Service Behind the Idea", project.get("products_summary"))
        show_products(project_id=project_id, public_only=not staff_view)
    with tabs[5]:
        business_section("Marketing Strategy", project.get("marketing_strategy"))
    with tabs[6]:
        business_section("Financial Plan", project.get("financial_plan"))
        show_financial_dashboard(project_id)
    with tabs[7]:
        business_section("Operational Plan", project.get("operational_plan"))
    with tabs[8]:
        show_milestones(project_id)


# =========================================================
# STAFF PAGES
# =========================================================
def sidebar(user):
    st.sidebar.markdown("# 💼 Zenvest")
    st.sidebar.markdown(f"**{esc(user['full_name'])}**  ")
    st.sidebar.markdown(role_badge(user["role"]), unsafe_allow_html=True)
    st.sidebar.divider()
    if st.sidebar.button("Logout", use_container_width=True):
        logout()


def staff_dashboard(user):
    hero(f"{user['role']} Dashboard", "Control business projects, product visibility, member records, investment performance, milestones, reports, and support.", ["Nakuru", "Business Plan Hub", "Investment Performance"])
    projects = query_df("SELECT * FROM projects")
    users = query_df("SELECT * FROM users")
    products = query_df("SELECT * FROM products")
    tx = query_df("SELECT * FROM transactions")
    active_projects = len(projects[projects["status"].isin(["Upcoming", "Active", "In Progress"])]) if not projects.empty else 0
    members = len(users[users["role"] == "Member"]) if not users.empty else 0
    active_products = len(products[products["status"] == "Active"]) if not products.empty else 0
    revenue = tx[tx["tx_type"] == "Revenue"]["amount"].sum() if not tx.empty else 0
    expense = tx[tx["tx_type"] == "Expense"]["amount"].sum() if not tx.empty else 0
    kpi_grid([
        ("📌", "Active Projects", str(active_projects), "Upcoming and active plans"),
        ("👥", "Members", str(members), "Active and pending accounts"),
        ("📦", "Active Products", str(active_products), "Visible to members/customers"),
        ("🏁", "Net Result", money(revenue - expense), "Revenue less expenses"),
    ])
    inv = query_df("SELECT * FROM investment_requests")
    msgs = query_df("SELECT * FROM chat_messages WHERE sender_role='Member' AND is_auto=0")
    pending_inv = len(inv[inv["status"].isin(["Submitted", "Seen", "Receipt Checked", "More Info Needed"])]) if not inv.empty else 0
    open_msgs = len(msgs[msgs["status"].isin(["Open", "Seen"])]) if not msgs.empty else 0
    kpi_grid([
        ("💳", "Investment Requests", str(len(inv)), "Member payment submissions"),
        ("👀", "Pending Payments", str(pending_inv), "Need admin action"),
        ("💬", "Unread Chat", str(staff_unread_chat_count()), "Support inbox"),
        ("📨", "Open Messages", str(open_msgs), "Need reply / close"),
    ])
    st.markdown('<div class="section-title">Featured active project</div>', unsafe_allow_html=True)
    active = query_df("SELECT * FROM projects WHERE status IN ('Upcoming','Active','In Progress') ORDER BY created_at DESC LIMIT 1")
    if not active.empty:
        show_project_full(int(active.iloc[0]["id"]), staff_view=True)
    else:
        st.info("No active project yet. Add one from Upcoming Events / Projects.")


def manage_projects():
    hero("Upcoming Events / Projects", "Add, edit, and monitor full business-plan projects with executive summary, idea description, market analysis, management, products, finance, operations, and milestones.", ["Project codes", "Expected end date", "Profit/Loss archive"])
    tab_add, tab_view, tab_update, tab_milestones = st.tabs(["Add Project", "View Projects", "Edit Project", "Milestones"])
    with tab_add:
        with st.form("add_project_form"):
            c1, c2, c3 = st.columns(3)
            code = c1.text_input("Project code", value=f"PRJ-{table_count('projects')+1:03d}")
            title = c2.text_input("Project title")
            location = c3.text_input("Location", value="Nakuru")
            c4, c5, c6 = st.columns(3)
            status = c4.selectbox("Status", ["Upcoming", "Active", "In Progress", "Completed", "Passed", "Cancelled"])
            visibility = c5.selectbox("Visibility", ["Members Only", "Public", "Staff Only"])
            start_date = c6.date_input("Start date", value=date.today())
            end_date = st.date_input("Expected end date", value=date(date.today().year, 12, 31))
            vision = st.text_area("Vision")
            goal = st.text_area("Goal")
            team_summary = st.text_area("Team behind it")
            executive_summary = st.text_area("1. Executive Summary")
            idea_description = st.text_area("2. Description of the Idea")
            market_analysis = st.text_area("3. Market Analysis")
            organization_management = st.text_area("4. Organization and Management")
            products_summary = st.text_area("5. Product / Service Behind the Idea")
            marketing_strategy = st.text_area("6. Marketing Strategy")
            financial_plan = st.text_area("7. Financial Plan")
            operational_plan = st.text_area("8. Operational Plan")
            c7, c8, c9 = st.columns(3)
            budget_target = c7.number_input("Budget target", min_value=0.0, value=0.0)
            funding_required = c8.number_input("Funding required", min_value=0.0, value=0.0)
            expected_revenue = c9.number_input("Expected revenue", min_value=0.0, value=0.0)
            submitted = st.form_submit_button("Create project", type="primary")
            if submitted:
                if not code or not title:
                    st.error("Project code and title are required.")
                else:
                    try:
                        execute(
                            """
                            INSERT INTO projects(code,title,location,status,visibility,start_date,end_date,vision,goal,team_summary,executive_summary,idea_description,market_analysis,organization_management,products_summary,marketing_strategy,financial_plan,operational_plan,budget_target,funding_required,expected_revenue)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                            """,
                            (code, title, location, status, visibility, str(start_date), str(end_date), vision, goal, team_summary, executive_summary, idea_description, market_analysis, organization_management, products_summary, marketing_strategy, financial_plan, operational_plan, budget_target, funding_required, expected_revenue),
                        )
                        st.success("Project created successfully.")
                    except sqlite3.IntegrityError:
                        st.error("That project code already exists.")
    with tab_view:
        df = query_df("SELECT * FROM projects ORDER BY created_at DESC")
        if df.empty:
            st.info("No projects yet.")
        else:
            for _, p in df.iterrows():
                project_card(dict(p))
                with st.expander(f"Open full plan: {p['code']} — {p['title']}"):
                    show_project_full(int(p["id"]), staff_view=True)
    with tab_update:
        project_id = project_selectbox("Select project to update", key="edit_project")
        if project_id:
            p = get_project(project_id)
            with st.form("edit_project_form"):
                c1, c2, c3 = st.columns(3)
                title = c1.text_input("Title", value=p.get("title") or "")
                location = c2.text_input("Location", value=p.get("location") or "Nakuru")
                status = c3.selectbox("Status", ["Upcoming", "Active", "In Progress", "Completed", "Passed", "Cancelled"], index=["Upcoming", "Active", "In Progress", "Completed", "Passed", "Cancelled"].index(p.get("status") if p.get("status") in ["Upcoming", "Active", "In Progress", "Completed", "Passed", "Cancelled"] else "Upcoming"))
                visibility = st.selectbox("Visibility", ["Members Only", "Public", "Staff Only"], index=["Members Only", "Public", "Staff Only"].index(p.get("visibility") if p.get("visibility") in ["Members Only", "Public", "Staff Only"] else "Members Only"))
                end_value = datetime.strptime(p["end_date"], "%Y-%m-%d").date() if p.get("end_date") else date.today()
                end_date = st.date_input("Expected end date", value=end_value)
                fields = {}
                for key, label in [
                    ("vision", "Vision"), ("goal", "Goal"), ("team_summary", "Team Summary"),
                    ("executive_summary", "Executive Summary"), ("idea_description", "Idea Description"),
                    ("market_analysis", "Market Analysis"), ("organization_management", "Organization and Management"),
                    ("products_summary", "Product / Service"), ("marketing_strategy", "Marketing Strategy"),
                    ("financial_plan", "Financial Plan"), ("operational_plan", "Operational Plan"),
                ]:
                    fields[key] = st.text_area(label, value=p.get(key) or "")
                c4, c5, c6 = st.columns(3)
                budget_target = c4.number_input("Budget target", min_value=0.0, value=float(p.get("budget_target") or 0))
                funding_required = c5.number_input("Funding required", min_value=0.0, value=float(p.get("funding_required") or 0))
                expected_revenue = c6.number_input("Expected revenue", min_value=0.0, value=float(p.get("expected_revenue") or 0))
                if st.form_submit_button("Save changes", type="primary"):
                    execute(
                        """
                        UPDATE projects SET title=?, location=?, status=?, visibility=?, end_date=?, vision=?, goal=?, team_summary=?, executive_summary=?, idea_description=?, market_analysis=?, organization_management=?, products_summary=?, marketing_strategy=?, financial_plan=?, operational_plan=?, budget_target=?, funding_required=?, expected_revenue=? WHERE id=?
                        """,
                        (title, location, status, visibility, str(end_date), fields["vision"], fields["goal"], fields["team_summary"], fields["executive_summary"], fields["idea_description"], fields["market_analysis"], fields["organization_management"], fields["products_summary"], fields["marketing_strategy"], fields["financial_plan"], fields["operational_plan"], budget_target, funding_required, expected_revenue, project_id),
                    )
                    st.success("Project updated.")
                    st.rerun()
            with st.expander("Archive / delete project", expanded=False):
                st.warning("Use Passed when the project time ended. Delete only if this project was created by mistake.")
                cdel1, cdel2 = st.columns(2)
                if cdel1.button("Mark as Passed / time ended", key=f"project_passed_{project_id}"):
                    execute("UPDATE projects SET status='Passed' WHERE id=?", (project_id,))
                    st.success("Project marked as Passed and will appear in the completed/performance archive.")
                    st.rerun()
                if cdel2.button("Delete project", key=f"project_delete_{project_id}"):
                    execute("DELETE FROM projects WHERE id=?", (project_id,))
                    st.warning("Project deleted. Related records may remain for reporting depending on database references.")
                    st.rerun()
    with tab_milestones:
        project_id = project_selectbox("Project for milestone", key="milestone_project")
        if project_id:
            with st.form("milestone_form", clear_on_submit=True):
                title = st.text_input("Milestone title")
                description = st.text_area("Description")
                due_date = st.date_input("Due date")
                status = st.selectbox("Status", ["Pending", "In Progress", "Completed", "Delayed"])
                if st.form_submit_button("Add milestone", type="primary"):
                    execute("INSERT INTO milestones(project_id,title,description,due_date,status) VALUES(?,?,?,?,?)", (project_id, title, description, str(due_date), status))
                    st.success("Milestone added.")
            show_milestones(project_id)


def manage_products():
    hero("Products & Services", "Add products, services, or investment offers. Active products automatically appear to members/customers; paused, expired, or removed items stay hidden from public view.", ["Dynamic products", "Admin controlled", "Customer view"])
    tab_add, tab_view = st.tabs(["Add / Update Product", "Product Gallery"])
    with tab_add:
        project_id = project_selectbox("Link product to project", key="product_project")
        with st.form("product_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            code = c1.text_input("Product code", value=f"PRD-{table_count('products')+1:03d}")
            name = c2.text_input("Product/service name")
            status = c3.selectbox("Status", ["Active", "Paused", "Expired", "Removed"])
            description = st.text_area("Description")
            c4, c5 = st.columns(2)
            price = c4.number_input("Price / value", min_value=0.0, value=0.0)
            image_hint = c5.text_input("Image idea / hint")
            if st.form_submit_button("Save product", type="primary"):
                if not code or not name:
                    st.error("Product code and name are required.")
                else:
                    try:
                        execute("INSERT INTO products(code,project_id,name,description,price,status,image_hint) VALUES(?,?,?,?,?,?,?)", (code, project_id, name, description, price, status, image_hint))
                        st.success("Product saved.")
                    except sqlite3.IntegrityError:
                        st.error("That product code already exists.")
        st.markdown('<div class="section-title">Quick status update</div>', unsafe_allow_html=True)
        df = query_df("SELECT id, code, name, status FROM products ORDER BY created_at DESC")
        if not df.empty:
            product_labels = [f"{r['code']} — {r['name']} ({r['status']})" for _, r in df.iterrows()]
            selected = st.selectbox("Select product", product_labels)
            prod_id = int(df.iloc[product_labels.index(selected)]["id"])
            new_status = st.selectbox("New status", ["Active", "Paused", "Expired", "Removed"], key="product_status")
            if st.button("Update product status", type="primary"):
                execute("UPDATE products SET status=? WHERE id=?", (new_status, prod_id))
                st.success("Product status updated.")
                st.rerun()
    with tab_view:
        show_products(public_only=False)
        df = query_df("SELECT code, name, status, price, created_at FROM products ORDER BY created_at DESC")
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)


def performance_page():
    hero("Investment Performance", "Real-time project infographics for funding, revenue, expenses, profit/loss, expected end date, and financial progress.", ["Live dashboard", "Cash flow", "ROI view"])
    project_id = project_selectbox("Select project", key="performance_project")
    if project_id:
        show_financial_dashboard(project_id)
        st.markdown('<div class="section-title">Add financial record</div>', unsafe_allow_html=True)
        with st.form("transaction_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            tx_type = c1.selectbox("Type", ["Funding", "Revenue", "Expense"])
            amount = c2.number_input("Amount", min_value=0.0, value=0.0)
            tx_date = c3.date_input("Date", value=date.today())
            note = st.text_input("Note")
            if st.form_submit_button("Add record", type="primary"):
                execute("INSERT INTO transactions(project_id, tx_type, amount, note, tx_date) VALUES(?,?,?,?,?)", (project_id, tx_type, amount, note, str(tx_date)))
                st.success("Financial record added.")
                st.rerun()


def completed_projects_page():
    hero("Completed / Success & Loss Archive", "After expected end date or staff completion, projects move here and show their final profit, loss, or break-even result.", ["Success archive", "Profit/Loss", "Closed plans"])
    df = query_df("SELECT * FROM projects WHERE status IN ('Completed','Passed') ORDER BY end_date DESC")
    if df.empty:
        st.info("No completed projects yet.")
        return
    for _, row in df.iterrows():
        project_card(dict(row))


def create_member_account(username, password, full_name, email="", phone="", status="active", member_role="Standard Member"):
    return execute(
        "INSERT INTO users(username,password_hash,role,member_role,full_name,email,phone,status) VALUES(?,?,?,?,?,?,?,?)",
        (username.strip(), hash_password(password), "Member", member_role, full_name.strip(), email.strip(), phone.strip(), status),
    )


def members_page(user):
    hero("Members", "Approve, add, edit, remove, restore, and assign simple member roles/categories from one control area.", ["Approvals", "Assign roles", "Manual add", "Email login"])
    df = query_df("SELECT id, username, role, member_role, full_name, email, phone, status, created_at FROM users WHERE role='Member' ORDER BY created_at DESC")
    role_opts = member_role_options()
    status_opts = ["active", "pending", "paused", "suspended", "abandoned", "failed/abandoned", "removed", "rejected"]
    tab_pending, tab_add, tab_assign, tab_control, tab_table = st.tabs(["Pending requests", "Add member", "Assign member role", "Member control", "All members"])

    with tab_pending:
        pending = df[df["status"] == "pending"] if not df.empty else pd.DataFrame()
        if pending.empty:
            st.info("No pending registration requests.")
        else:
            st.markdown("Choose a member category before approving. This does not change system access; it only classifies the member for business operations.")
            for _, r in pending.iterrows():
                render_html(f'''
<div class="interaction-card">
  <div class="project-title">{esc(r['full_name'])}</div>
  <div>Username: <b>{esc(r['username'])}</b> · Email: <b>{esc(r['email'] or '')}</b> · Phone: <b>{esc(r['phone'] or '')}</b></div>
  <div style="margin-top:.45rem;">{status_badge(r['status'])} {member_role_badge(r.get('member_role'))}</div>
</div>
''')
                role_choice = st.selectbox("Assign member role/category", role_opts, index=role_opts.index(r.get("member_role")) if r.get("member_role") in role_opts else 0, key=f"pending_role_{int(r['id'])}")
                c1, c2, c3 = st.columns(3)
                if c1.button("Approve as selected role", key=f"approve_{r['id']}", type="primary"):
                    execute("UPDATE users SET status='active', member_role=? WHERE id=?", (role_choice, int(r["id"])))
                    st.success("Member approved and role/category assigned.")
                    st.rerun()
                if c2.button("Reject", key=f"reject_{r['id']}"):
                    execute("UPDATE users SET status='rejected' WHERE id=?", (int(r["id"]),))
                    st.warning("Member request rejected.")
                    st.rerun()
                if c3.button("Mark abandoned", key=f"abandon_pending_{r['id']}"):
                    execute("UPDATE users SET status='abandoned' WHERE id=?", (int(r["id"]),))
                    st.warning("Request marked abandoned.")
                    st.rerun()

    with tab_add:
        st.markdown("Create a member directly and assign their business role/category at the same time.")
        with st.form("manual_add_member", clear_on_submit=True):
            c1, c2 = st.columns(2)
            username = c1.text_input("Username", placeholder="example: john")
            email = c2.text_input("Email for login", placeholder="member@email.com")
            full_name = st.text_input("Full name")
            c3, c4 = st.columns(2)
            phone = c3.text_input("Phone")
            password = c4.text_input("Temporary password", type="password")
            c5, c6 = st.columns(2)
            status = c5.selectbox("Initial status", ["active", "pending", "paused", "suspended"])
            member_role = c6.selectbox("Member role/category", role_opts)
            submitted = st.form_submit_button("Add member account", type="primary")
            if submitted:
                if not username or not full_name or not password:
                    st.error("Username, full name, and password are required.")
                else:
                    try:
                        create_member_account(username, password, full_name, email, phone, status, member_role)
                        st.success("Member account added. They can sign in using username or email when status is active.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("That username already exists. Choose another username.")

    with tab_assign:
        if df.empty:
            st.info("No member records yet.")
        else:
            st.markdown("### Quick assign member role/category")
            c1, c2 = st.columns(2)
            status_filter = c1.selectbox("Filter by status", ["All"] + status_opts, key="member_role_status_filter")
            role_filter = c2.selectbox("Filter by current role/category", ["All"] + role_opts, key="member_role_role_filter")
            view = df.copy()
            if status_filter != "All":
                view = view[view["status"] == status_filter]
            if role_filter != "All":
                view = view[view["member_role"].fillna("Standard Member") == role_filter]
            if view.empty:
                st.info("No members match this filter.")
            else:
                labels = [f"#{int(r['id'])} · {r['full_name']} · @{r['username']} · {r.get('member_role') or 'Standard Member'} · {r['status']}" for _, r in view.iterrows()]
                selected = st.selectbox("Select member", labels, key="quick_member_role_select")
                r = dict(view.iloc[labels.index(selected)])
                render_html(f'''
<div class="interaction-card">
  <div class="project-title">{esc(r.get('full_name'))}</div>
  <div>Username: <b>{esc(r.get('username'))}</b> · Email: <b>{esc(r.get('email') or '')}</b> · Phone: <b>{esc(r.get('phone') or '')}</b></div>
  <div style="margin-top:.45rem;">{status_badge(r.get('status'))} {member_role_badge(r.get('member_role'))}</div>
</div>
''')
                c3, c4 = st.columns(2)
                new_role = c3.selectbox("New member role/category", role_opts, index=role_opts.index(r.get("member_role")) if r.get("member_role") in role_opts else 0, key=f"new_member_role_{int(r['id'])}")
                new_status = c4.selectbox("Optional status", status_opts, index=status_opts.index(r.get("status")) if r.get("status") in status_opts else 0, key=f"new_member_status_{int(r['id'])}")
                if st.button("Save role/status assignment", type="primary", key=f"save_member_role_status_{int(r['id'])}"):
                    execute("UPDATE users SET member_role=?, status=? WHERE id=?", (new_role, new_status, int(r["id"])))
                    st.success("Member role/category and status updated.")
                    st.rerun()
                st.markdown("#### One-click common assignments")
                q1, q2, q3, q4 = st.columns(4)
                quicks = [
                    (q1, "Active Investor", "Investment Member", "active"),
                    (q2, "Premium", "Premium Investor", "active"),
                    (q3, "Project Partner", "Project Partner", "active"),
                    (q4, "Dormant", "Dormant / Monitoring", "paused"),
                ]
                for col, label, role_value, status_value in quicks:
                    if col.button(label, key=f"quick_{label}_{int(r['id'])}"):
                        execute("UPDATE users SET member_role=?, status=? WHERE id=?", (role_value, status_value, int(r["id"])))
                        st.success(f"Assigned {role_value} / {status_value}.")
                        st.rerun()

    with tab_control:
        if df.empty:
            st.info("No member records yet.")
        else:
            labels = [f"#{int(r['id'])} · {r['full_name']} · @{r['username']} · {r.get('member_role') or 'Standard Member'} · {r['status']}" for _, r in df.iterrows()]
            selected = st.selectbox("Select member to control", labels, key="member_control_select")
            r = dict(df.iloc[labels.index(selected)])
            render_html(f'''
<div class="interaction-card">
  <div class="project-title">{esc(r.get('full_name'))}</div>
  <div>Username: <b>{esc(r.get('username'))}</b> · Email: <b>{esc(r.get('email') or '')}</b> · Phone: <b>{esc(r.get('phone') or '')}</b></div>
  <div style="margin-top:.45rem;">{status_badge(r.get('status'))} {member_role_badge(r.get('member_role'))}</div>
  <div class="small-muted">Created: {esc(r.get('created_at') or '')}</div>
</div>
''')
            c1, c2, c3, c4, c5 = st.columns(5)
            actions = [
                (c1, "Activate", "active"),
                (c2, "Pause", "paused"),
                (c3, "Suspend", "suspended"),
                (c4, "Failed / abandon", "failed/abandoned"),
                (c5, "Remove", "removed"),
            ]
            for col, label, new_status in actions:
                if col.button(label, key=f"member_{new_status}_{r['id']}"):
                    execute("UPDATE users SET status=? WHERE id=?", (new_status, int(r["id"])))
                    st.success(f"Member status changed to {new_status}.")
                    st.rerun()

            with st.expander("Edit member details / role / reset password", expanded=False):
                with st.form(f"edit_member_{r['id']}"):
                    full_name = st.text_input("Full name", value=r.get("full_name") or "")
                    c6, c7 = st.columns(2)
                    email = c6.text_input("Email", value=r.get("email") or "")
                    phone = c7.text_input("Phone", value=r.get("phone") or "")
                    c8, c9 = st.columns(2)
                    member_role = c8.selectbox("Member role/category", role_opts, index=role_opts.index(r.get("member_role")) if r.get("member_role") in role_opts else 0)
                    status = c9.selectbox("Status", status_opts, index=status_opts.index(r.get("status")) if r.get("status") in status_opts else 0)
                    new_password = st.text_input("New password (leave blank to keep current)", type="password")
                    submitted = st.form_submit_button("Save member changes", type="primary")
                    if submitted:
                        execute("UPDATE users SET full_name=?, email=?, phone=?, member_role=?, status=? WHERE id=?", (full_name, email, phone, member_role, status, int(r["id"])))
                        if new_password:
                            execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new_password), int(r["id"])))
                        st.success("Member updated.")
                        st.rerun()

    with tab_table:
        if df.empty:
            st.info("No member records yet.")
        else:
            st.markdown('<div class="table-card">', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

def staff_accounts_page(user):
    hero("Staff Accounts", "Chairman-only area for creating and managing Manager, Secretary, and Chairman accounts.", ["Chairman control", "Staff roles", "Secure access"])
    if not can_manage_staff(user):
        st.error("Only the Chairman can manage staff accounts.")
        return
    with st.form("staff_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        username = c1.text_input("Username")
        role = c2.selectbox("Role", ["Chairman", "Manager", "Secretary"])
        password = c3.text_input("Password", type="password")
        full_name = st.text_input("Full name")
        c4, c5 = st.columns(2)
        email = c4.text_input("Email")
        phone = c5.text_input("Phone")
        if st.form_submit_button("Create staff account", type="primary"):
            if not username or not password or not full_name:
                st.error("Username, password, and full name are required.")
            else:
                try:
                    execute("INSERT INTO users(username,password_hash,role,full_name,email,phone,status) VALUES(?,?,?,?,?,?,?)", (username, hash_password(password), role, full_name, email, phone, "active"))
                    st.success("Staff account created.")
                except sqlite3.IntegrityError:
                    st.error("That username already exists.")
    df = query_df("SELECT id, username, role, full_name, email, phone, status, created_at FROM users WHERE role IN ('Chairman','Manager','Secretary') ORDER BY role, full_name")
    st.dataframe(df, use_container_width=True, hide_index=True)


def support_settings_page(staff=True, user=None):
    user = user or current_user()
    hero("Support Chat & Contacts", "Simple Enter-to-send public/member support chat with clear unread counts and no unnecessary send buttons.", ["Live chat area", "Admin inbox", "Reliable sending"])
    if staff:
        tab_settings, tab_public, tab_faq, tab_messages, tab_test = st.tabs(["Support & payment settings", "Public website content", "FAQ knowledge base", "Member messages", "Test chatbot"])
        with tab_settings:
            with st.form("support_settings"):
                whatsapp = st.text_input("WhatsApp support number", value=get_setting("whatsapp", "+254790240112"))
                email = st.text_input("Chairman email", value=get_setting("chairman_email", "zachariathinji@gmail.com"))
                hours = st.text_input("Business hours", value=get_setting("business_hours", "Monday to Saturday, 8:00 AM to 6:00 PM"))
                message = st.text_area("Fallback support message", value=get_setting("support_message", ""))
                chat_note = st.text_area("Quiet chat note shown to members", value=get_setting("chat_online_note", ""))
                st.markdown("### Payment instructions shown to members")
                mpesa_till = st.text_input("Official M-Pesa Till / Paybill / number", value=get_setting("mpesa_till_paybill", ""))
                mpesa_name = st.text_input("M-Pesa account / business name", value=get_setting("mpesa_account_name", "Zenvest Investment Holdings"))
                mpesa_account = st.text_input("Account/reference instruction", value=get_setting("mpesa_account_number", ""))
                payment_instructions = st.text_area("Detailed payment instructions", value=get_setting("payment_instructions", ""))
                if st.form_submit_button("Save support and payment settings", type="primary"):
                    update_setting("whatsapp", whatsapp)
                    update_setting("chairman_email", email)
                    update_setting("business_hours", hours)
                    update_setting("support_message", message)
                    update_setting("chat_online_note", chat_note)
                    update_setting("mpesa_till_paybill", mpesa_till)
                    update_setting("mpesa_account_name", mpesa_name)
                    update_setting("mpesa_account_number", mpesa_account)
                    update_setting("payment_instructions", payment_instructions)
                    st.success("Support and payment settings updated.")
            st.markdown("### Customer-support assignment")
            if can_manage_staff(user):
                staff_df = query_df("SELECT id, full_name, role, username FROM users WHERE role IN ('Chairman','Manager','Secretary') AND status='active' ORDER BY CASE role WHEN 'Chairman' THEN 1 WHEN 'Manager' THEN 2 ELSE 3 END, full_name")
                if staff_df.empty:
                    st.warning("No active staff accounts found.")
                else:
                    current_sid = get_support_staff_id()
                    staff_labels = [f"{r['full_name']} ({r['role']}) · @{r['username']}" for _, r in staff_df.iterrows()]
                    default_idx = 0
                    for i, (_, r) in enumerate(staff_df.iterrows()):
                        if int(r['id']) == int(current_sid or 0):
                            default_idx = i
                            break
                    selected_staff = st.selectbox("Choose the only admin who can reply to public/member chats", staff_labels, index=default_idx)
                    selected_id = int(staff_df.iloc[staff_labels.index(selected_staff)]['id'])
                    if st.button("Assign customer support admin", type="primary"):
                        update_setting("support_staff_user_id", str(selected_id))
                        st.success("Customer-support admin updated.")
                        st.rerun()
            else:
                st.info(f"Current customer-support admin: {support_staff_label()}. Only the Chairman can change this assignment.")
        with tab_public:
            with st.form("public_website_content_form"):
                public_hero_title = st.text_input("Public hero title", value=get_setting("public_hero_title", "Investment opportunities, products and performance in one secure portal"))
                public_hero_subtitle = st.text_area("Public hero subtitle", value=get_setting("public_hero_subtitle", ""))
                public_rate = st.text_input("Public investment rate / return guidance", value=get_setting("public_investment_rate", "Starter 8%–12% · Balanced 13%–18% · Expansion 19%–25%"))
                public_rate_note = st.text_area("Public rate note / disclaimer", value=get_setting("public_rate_note", ""))
                public_about = st.text_area("Public about Zenvest text", value=get_setting("public_about", ""))
                public_services_intro = st.text_area("Public services intro", value=get_setting("public_services_intro", ""))
                if st.form_submit_button("Save public website content", type="primary"):
                    update_setting("public_hero_title", public_hero_title)
                    update_setting("public_hero_subtitle", public_hero_subtitle)
                    update_setting("public_investment_rate", public_rate)
                    update_setting("public_rate_note", public_rate_note)
                    update_setting("public_about", public_about)
                    update_setting("public_services_intro", public_services_intro)
                    st.success("Public website content updated. It will appear on the public landing pages.")
            st.info("These fields control information visible before login, including the public investment rate shown on Home, Investments, Performance, and About pages.")

        with tab_faq:
            with st.form("faq_form", clear_on_submit=True):
                question = st.text_input("Question")
                answer = st.text_area("Answer")
                active = st.checkbox("Active", value=True)
                if st.form_submit_button("Add FAQ", type="primary"):
                    if not question or not answer:
                        st.error("Question and answer are required.")
                    else:
                        execute("INSERT INTO faqs(question,answer,active) VALUES(?,?,?)", (question, answer, 1 if active else 0))
                        st.success("FAQ added.")
            df = query_df("SELECT id, question, answer, active FROM faqs ORDER BY id DESC")
            st.dataframe(df, use_container_width=True, hide_index=True)
        with tab_messages:
            admin_chat_center(user)
        with tab_test:
            chatbot_widget(user=user, staff=True)
    else:
        chatbot_widget(user=user, staff=False)
        st.markdown('<div class="section-title">Visible contacts / names</div>', unsafe_allow_html=True)
        show_visible_directory(member_view=True)

def reports_page():
    hero("Reports", "Download project, product, member, transaction, and milestone records as CSV files.", ["CSV exports", "Records", "Transparency"])
    reports = {
        "Projects": query_df("SELECT * FROM projects"),
        "Products": query_df("SELECT * FROM products"),
        "Transactions": query_df("SELECT * FROM transactions"),
        "Investment Requests": get_investment_requests(),
        "Investment Activity Audit": query_df("SELECT * FROM investment_activity ORDER BY created_at DESC"),
        "Member Notifications": query_df("SELECT * FROM notifications ORDER BY created_at DESC"),
        "Chat Messages": query_df("SELECT * FROM chat_messages ORDER BY created_at DESC"),
        "Names Directory": query_df("SELECT * FROM people_directory ORDER BY created_at DESC"),
        "Milestones": query_df("SELECT * FROM milestones"),
        "Members": query_df("SELECT id, username, role, full_name, email, phone, status, created_at FROM users WHERE role='Member'"),
    }
    for name, df in reports.items():
        with st.expander(name, expanded=name == "Projects"):
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(f"Download {name} CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"zenvest_{name.lower()}.csv", mime="text/csv")


# =========================================================
# MEMBER PAGES
# =========================================================
def member_dashboard(user):
    hero("Member Dashboard", "Review investment opportunities, active products, project performance, milestones, notifications, and support options.", ["Investment opportunities", "Products", "Support"])
    member_notifications_panel(user, compact=True)
    projects = query_df("SELECT * FROM projects WHERE visibility IN ('Members Only','Public') AND status NOT IN ('Cancelled','Completed','Passed')")
    products = query_df("SELECT * FROM products WHERE status='Active'")
    tx = query_df("SELECT * FROM transactions")
    funding = tx[tx["tx_type"] == "Funding"]["amount"].sum() if not tx.empty else 0
    revenue = tx[tx["tx_type"] == "Revenue"]["amount"].sum() if not tx.empty else 0
    expense = tx[tx["tx_type"] == "Expense"]["amount"].sum() if not tx.empty else 0
    kpi_grid([
        ("📌", "Visible Projects", str(len(projects)), "Investment opportunities"),
        ("📦", "Active Products", str(len(products)), "Available offers"),
        ("💰", "Funding Recorded", money(funding), "Across visible projects"),
        ("🏁", "Net Result", money(revenue - expense), "Overall performance"),
    ])
    st.markdown('<div class="section-title">Quick links</div>', unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        quick_nav_button("📌 Investment Opportunities", "opportunities", "member_dash_opportunities")
    with q2:
        quick_nav_button("💳 My Investments", "my_investments", "member_dash_my_investments")
    with q3:
        quick_nav_button("📈 Project Performance", "performance", "member_dash_performance")
    with q4:
        quick_nav_button("💬 Support Chat", "support", "member_dash_support")
    if not projects.empty:
        st.markdown('<div class="section-title">Latest opportunity</div>', unsafe_allow_html=True)
        project_card(dict(projects.iloc[0]), show_button=True, button_label="Open this investment opportunity", key_prefix="latest_member_project")


def member_projects(user=None):
    user = user or current_user()
    hero("Investment Opportunities", "View upcoming projects, accept a project, and submit investment/payment details for admin review.", ["Accept project", "M-Pesa details", "Admin review"])
    df = query_df("SELECT * FROM projects WHERE visibility IN ('Members Only','Public') AND status NOT IN ('Cancelled','Completed','Passed') ORDER BY created_at DESC")
    if df.empty:
        st.info("No visible investment opportunities yet.")
        return
    labels = [f"{r['code']} — {r['title']}" for _, r in df.iterrows()]
    qp_project = qp_get("project_id", "")
    default_index = 0
    if qp_project:
        for i, (_, row) in enumerate(df.iterrows()):
            if str(int(row["id"])) == str(qp_project):
                default_index = i
                break
    selected = st.selectbox("Select opportunity", labels, index=default_index)
    project_id = int(df.iloc[labels.index(selected)]["id"])
    qp_set(project_id=project_id)
    show_project_full(project_id, staff_view=False)
    member_investment_action(project_id, user)


def member_products():
    hero("Products & Services", "Active products and services added by the Zenvest staff panel appear here automatically.", ["Dynamic product list", "Customer view", "Active offers"])
    show_products(public_only=True)


def member_performance():
    hero("Project Performance", "Track funding, revenue, expenses, profit/loss, progress, and expected end dates for visible projects.", ["Performance", "Charts", "Progress"])
    df = query_df("SELECT id, code, title FROM projects WHERE visibility IN ('Members Only','Public') AND status NOT IN ('Cancelled') ORDER BY created_at DESC")
    if df.empty:
        st.info("No visible projects yet.")
        return
    labels = [f"{r['code']} — {r['title']}" for _, r in df.iterrows()]
    qp_project = qp_get("project_id", "")
    default_index = 0
    if qp_project:
        for i, (_, row) in enumerate(df.iterrows()):
            if str(int(row["id"])) == str(qp_project):
                default_index = i
                break
    selected = st.selectbox("Select project", labels, index=default_index)
    project_id = int(df.iloc[labels.index(selected)]["id"])
    qp_set(project_id=project_id)
    show_financial_dashboard(project_id)


# =========================================================
# APP ROUTER
# =========================================================
def main():
    init_db()
    user = current_user()
    if not user:
        public_site_router()
        return
    sidebar(user)
    current_page_key = qp_get("page", "dashboard") or "dashboard"

    if is_staff(user):
        staff_chat_count = staff_unread_chat_count()
        staff_pages = [
            ("dashboard", "🏠 Dashboard"),
            ("projects", "📌 Upcoming Events / Projects"),
            ("investment_requests", "💳 Investment Requests"),
            ("products", "📦 Products & Services"),
            ("performance", "📈 Investment Performance"),
            ("completed", "🏁 Completed / Passed Archive"),
            ("members", "👥 Members"),
            ("directory", "👤 Names & Contacts"),
            ("support", f"💬 Support Chat & Inbox{chat_badge_text(staff_chat_count)}"),
            ("reports", "📄 Reports"),
        ]
        if can_manage_staff(user):
            staff_pages.insert(7, ("staff_accounts", "🧑‍💼 Staff Accounts"))
        keys = [k for k, _ in staff_pages]
        labels = [label for _, label in staff_pages]
        if current_page_key not in keys:
            current_page_key = "dashboard"
        page_label = st.sidebar.radio("Navigation", labels, index=nav_index(current_page_key, keys), label_visibility="collapsed")
        selected_key = keys[labels.index(page_label)]
        if selected_key != qp_get("page", ""):
            set_page(selected_key)

        if selected_key == "dashboard":
            staff_dashboard(user)
        elif selected_key == "projects":
            manage_projects()
        elif selected_key == "investment_requests":
            investment_requests_page(user)
        elif selected_key == "products":
            manage_products()
        elif selected_key == "performance":
            performance_page()
        elif selected_key == "completed":
            completed_projects_page()
        elif selected_key == "members":
            members_page(user)
        elif selected_key == "staff_accounts":
            staff_accounts_page(user)
        elif selected_key == "directory":
            names_directory_page(user)
        elif selected_key == "support":
            support_settings_page(staff=True, user=user)
        elif selected_key == "reports":
            reports_page()
    else:
        member_chat_count = member_unread_chat_count(int(user["id"]))
        member_pages = [
            ("dashboard", "🏠 Dashboard"),
            ("opportunities", "📌 Investment Opportunities"),
            ("my_investments", "💳 My Investments"),
            ("products", "📦 Products & Services"),
            ("performance", "📈 Project Performance"),
            ("support", f"💬 Support Chat & Contacts{chat_badge_text(member_chat_count)}"),
        ]
        keys = [k for k, _ in member_pages]
        labels = [label for _, label in member_pages]
        if current_page_key not in keys:
            current_page_key = "dashboard"
        page_label = st.sidebar.radio("Navigation", labels, index=nav_index(current_page_key, keys), label_visibility="collapsed")
        selected_key = keys[labels.index(page_label)]
        if selected_key != qp_get("page", ""):
            set_page(selected_key)

        if selected_key == "dashboard":
            member_dashboard(user)
        elif selected_key == "opportunities":
            member_projects(user)
        elif selected_key == "my_investments":
            member_investments_page(user)
        elif selected_key == "products":
            member_products()
        elif selected_key == "performance":
            member_performance()
        elif selected_key == "support":
            support_settings_page(staff=False, user=user)
    st.markdown('<div class="footer-note">Zenvest Investment Holdings · Streamlit visual business portal · Chairman, Manager, Secretary, Member access · Public support chat.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
