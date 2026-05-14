import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import calendar
from datetime import datetime, date

from db import *
from auth import authenticate, hash_password
from analytics import generate_kpis

# ─── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="PerfTrack",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

# ─── GLOBAL CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}

.stApp { background: #f0f2f5 !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div:first-child {
    background: #1a1f2e !important;
    background-color: #1a1f2e !important;
    border-right: none !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
section[data-testid="stSidebar"] *:not(button) { color: #c8d0e0 !important; }

.sidebar-logo {
    padding: 24px 20px 20px;
    border-bottom: 1px solid #2d3446;
}
.sidebar-logo-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 12px; display: flex;
    align-items: center; justify-content: center;
    font-size: 18px; margin-bottom: 10px;
}
.sidebar-logo-title { font-size: 16px !important; font-weight: 700 !important; color: #ffffff !important; letter-spacing: -0.3px; }
.sidebar-logo-sub   { font-size: 11px !important; color: #6b7a99 !important; margin-top: 2px; }

.sidebar-section-label {
    font-size: 10px !important; font-weight: 600 !important;
    color: #4b5675 !important; text-transform: uppercase;
    letter-spacing: 0.08em; padding: 16px 20px 6px;
}

div[data-testid="stSidebar"] .stRadio > label { display: none !important; }
div[data-testid="stSidebar"] .stRadio > div { gap: 1px !important; padding: 0 10px; }
div[data-testid="stSidebar"] .stRadio label {
    display: flex !important; align-items: center !important;
    padding: 9px 14px !important; border-radius: 8px !important;
    font-size: 13px !important; font-weight: 400 !important;
    color: #8d98b3 !important; cursor: pointer !important;
    transition: all 0.15s !important; margin: 1px 0 !important;
    border: none !important;
}
div[data-testid="stSidebar"] .stRadio label:hover {
    background: #242a3e !important; color: #c8d0e0 !important;
}
div[data-testid="stSidebar"] .stRadio label[data-testid="stMarkdownContainer"] { font-weight: 500 !important; }

.sidebar-user {
    padding: 14px 20px;
    border-top: 1px solid #2d3446;
    margin-top: auto;
}
.sidebar-user-name  { font-size: 13px !important; font-weight: 600 !important; color: #e2e7f0 !important; }
.sidebar-user-role  { font-size: 11px !important; color: #6b7a99 !important; margin-top: 2px; }

div[data-testid="stSidebar"] .stButton > button {
    background: #242a3e !important;
    color: #8d98b3 !important;
    border: 1px solid #2d3446 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    padding: 7px 14px !important;
    width: 100%;
    box-shadow: none !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: #2d3446 !important;
    color: #c8d0e0 !important;
    box-shadow: none !important;
}

/* ── Page shell ── */
.page-header {
    background: #ffffff;
    border-bottom: 1px solid #e4e7ec;
    padding: 20px 32px;
    display: flex; align-items: center; justify-content: space-between;
}
.page-title    { font-size: 17px; font-weight: 700; color: #101828; }
.page-subtitle { font-size: 12px; color: #98a2b3; margin-top: 3px; }
.badge-coordinator {
    display: inline-flex; align-items: center; gap: 6px;
    background: #eef2ff; color: #4f46e5;
    font-size: 12px; font-weight: 500;
    padding: 5px 14px; border-radius: 20px; border: 1px solid #c7d2fe;
}
.badge-employee {
    display: inline-flex; align-items: center; gap: 6px;
    background: #f0fdf4; color: #16a34a;
    font-size: 12px; font-weight: 500;
    padding: 5px 14px; border-radius: 20px; border: 1px solid #bbf7d0;
}

/* ── KPI cards ── */
.kpi-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 16px; padding: 24px 32px 0;
}
.kpi-card {
    background: #ffffff; border: 1px solid #e4e7ec;
    border-radius: 16px; padding: 20px 22px;
    position: relative; overflow: hidden;
    transition: box-shadow 0.2s, transform 0.2s;
}
.kpi-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.07); transform: translateY(-1px); }
.kpi-accent {
    position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 16px 16px 0 0;
}
.kpi-icon {
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; margin-bottom: 14px;
}
.kpi-label { font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.07em; color: #98a2b3; margin-bottom: 6px; }
.kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 32px; font-weight: 700; line-height: 1; color: #101828; }
.kpi-sub   { font-size: 11px; margin-top: 8px; color: #98a2b3; }
.kpi-up    { color: #16a34a !important; }
.kpi-down  { color: #dc2626 !important; }

/* ── Content area ── */
.content-area { padding: 24px 32px; }

/* ── Cards ── */
.card {
    background: #ffffff; border: 1px solid #e4e7ec;
    border-radius: 16px; padding: 20px 22px; margin-bottom: 16px;
}
.card-title { font-size: 14px; font-weight: 600; color: #101828; margin-bottom: 14px; }

/* ── Employee card ── */
.emp-card {
    background: #ffffff; border: 1px solid #e4e7ec;
    border-radius: 14px; padding: 16px 20px;
    margin-bottom: 10px; transition: box-shadow 0.15s;
}
.emp-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
.emp-avatar {
    width: 42px; height: 42px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 700; color: white; flex-shrink: 0;
}
.emp-name   { font-size: 14px; font-weight: 600; color: #101828; }
.emp-meta   { font-size: 12px; color: #98a2b3; margin-top: 2px; }

/* ── Task pill ── */
.task-row {
    background: #ffffff; border: 1px solid #e4e7ec;
    border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 12px;
    transition: box-shadow 0.15s;
}
.task-row:hover { box-shadow: 0 3px 12px rgba(0,0,0,0.05); }
.status-pill {
    font-size: 11px; font-weight: 500;
    padding: 3px 10px; border-radius: 20px; white-space: nowrap;
}
.priority-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

/* ── Calendar ── */
.cal-wrap { background: #ffffff; border: 1px solid #e4e7ec; border-radius: 16px; padding: 20px; }
.cal-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.cal-title  { font-size: 15px; font-weight: 600; color: #101828; }
.cal-grid   { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
.cal-dow    { text-align: center; font-size: 11px; font-weight: 600; color: #98a2b3; padding: 6px 0; text-transform: uppercase; }
.cal-day    { min-height: 76px; border: 1px solid #e4e7ec; border-radius: 10px; padding: 7px; background: #f9fafb; transition: all 0.15s; cursor: default; }
.cal-day:hover { border-color: #c7d2fe; }
.cal-day.today  { border-color: #6366f1; background: #eef2ff; }
.cal-day.logged { background: #f0fdf4; border-color: #86efac; }
.cal-day.empty  { background: transparent !important; border: 1px solid transparent !important; }
.cal-daynum     { font-size: 11px; font-weight: 600; color: #475569; }
.cal-day.today .cal-daynum { color: #4f46e5; }
.cal-pill {
    font-size: 10px; background: #6366f1; color: white;
    border-radius: 4px; padding: 2px 6px; margin-top: 3px;
    font-family: 'JetBrains Mono', monospace; display: inline-block;
}
.cal-day.logged .cal-pill { background: #16a34a; }

/* ── Interactions ── */
.interaction-card {
    background: #fff; border: 1px solid #e4e7ec; border-radius: 12px;
    padding: 14px 16px; margin-bottom: 8px;
    border-left: 3px solid #6366f1;
}

/* ── Labels ── */
label, .stTextInput label, .stTextArea label, .stSelectbox label,
.stNumberInput label, .stDateInput label, .stTimeInput label,
.stSlider label, .stRadio label,
p[data-testid="stMarkdownContainer"] {
    color: #374151 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}
/* Streamlit widget labels */
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stTimeInput"] label,
div[data-testid="stSlider"] label {
    color: #374151 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    margin-bottom: 4px !important;
}

/* ── Forms ── */
div[data-testid="stForm"] {
    background: #ffffff !important; border: 1px solid #e4e7ec !important;
    border-radius: 16px !important; padding: 24px !important;
}
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background: #f9fafb !important; border: 1px solid #e4e7ec !important;
    border-radius: 10px !important; color: #101828 !important;
    font-size: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
.stSelectbox > div > div {
    background: #f9fafb !important; border: 1px solid #e4e7ec !important;
    border-radius: 10px !important; color: #101828 !important;
}
/* Selectbox text */
.stSelectbox > div > div > div { color: #101828 !important; }

/* ── Buttons — ALL contexts ── */
.stButton > button,
div[data-testid="stForm"] .stButton > button,
div[data-testid="stFormSubmitButton"] > button,
button[kind="formSubmit"], button[kind="primary"] {
    background: #6366f1 !important; color: #ffffff !important;
    border: none !important; border-radius: 10px !important;
    padding: 10px 22px !important; font-size: 14px !important;
    font-weight: 500 !important; transition: background 0.2s !important;
    box-shadow: none !important;
}
.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background: #4f46e5 !important; color: #ffffff !important;
}

/* ── Expanders ── */
div[data-testid="stExpander"] {
    background: #ffffff !important; border: 1px solid #e4e7ec !important;
    border-radius: 14px !important; margin-bottom: 10px !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"] summary {
    background: #ffffff !important; color: #101828 !important;
    font-size: 14px !important; font-weight: 500 !important;
    padding: 14px 18px !important;
}
div[data-testid="stExpander"] summary:hover { background: #f9fafb !important; }
div[data-testid="stExpander"] > div[data-testid="stExpanderDetails"] {
    background: #ffffff !important; padding: 0 18px 16px !important;
}

/* ── Number input ── */
div[data-testid="stNumberInput"] input { color: #101828 !important; }
div[data-testid="stNumberInput"] button {
    background: #f9fafb !important; border-color: #e4e7ec !important;
    color: #374151 !important;
}

/* ── Date / Time inputs ── */
div[data-testid="stDateInput"] input,
div[data-testid="stTimeInput"] input {
    color: #101828 !important; background: #f9fafb !important;
    border: 1px solid #e4e7ec !important; border-radius: 10px !important;
}

/* ── Slider ── */
div[data-testid="stSlider"] [data-testid="stThumbValue"],
div[data-testid="stSlider"] [data-testid="stTickBarMin"],
div[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: #374151 !important;
}
div[data-testid="stSlider"] [role="slider"] { background: #6366f1 !important; }

/* ── Radio ── */
div[data-testid="stRadio"] label { color: #374151 !important; font-size: 13px !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] { color: #64748b !important; }
.stTabs [aria-selected="true"] { color: #101828 !important; }

/* ── General text ── */
.stApp p, .stApp span, .stApp div { color: inherit; }
.stMarkdown p { color: #374151 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f9fafb !important; border-radius: 12px !important;
    padding: 4px !important; border: 1px solid #e4e7ec !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important; padding: 8px 18px !important;
    font-size: 13px !important; font-weight: 500 !important;
    color: #64748b !important; background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important; color: #101828 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
}

/* ── Misc ── */
.stDataFrame { border-radius: 12px !important; border: 1px solid #e4e7ec !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 10px; }
.stAlert { border-radius: 12px !important; }
div[data-testid="stExpander"] {
    background: #ffffff !important; border: 1px solid #e4e7ec !important;
    border-radius: 14px !important;
}
h1, h2, h3, h4 { color: #101828 !important; }
.spacer-sm { height: 12px; }
.spacer-md { height: 20px; }
.spacer-lg { height: 32px; }

/* ── Login page ── */
.login-shell {
    min-height: 100vh; background: linear-gradient(135deg, #1a1f2e 0%, #252d40 100%);
    display: flex; align-items: center; justify-content: center;
}
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ──────────────────────────────────────────────────
DEPT_COLORS = {
    "Engineering": "#6366f1", "Design": "#8b5cf6",
    "Marketing": "#06b6d4",   "Sales": "#f59e0b",
    "Support": "#ef4444",     "Finance": "#10b981", "HR": "#ec4899",
}
AVATAR_COLORS = ["#6366f1","#8b5cf6","#06b6d4","#f59e0b","#ef4444","#10b981","#ec4899","#3b82f6"]
STATUS_COLORS = {"Completed": "#16a34a", "In Progress": "#6366f1", "Pending": "#f59e0b"}
PLOTLY_BASE   = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", size=12, color="#64748b"),
    margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
)

# ─── SESSION ────────────────────────────────────────────────────
for k, v in [("logged_in", False), ("role", None), ("employee_row", None), ("username", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─── LOGIN ──────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1a1f2e 0%, #252d40 100%) !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center;margin-bottom:32px'>
            <div style='display:inline-flex;align-items:center;justify-content:center;
                        width:56px;height:56px;background:linear-gradient(135deg,#6366f1,#8b5cf6);
                        border-radius:16px;font-size:26px;margin-bottom:14px;box-shadow:0 8px 24px rgba(99,102,241,0.35)'>📊</div>
            <div style='font-size:26px;font-weight:700;color:#ffffff;letter-spacing:-0.5px'>PerfTrack</div>
            <div style='font-size:14px;color:#6b7a99;margin-top:5px'>Workforce Management Platform</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign in →", use_container_width=True)
            if submitted:
                result = authenticate(username, password)
                if result:
                    role, emp_row = result
                    st.session_state.logged_in   = True
                    st.session_state.role        = role
                    st.session_state.username    = username
                    st.session_state.employee_row = emp_row
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.markdown("""
        <div style='margin-top:16px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                    border-radius:12px;padding:14px 18px;font-size:12px;color:#6b7a99;text-align:center'>
            Coordinator: <code style='color:#a5b4fc'>admin</code> / <code style='color:#a5b4fc'>admin123</code>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

ROLE = st.session_state.role
EMP  = st.session_state.employee_row

# ─── DATA LOADERS ───────────────────────────────────────────────
@st.cache_data(ttl=10)
def load_employees():
    return pd.DataFrame(
        get_employees(),
        columns=["id","name","department","email","role","active","username","password_hash","created_at"]
    )

@st.cache_data(ttl=10)
def load_tasks(employee_id=None):
    rows = get_tasks(employee_id)
    if rows:
        return pd.DataFrame(rows, columns=["id","employee_id","title","status","priority","hours","created_at"])
    return pd.DataFrame(columns=["id","employee_id","title","status","priority","hours","created_at"])

@st.cache_data(ttl=10)
def load_work_logs(employee_id=None, month=None, year=None):
    rows = get_work_logs(employee_id, month, year)
    if rows:
        return pd.DataFrame(rows, columns=["id","employee_id","log_date","start_time","end_time","hours_worked","note","created_at"])
    return pd.DataFrame(columns=["id","employee_id","log_date","start_time","end_time","hours_worked","note","created_at"])

def avatar_color(name, idx=0):
    return AVATAR_COLORS[idx % len(AVATAR_COLORS)]

def initials(name):
    parts = name.strip().split()
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()

# ─── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    role_label = "Project Coordinator" if ROLE == "admin" else "Employee"
    display_name = st.session_state.username if ROLE == "admin" else (EMP[1] if EMP else "Employee")

    st.markdown(f"""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">📊</div>
        <div class="sidebar-logo-title">PerfTrack</div>
        <div class="sidebar-logo-sub">Workforce Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)

    if ROLE == "admin":
        page = st.radio("nav", [
            "📊  Dashboard",
            "👥  Employees",
            "✅  Tasks",
            "💬  Interactions",
        ], label_visibility="collapsed")
    else:
        page = st.radio("nav", [
            "🏠  My Overview",
            "📅  Work Calendar",
            "✅  My Tasks",
        ], label_visibility="collapsed")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sidebar-user">
        <div class="sidebar-user-name">{display_name}</div>
        <div class="sidebar-user-role">{role_label}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Sign out", use_container_width=True):
        for k in ["logged_in","role","username","employee_row"]:
            st.session_state[k] = False if k == "logged_in" else None
        load_employees.clear(); load_tasks.clear(); load_work_logs.clear()
        st.rerun()

# ═══════════════════════════════════════════════════════════════
#  ADMIN — DASHBOARD
# ═══════════════════════════════════════════════════════════════
if ROLE == "admin" and "Dashboard" in page:
    employees = load_employees()
    tasks     = load_tasks()
    kpis      = generate_kpis(employees, tasks)

    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">Dashboard</div>
            <div class="page-subtitle">Live workforce overview</div>
        </div>
        <div class="badge-coordinator">🎯 Project Coordinator</div>
    </div>
    """, unsafe_allow_html=True)

    active_count = len(employees[employees["active"] == 1]) if not employees.empty else 0
    cr = kpis.get("completion_rate", 0)

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-accent" style="background:#6366f1"></div>
            <div class="kpi-icon" style="background:#eef2ff">👥</div>
            <div class="kpi-label">Active Employees</div>
            <div class="kpi-value" style="color:#6366f1">{active_count}</div>
            <div class="kpi-sub">of {kpis.get('employees',0)} total</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-accent" style="background:#f59e0b"></div>
            <div class="kpi-icon" style="background:#fffbeb">📋</div>
            <div class="kpi-label">Total Tasks</div>
            <div class="kpi-value" style="color:#f59e0b">{kpis.get('tasks',0)}</div>
            <div class="kpi-sub">Across all team</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-accent" style="background:#10b981"></div>
            <div class="kpi-icon" style="background:#ecfdf5">✅</div>
            <div class="kpi-label">Completed</div>
            <div class="kpi-value" style="color:#10b981">{kpis.get('completed',0)}</div>
            <div class="kpi-sub kpi-up">↑ On track</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-accent" style="background:#8b5cf6"></div>
            <div class="kpi-icon" style="background:#f5f3ff">📈</div>
            <div class="kpi-label">Completion Rate</div>
            <div class="kpi-value" style="color:#8b5cf6">{cr}%</div>
            <div class="kpi-sub {'kpi-up' if cr >= 60 else 'kpi-down'}">{'↑ Above target' if cr >= 60 else '↓ Below 60% target'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
    st.markdown('<div style="padding: 0 32px">', unsafe_allow_html=True)

    c1, c2 = st.columns([1.6, 1], gap="medium")
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Department Workload · Hours</div>', unsafe_allow_html=True)
        if not tasks.empty and not employees.empty:
            merged = tasks.merge(employees[["id","department"]], left_on="employee_id", right_on="id")
            dept_h = merged.groupby("department")["hours"].sum().reset_index().sort_values("hours", ascending=False)
            dept_h["color"] = dept_h["department"].map(lambda d: DEPT_COLORS.get(d,"#6366f1"))
            fig = go.Figure(go.Bar(
                x=dept_h["department"], y=dept_h["hours"],
                marker_color=dept_h["color"], marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>%{y:.0f} hrs<extra></extra>"
            ))
            fig.update_layout(**PLOTLY_BASE, height=220,
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False), bargap=0.4)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No task data yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Task Status</div>', unsafe_allow_html=True)
        if not tasks.empty:
            sc = tasks["status"].value_counts().reset_index()
            sc.columns = ["status","count"]
            sc["color"] = sc["status"].map(lambda s: STATUS_COLORS.get(s,"#94a3b8"))
            fig2 = go.Figure(go.Pie(
                labels=sc["status"], values=sc["count"], hole=0.65,
                marker=dict(colors=sc["color"], line=dict(width=0)),
                hovertemplate="<b>%{label}</b><br>%{value} tasks<extra></extra>",
                textinfo="none"
            ))
            pie_layout = {**PLOTLY_BASE, "height": 220, "showlegend": True,
                "legend": dict(orientation="v", x=1.0, y=0.5, font=dict(size=11)),
                "annotations": [dict(text=f"<b>{cr}%</b>", x=0.5, y=0.5,
                                  font=dict(size=18, color="#101828"), showarrow=False,
                                  xref="paper", yref="paper")]}
            fig2.update_layout(**pie_layout)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No tasks yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Team roster
    st.markdown('<div class="card-title" style="margin-top:8px">Team Roster</div>', unsafe_allow_html=True)
    if not employees.empty:
        for i, (_, emp) in enumerate(employees.iterrows()):
            color  = avatar_color(emp["name"], i)
            init   = initials(emp["name"])
            status = "Active" if emp["active"] == 1 else "Inactive"
            sc     = "#10b981" if emp["active"] == 1 else "#ef4444"
            emp_tasks = load_tasks(int(emp["id"]))
            done = len(emp_tasks[emp_tasks["status"]=="Completed"]) if not emp_tasks.empty else 0
            tot  = len(emp_tasks)
            st.markdown(f"""
            <div class="emp-card" style="display:flex;align-items:center;gap:14px">
                <div class="emp-avatar" style="background:{color}">{init}</div>
                <div style="flex:1">
                    <div class="emp-name">{emp['name']}</div>
                    <div class="emp-meta">{emp['department']} · {emp['role']}</div>
                </div>
                <div style="text-align:center;min-width:70px">
                    <div style="font-size:11px;color:#98a2b3">Tasks</div>
                    <div style="font-size:14px;font-weight:600;color:#6366f1;font-family:'JetBrains Mono',monospace">{done}/{tot}</div>
                </div>
                <span style="font-size:11px;font-weight:500;padding:4px 12px;border-radius:20px;
                             background:{sc}1a;color:{sc};border:1px solid {sc}44">{status}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No employees yet.")

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  ADMIN — EMPLOYEES
# ═══════════════════════════════════════════════════════════════
elif ROLE == "admin" and "Employees" in page:

    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">Employee Management</div>
            <div class="page-subtitle">Add, view and remove team members</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-area" style="padding-top:0">', unsafe_allow_html=True)

    tab_add, tab_list = st.tabs(["➕  Add Employee", "👥  All Employees"])

    with tab_add:
        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
        col_f, col_info = st.columns([1, 1.1], gap="large")
        with col_f:
            with st.form("emp_add_form", clear_on_submit=True):
                st.markdown("**Employee Details**")
                name       = st.text_input("Full name",        placeholder="e.g. Aoife Murphy")
                department = st.text_input("Department",        placeholder="e.g. Engineering")
                email      = st.text_input("Work email",        placeholder="aoife@company.com")
                role       = st.text_input("Job title",         placeholder="e.g. Senior Developer")
                st.divider()
                st.markdown("**Login Credentials**")
                emp_username = st.text_input("Username",        placeholder="e.g. aoife.murphy")
                emp_password = st.text_input("Temporary password", type="password", placeholder="Min 6 characters")
                submitted = st.form_submit_button("Add Employee", use_container_width=True)
                if submitted:
                    if not name or not email:
                        st.error("Name and email are required.")
                    elif not emp_username or not emp_password:
                        st.error("Username and password are required.")
                    elif len(emp_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        try:
                            ph = hash_password(emp_password)
                            add_employee(name, department, email, role, emp_username, ph)
                            log_action(f"Added employee: {name}", "admin")
                            st.success(f"✓ {name} added — username: **{emp_username}**")
                            load_employees.clear()
                        except Exception as e:
                            st.error(str(e))

        with col_info:
            st.markdown("""
            <div style='background:#eef2ff;border:1px solid #c7d2fe;border-radius:14px;padding:20px'>
                <div style='font-size:14px;font-weight:600;color:#4f46e5;margin-bottom:10px'>How it works</div>
                <div style='font-size:13px;color:#374151;line-height:1.9'>
                    ① Each employee gets a unique username & password<br>
                    ② They sign in from the same login screen<br>
                    ③ Employees can log hours on their calendar<br>
                    ④ Employees can view & update their own tasks<br>
                    ⑤ Only you (Coordinator) can manage employees & assign tasks
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_list:
        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
        employees = load_employees()
        if employees.empty:
            st.info("No employees yet. Use the Add Employee tab.")
        else:
            for i, (_, emp) in enumerate(employees.iterrows()):
                color     = avatar_color(emp["name"], i)
                init      = initials(emp["name"])
                is_active = emp["active"] == 1
                sc        = "#10b981" if is_active else "#ef4444"
                status    = "Active" if is_active else "Inactive"
                emp_tasks = load_tasks(int(emp["id"]))
                done      = len(emp_tasks[emp_tasks["status"]=="Completed"]) if not emp_tasks.empty else 0
                total     = len(emp_tasks)
                rating    = calculate_employee_rating(int(emp["id"]))
                star_str  = "⭐" * min(int(rating), 5)
                exp_key   = f"emp_expanded_{emp['id']}"
                if exp_key not in st.session_state:
                    st.session_state[exp_key] = False
                is_open = st.session_state[exp_key]

                # Card header — always visible
                h_col, t_col = st.columns([6, 1])
                with h_col:
                    st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:14px;
                                background:#ffffff;border:1px solid #e4e7ec;
                                border-radius:{"14px 14px 0 0" if is_open else "14px"};
                                padding:14px 18px;margin-top:8px;cursor:pointer'>
                        <div class="emp-avatar" style="background:{color}">{init}</div>
                        <div style="flex:1">
                            <div style="font-size:14px;font-weight:600;color:#101828">{emp['name']}</div>
                            <div style="font-size:12px;color:#98a2b3;margin-top:2px">{emp['department']} · {emp['role']}</div>
                        </div>
                        <div style="text-align:center;margin-right:16px">
                            <div style="font-size:10px;color:#98a2b3;font-weight:500">TASKS</div>
                            <div style="font-size:16px;font-weight:700;color:#6366f1;font-family:'JetBrains Mono',monospace">{done}/{total}</div>
                        </div>
                        <span style="font-size:11px;font-weight:500;padding:4px 12px;border-radius:20px;
                                     background:{sc}1a;color:{sc};border:1px solid {sc}44;margin-right:8px">{status}</span>
                        <span style="font-size:16px;color:#98a2b3">{"▲" if is_open else "▼"}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with t_col:
                    st.markdown('<div style="margin-top:8px"></div>', unsafe_allow_html=True)
                    btn_label = "▲ Collapse" if is_open else "▼ Expand"
                    if st.button(btn_label, key=f"toggle_{emp['id']}", use_container_width=True):
                        st.session_state[exp_key] = not is_open
                        st.rerun()

                # Expanded detail panel
                if is_open:
                    st.markdown(f"""
                    <div style='background:#f9fafb;border:1px solid #e4e7ec;border-top:none;
                                border-radius:0 0 14px 14px;padding:18px 20px;margin-bottom:4px'>
                        <div style='display:flex;gap:16px;flex-wrap:wrap'>
                            <div style='flex:2;min-width:200px'>
                                <div style='font-size:12px;color:#64748b;margin-bottom:3px'>📧 {emp['email']}</div>
                                <div style='font-size:12px;color:#64748b;margin-bottom:3px'>👤 @{emp['username'] or "—"}</div>
                                <div style='font-size:12px;color:#64748b'>🏢 {emp['department']} · {emp['role']}</div>
                            </div>
                            <div style='background:#ffffff;border:1px solid #e4e7ec;border-radius:10px;
                                        padding:12px 16px;text-align:center;min-width:100px'>
                                <div style='font-size:10px;color:#98a2b3;font-weight:600;text-transform:uppercase'>Rating</div>
                                <div style='font-size:18px;margin-top:4px'>{star_str}</div>
                                <div style='font-size:12px;color:#6366f1;font-weight:600;font-family:"JetBrains Mono",monospace'>{rating}/5</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    btn_col1, btn_col2, _ = st.columns([1.2, 1.2, 4])
                    with btn_col1:
                        if is_active:
                            if st.button("⏸ Deactivate", key=f"deact_{emp['id']}", use_container_width=True):
                                deactivate_employee(int(emp["id"]))
                                log_action(f"Deactivated: {emp['name']}", "admin")
                                load_employees.clear(); st.rerun()
                    with btn_col2:
                        if st.button("🗑 Remove", key=f"del_{emp['id']}", use_container_width=True):
                            delete_employee(int(emp["id"]))
                            log_action(f"Deleted: {emp['name']}", "admin")
                            load_employees.clear(); load_tasks.clear(); st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  ADMIN — TASKS
# ═══════════════════════════════════════════════════════════════
elif ROLE == "admin" and "Tasks" in page:

    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">Task Management</div>
            <div class="page-subtitle">Assign and track tasks across your team</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-area" style="padding-top:0">', unsafe_allow_html=True)

    employees = load_employees()
    active_emps = employees[employees["active"] == 1] if not employees.empty else pd.DataFrame()
    emp_options = {row["name"]: row["id"] for _, row in active_emps.iterrows()} if not active_emps.empty else {}

    tab_assign, tab_all = st.tabs(["➕  Assign Task", "📋  All Tasks"])

    with tab_assign:
        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
        col_f, _ = st.columns([1, 1.2], gap="large")
        with col_f:
            if not emp_options:
                st.warning("Add active employees first.")
            else:
                with st.form("task_add_form", clear_on_submit=True):
                    emp_name = st.selectbox("Assign to", list(emp_options.keys()))
                    title    = st.text_input("Task title", placeholder="e.g. Q3 performance review")
                    c1, c2  = st.columns(2)
                    with c1:
                        status = st.selectbox("Initial status", ["Pending","In Progress","Completed"])
                    with c2:
                        priority = st.selectbox("Priority", ["Low","Medium","High"])
                    hours = st.number_input("Estimated hours", min_value=0.5, step=0.5, value=1.0)
                    submitted = st.form_submit_button("Assign Task", use_container_width=True)
                    if submitted:
                        if not title:
                            st.error("Task title is required.")
                        else:
                            add_task(emp_options[emp_name], title, status, priority, hours)
                            log_action(f"Task '{title}' → {emp_name}", "admin")
                            st.success(f"✓ Task assigned to {emp_name}.")
                            load_tasks.clear()

    with tab_all:
        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
        # Filter
        filter_opts = {"All employees": None}
        filter_opts.update({emp["name"]: emp["id"] for _, emp in employees.iterrows()})
        sel_filter = st.selectbox("Filter by employee", list(filter_opts.keys()), key="task_filter_sel")
        filter_id = filter_opts[sel_filter]

        tasks = load_tasks(filter_id)
        if tasks.empty:
            st.info("No tasks found.")
        else:
            merged = tasks.copy()
            if not employees.empty:
                merged = tasks.merge(employees[["id","name","department"]], left_on="employee_id", right_on="id", suffixes=("","_emp"))
            else:
                merged["name"] = "Unknown"; merged["department"] = "—"

            for _, task in merged.iterrows():
                sc   = STATUS_COLORS.get(task["status"], "#94a3b8")
                pr_c = {"High":"#ef4444","Medium":"#f59e0b","Low":"#10b981"}.get(task["priority"],"#94a3b8")
                col_info, col_status, col_del = st.columns([4, 1.5, 0.7])
                with col_info:
                    st.markdown(f"""
                    <div class="task-row" style="border-left:3px solid {sc}">
                        <div class="priority-dot" style="background:{pr_c}"></div>
                        <div style="flex:1">
                            <div style='font-size:13px;font-weight:500;color:#101828'>{task['title']}</div>
                            <div style='font-size:11px;color:#98a2b3;margin-top:3px'>
                                👤 {task.get('name','—')} · {task.get('department','—')} · {task['hours']}h
                                <span style='color:{pr_c};font-weight:500;margin-left:4px'>{task['priority']}</span>
                            </div>
                        </div>
                        <span class="status-pill" style="background:{sc}1a;color:{sc};border:1px solid {sc}44">{task['status']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_status:
                    new_status = st.selectbox(
                        "Status", ["Pending","In Progress","Completed"],
                        index=["Pending","In Progress","Completed"].index(task["status"]),
                        key=f"admin_task_status_{task['id']}",
                        label_visibility="collapsed"
                    )
                    if st.button("Save", key=f"admin_task_save_{task['id']}", use_container_width=True):
                        update_task_status(int(task["id"]), new_status)
                        load_tasks.clear(); st.rerun()
                with col_del:
                    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                    if st.button("🗑", key=f"del_task_{task['id']}", use_container_width=True):
                        delete_task(int(task["id"]))
                        load_tasks.clear(); st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  ADMIN — INTERACTIONS
# ═══════════════════════════════════════════════════════════════
elif ROLE == "admin" and "Interactions" in page:

    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">Interactions</div>
            <div class="page-subtitle">Log team interactions and performance notes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
    st.markdown('<div class="content-area" style="padding-top:0">', unsafe_allow_html=True)

    employees = load_employees()
    emp_opts  = {emp["name"]: emp["id"] for _, emp in employees.iterrows()} if not employees.empty else {}

    col_form, col_log = st.columns([1, 1.4], gap="large")

    with col_form:
        if not emp_opts:
            st.warning("No employees to log interactions for.")
        else:
            with st.form("interaction_form", clear_on_submit=True):
                st.markdown("**Log Interaction**")
                emp_name = st.selectbox("Employee", list(emp_opts.keys()))
                itype    = st.selectbox("Type", ["1-on-1","Meeting","Review","Client Call","Support"])
                score    = st.slider("Performance score", 1, 5, 3, help="1 = needs improvement · 5 = exceptional")
                note     = st.text_area("Notes", placeholder="Key points from the interaction…", height=100)
                sub      = st.form_submit_button("Log Interaction", use_container_width=True)
                if sub:
                    add_interaction(emp_opts[emp_name], itype, score, note)
                    log_action(f"Interaction for {emp_name}", "admin")
                    st.success("✓ Interaction logged.")

    with col_log:
        st.markdown("**Recent Interactions**")
        rows = get_interactions()
        if rows:
            df = pd.DataFrame(rows, columns=["id","employee_id","type","score","note","created_at"])
            emp_map = {emp["id"]: emp["name"] for _, emp in employees.iterrows()} if not employees.empty else {}
            df["employee"] = df["employee_id"].map(emp_map)
            for _, r in df.head(15).iterrows():
                stars = "⭐" * int(r["score"])
                st.markdown(f"""
                <div class="interaction-card">
                    <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:5px'>
                        <div style='font-size:13px;font-weight:600;color:#101828'>{r.get('employee','—')}</div>
                        <div style='font-size:13px'>{stars}</div>
                    </div>
                    <div style='font-size:11px;color:#98a2b3;margin-bottom:6px'>
                        {r['type']} · {str(r['created_at'])[:10]}
                    </div>
                    {f'<div style="font-size:12px;color:#374151">{r["note"]}</div>' if r['note'] else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No interactions logged yet.")

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  EMPLOYEE VIEWS
# ═══════════════════════════════════════════════════════════════
elif ROLE == "employee":
    emp_id   = EMP[0]
    emp_name = EMP[1]
    emp_dept = EMP[2]
    emp_role = EMP[4]

    # ─── EMPLOYEE — OVERVIEW ──────────────────────────────────
    if "Overview" in page:
        st.markdown(f"""
        <div class="page-header">
            <div>
                <div class="page-title">Welcome back, {emp_name.split()[0]} 👋</div>
                <div class="page-subtitle">{emp_dept} · {emp_role}</div>
            </div>
            <div class="badge-employee">● Employee Portal</div>
        </div>
        """, unsafe_allow_html=True)

        my_tasks = load_tasks(emp_id)
        all_logs = load_work_logs(emp_id)

        today = date.today()
        logs_this_month = load_work_logs(emp_id, today.month, today.year)

        total_t     = len(my_tasks)
        completed_t = len(my_tasks[my_tasks["status"] == "Completed"]) if not my_tasks.empty else 0
        pending_t   = len(my_tasks[my_tasks["status"] == "Pending"])   if not my_tasks.empty else 0
        hours_month = logs_this_month["hours_worked"].sum() if not logs_this_month.empty else 0

        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-accent" style="background:#6366f1"></div>
                <div class="kpi-icon" style="background:#eef2ff">📋</div>
                <div class="kpi-label">My Tasks</div>
                <div class="kpi-value" style="color:#6366f1">{total_t}</div>
                <div class="kpi-sub">Total assigned</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-accent" style="background:#10b981"></div>
                <div class="kpi-icon" style="background:#ecfdf5">✅</div>
                <div class="kpi-label">Completed</div>
                <div class="kpi-value" style="color:#10b981">{completed_t}</div>
                <div class="kpi-sub kpi-up">↑ Done</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-accent" style="background:#f59e0b"></div>
                <div class="kpi-icon" style="background:#fffbeb">⏳</div>
                <div class="kpi-label">Pending</div>
                <div class="kpi-value" style="color:#f59e0b">{pending_t}</div>
                <div class="kpi-sub">To do</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-accent" style="background:#8b5cf6"></div>
                <div class="kpi-icon" style="background:#f5f3ff">🕐</div>
                <div class="kpi-label">Hours This Month</div>
                <div class="kpi-value" style="color:#8b5cf6">{hours_month:.0f}h</div>
                <div class="kpi-sub">{calendar.month_abbr[today.month]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="content-area">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Recent Tasks</div>', unsafe_allow_html=True)
        if not my_tasks.empty:
            for _, t in my_tasks.head(6).iterrows():
                sc   = STATUS_COLORS.get(t["status"], "#94a3b8")
                pr_c = {"High":"#ef4444","Medium":"#f59e0b","Low":"#10b981"}.get(t["priority"],"#94a3b8")
                st.markdown(f"""
                <div class="task-row" style="border-left:3px solid {sc}">
                    <div class="priority-dot" style="background:{pr_c}"></div>
                    <div style="flex:1">
                        <div style='font-size:13px;font-weight:500;color:#101828'>{t['title']}</div>
                        <div style='font-size:11px;color:#98a2b3;margin-top:2px'>{t['hours']}h · <span style='color:{pr_c}'>{t['priority']}</span></div>
                    </div>
                    <span class="status-pill" style="background:{sc}1a;color:{sc};border:1px solid {sc}44">{t['status']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No tasks assigned yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── EMPLOYEE — WORK CALENDAR ────────────────────────────
    elif "Calendar" in page:
        st.markdown("""
        <div class="page-header">
            <div>
                <div class="page-title">Work Calendar</div>
                <div class="page-subtitle">Log your working hours and review monthly history</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
        today = date.today()

        col_cal, col_log = st.columns([2, 1], gap="large")

        with col_cal:
            st.markdown('<div style="padding-left:32px">', unsafe_allow_html=True)

            m_col, y_col = st.columns(2)
            with m_col:
                sel_month = st.selectbox("Month", list(range(1,13)),
                    index=today.month-1, format_func=lambda m: calendar.month_name[m])
            with y_col:
                sel_year = st.selectbox("Year", list(range(today.year-2, today.year+2)), index=2)

            logs = load_work_logs(emp_id, sel_month, sel_year)
            log_by_date = {}
            if not logs.empty:
                for _, row in logs.iterrows():
                    d = str(row["log_date"])
                    log_by_date.setdefault(d, []).append(row)

            cal_data = calendar.monthcalendar(sel_year, sel_month)
            dow_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

            # Calendar HTML
            cal_html = '<div class="cal-wrap">'
            cal_html += f'<div class="cal-header"><div class="cal-title">{calendar.month_name[sel_month]} {sel_year}</div></div>'
            cal_html += '<div class="cal-grid">'
            for d in dow_names:
                cal_html += f'<div class="cal-dow">{d}</div>'
            for week in cal_data:
                for dn in week:
                    if dn == 0:
                        cal_html += '<div class="cal-day empty"></div>'; continue
                    d_str = f"{sel_year}-{sel_month:02d}-{dn:02d}"
                    is_today = (dn == today.day and sel_month == today.month and sel_year == today.year)
                    has_log  = d_str in log_by_date
                    cls = "cal-day" + (" today" if is_today else "") + (" logged" if has_log else "")
                    inner = f'<div class="cal-daynum">{dn}</div>'
                    if has_log:
                        for entry in log_by_date[d_str]:
                            inner += f'<div class="cal-pill">{entry["hours_worked"]:.1f}h</div>'
                    cal_html += f'<div class="{cls}">{inner}</div>'
            cal_html += '</div></div>'
            st.markdown(cal_html, unsafe_allow_html=True)

            # Monthly stats
            if not logs.empty:
                total_m = logs["hours_worked"].sum()
                days_w  = logs["log_date"].nunique()
                avg_d   = total_m / days_w if days_w else 0
                st.markdown(f"""
                <div style='display:flex;gap:10px;margin-top:12px'>
                    <div style='flex:1;background:#eef2ff;border:1px solid #c7d2fe;border-radius:12px;padding:12px;text-align:center'>
                        <div style='font-size:11px;color:#6366f1;font-weight:500'>Days Worked</div>
                        <div style='font-size:22px;font-weight:700;color:#4f46e5;font-family:"JetBrains Mono",monospace'>{days_w}</div>
                    </div>
                    <div style='flex:1;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;padding:12px;text-align:center'>
                        <div style='font-size:11px;color:#16a34a;font-weight:500'>Total Hours</div>
                        <div style='font-size:22px;font-weight:700;color:#16a34a;font-family:"JetBrains Mono",monospace'>{total_m:.1f}h</div>
                    </div>
                    <div style='flex:1;background:#fffbeb;border:1px solid #fde68a;border-radius:12px;padding:12px;text-align:center'>
                        <div style='font-size:11px;color:#d97706;font-weight:500'>Avg / Day</div>
                        <div style='font-size:22px;font-weight:700;color:#d97706;font-family:"JetBrains Mono",monospace'>{avg_d:.1f}h</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        with col_log:
            st.markdown('<div style="padding-right:32px">', unsafe_allow_html=True)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Log Working Hours</div>', unsafe_allow_html=True)

            with st.form("work_log_form", clear_on_submit=True):
                log_date   = st.date_input("Date", value=today)
                c1, c2 = st.columns(2)
                with c1:
                    start_time = st.time_input("Start", value=datetime.strptime("09:00","%H:%M").time())
                with c2:
                    end_time   = st.time_input("End",   value=datetime.strptime("17:00","%H:%M").time())
                note = st.text_area("Notes (optional)", placeholder="What did you work on?", height=80)
                sub  = st.form_submit_button("Log Hours", use_container_width=True)
                if sub:
                    dt_s = datetime.combine(log_date, start_time)
                    dt_e = datetime.combine(log_date, end_time)
                    if dt_e <= dt_s:
                        st.error("End time must be after start time.")
                    else:
                        hrs = (dt_e - dt_s).seconds / 3600
                        add_work_log(emp_id, str(log_date), start_time.strftime("%H:%M"), end_time.strftime("%H:%M"), hrs, note)
                        load_work_logs.clear()
                        st.success(f"✓ {hrs:.1f}h logged for {log_date.strftime('%d %b %Y')}")
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

            # Logged entries list
            st.markdown('<div class="card-title" style="margin-top:12px">Logged Entries</div>', unsafe_allow_html=True)
            logs = load_work_logs(emp_id, sel_month, sel_year)
            if not logs.empty:
                for _, row in logs.sort_values("log_date", ascending=False).iterrows():
                    d_obj  = datetime.strptime(str(row["log_date"]), "%Y-%m-%d")
                    d_disp = d_obj.strftime("%d %b %Y")
                    col_entry, col_del = st.columns([5, 0.7])
                    with col_entry:
                        st.markdown(f"""
                        <div style='background:#f9fafb;border:1px solid #e4e7ec;border-radius:10px;
                                    padding:10px 14px;margin-bottom:6px'>
                            <div style='font-size:13px;font-weight:500;color:#101828'>{d_disp}</div>
                            <div style='font-size:11px;color:#98a2b3;margin-top:2px'>
                                🕐 {row['start_time']} – {row['end_time']} ·
                                <span style='color:#6366f1;font-weight:600;font-family:"JetBrains Mono",monospace'>{row['hours_worked']:.1f}h</span>
                            </div>
                            {f'<div style="font-size:11px;color:#64748b;margin-top:3px">{row["note"]}</div>' if row['note'] else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    with col_del:
                        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
                        if st.button("🗑", key=f"del_log_{row['id']}"):
                            delete_work_log(int(row["id"]))
                            load_work_logs.clear(); st.rerun()
            else:
                st.info("No entries for this month.")

            st.markdown('</div>', unsafe_allow_html=True)

    # ─── EMPLOYEE — MY TASKS ────────────────────────────────
    elif "Tasks" in page:
        st.markdown("""
        <div class="page-header">
            <div>
                <div class="page-title">My Tasks</div>
                <div class="page-subtitle">View and update your assigned tasks</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="content-area">', unsafe_allow_html=True)
        my_tasks = load_tasks(emp_id)

        if my_tasks.empty:
            st.info("No tasks assigned yet. Your coordinator will add tasks here.")
        else:
            status_filter = st.radio(
                "Filter", ["All","Pending","In Progress","Completed"],
                horizontal=True, label_visibility="collapsed"
            )
            filtered = my_tasks if status_filter == "All" else my_tasks[my_tasks["status"] == status_filter]

            if filtered.empty:
                st.info(f"No {status_filter.lower()} tasks.")
            else:
                for _, t in filtered.iterrows():
                    sc   = STATUS_COLORS.get(t["status"], "#94a3b8")
                    pr_c = {"High":"#ef4444","Medium":"#f59e0b","Low":"#10b981"}.get(t["priority"],"#94a3b8")

                    col_info, col_update = st.columns([3.5, 1.5])
                    with col_info:
                        st.markdown(f"""
                        <div class="task-row" style="border-left:3px solid {sc}">
                            <div class="priority-dot" style="background:{pr_c}"></div>
                            <div style="flex:1">
                                <div style='font-size:13px;font-weight:600;color:#101828'>{t['title']}</div>
                                <div style='font-size:11px;color:#98a2b3;margin-top:3px'>
                                    <span style='color:{pr_c};font-weight:500'>{t['priority']}</span> · {t['hours']}h · Added {str(t['created_at'])[:10]}
                                </div>
                            </div>
                            <span class="status-pill" style="background:{sc}1a;color:{sc};border:1px solid {sc}44">{t['status']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_update:
                        new_status = st.selectbox(
                            "Status",
                            ["Pending","In Progress","Completed"],
                            index=["Pending","In Progress","Completed"].index(t["status"]),
                            key=f"emp_task_{t['id']}",
                            label_visibility="collapsed"
                        )
                        if st.button("Update", key=f"upd_{t['id']}", use_container_width=True):
                            update_task_status(int(t["id"]), new_status)
                            load_tasks.clear(); st.success("✓ Updated."); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)