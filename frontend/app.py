import streamlit as st
from utils import generate_starters_api, factcheck_api, get_history_api, send_feedback_api

st.set_page_config(
    page_title="NexConnect · Networking Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ══ FORCE DARK BASE — fix black-on-black ══ */
html, body { background: #0A0714 !important; color: #E2E8F0 !important; }
.stApp { background: #0A0714 !important; }
[data-testid="stAppViewContainer"] { background: #0A0714 !important; }
[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1180px !important; }

/* Force ALL text to be visible */
p, span, div, label, h1, h2, h3, h4, h5, li, td, th {
    color: #E2E8F0 !important;
}

/* ══ KEYFRAME ANIMATIONS ══ */
@keyframes floatUp {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}
@keyframes pulseGlow {
    0%, 100% { opacity: 0.5; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.15); }
}
@keyframes shimmer {
    0% { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes rotateSlow {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.2; }
}
@keyframes borderPulse {
    0%, 100% { border-color: rgba(124,58,237,0.3); }
    50% { border-color: rgba(168,85,247,0.7); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-16px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes countUp {
    from { opacity: 0; transform: scale(0.8); }
    to { opacity: 1; transform: scale(1); }
}

/* ══ AMBIENT ORBS ══ */
.orb-container {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; z-index: 0; overflow: hidden;
}
.orb {
    position: absolute; border-radius: 50%;
    filter: blur(80px); opacity: 0.35;
}
.orb-1 {
    width: 500px; height: 500px;
    background: radial-gradient(circle, #4C1D95, transparent 70%);
    top: -150px; right: -100px;
    animation: floatUp 8s ease-in-out infinite;
}
.orb-2 {
    width: 350px; height: 350px;
    background: radial-gradient(circle, #1E3A8A, transparent 70%);
    bottom: -80px; left: -80px;
    animation: floatUp 10s ease-in-out infinite reverse;
}
.orb-3 {
    width: 250px; height: 250px;
    background: radial-gradient(circle, #6D28D9, transparent 70%);
    top: 40%; left: 40%;
    animation: floatUp 12s ease-in-out infinite 2s;
}

/* ══ HERO ══ */
.hero {
    position: relative; padding: 2.8rem 2.5rem 2.2rem;
    border-radius: 24px; margin-bottom: 1.75rem; overflow: hidden;
    background: linear-gradient(135deg, rgba(76,29,149,0.2) 0%, rgba(15,10,30,0.6) 50%, rgba(30,58,138,0.15) 100%);
    border: 1px solid rgba(124,58,237,0.3);
    animation: fadeInUp 0.6s ease both;
}
.hero::before {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(124,58,237,0.08), transparent 60%);
    pointer-events: none;
}
.hero-top-line {
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #7C3AED, #A855F7, #EC4899, transparent);
    animation: shimmer 3s linear infinite;
    background-size: 400px 100%;
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(124,58,237,0.15); border: 1px solid rgba(124,58,237,0.4);
    border-radius: 100px; padding: 5px 14px;
    font-size: 11px !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    color: #C4B5FD !important; margin-bottom: 1rem;
    animation: borderPulse 3s ease-in-out infinite;
}
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #10B981; display: inline-block;
    animation: pulseGlow 1.4s ease-in-out infinite;
    box-shadow: 0 0 8px #10B981;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 3.2rem !important; font-weight: 700 !important;
    letter-spacing: -0.04em !important; line-height: 1 !important;
    background: linear-gradient(135deg, #ffffff 0%, #C4B5FD 40%, #A855F7 75%, #EC4899 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important; margin: 0 0 0.6rem !important;
    animation: fadeInUp 0.7s ease 0.1s both;
}
.hero-sub {
    font-size: 1rem !important; color: #94A3B8 !important;
    max-width: 520px; line-height: 1.65; margin: 0;
    animation: fadeInUp 0.7s ease 0.2s both;
}
.hero-stats {
    display: flex; gap: 3rem; margin-top: 2rem; padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.07);
    animation: fadeInUp 0.7s ease 0.3s both;
}
.hero-stat-val {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.9rem !important; font-weight: 700 !important;
    color: #C4B5FD !important; line-height: 1 !important;
    animation: countUp 0.5s ease 0.5s both;
}
.hero-stat-val em { font-size: 1rem !important; color: #7C3AED !important; font-style: normal !important; }
.hero-stat-lbl {
    font-size: 10px !important; color: #475569 !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.08em !important; margin-top: 4px !important;
}

/* ══ FLOATING PARTICLES ══ */
.particles { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
.particle {
    position: absolute; width: 2px; height: 2px;
    background: rgba(168,85,247,0.6); border-radius: 50%;
    animation: floatUp var(--dur, 6s) ease-in-out infinite var(--delay, 0s);
}

/* ══ TABS ══ */
[data-testid="stTabs"] [role="tablist"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important; padding: 5px !important; gap: 4px !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important; font-weight: 600 !important;
    color: #475569 !important; border-radius: 10px !important;
    padding: 10px 20px !important; border: 1px solid transparent !important;
    background: transparent !important; transition: all 0.25s !important;
}
[data-testid="stTabs"] [role="tab"]:hover { color: #94A3B8 !important; background: rgba(255,255,255,0.04) !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #C4B5FD !important;
    background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(168,85,247,0.12)) !important;
    border-color: rgba(124,58,237,0.45) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }
[data-testid="stTabs"] [role="tabpanel"] { padding-top: 1.5rem !important; }

/* ══ GLASS PANELS ══ */
.glass-panel {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 1.75rem;
    position: relative; overflow: hidden;
    animation: fadeInUp 0.5s ease both;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.glass-panel:hover {
    border-color: rgba(124,58,237,0.3);
    box-shadow: 0 0 40px rgba(124,58,237,0.08);
}
.glass-panel::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124,58,237,0.5), rgba(168,85,247,0.3), transparent);
}
.panel-glow {
    position: absolute; top: -80px; right: -80px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(124,58,237,0.15), transparent 70%);
    pointer-events: none; animation: floatUp 6s ease-in-out infinite;
}
.panel-label {
    font-size: 10.5px !important; font-weight: 800 !important;
    text-transform: uppercase !important; letter-spacing: 0.12em !important;
    color: #475569 !important; display: flex; align-items: center; gap: 8px;
    margin-bottom: 1.3rem;
}
.panel-bar {
    width: 3px; height: 14px; border-radius: 2px; display: inline-block;
    background: linear-gradient(180deg, #7C3AED, #A855F7);
}

/* ══ INPUTS — FORCE VISIBLE ══ */
[data-testid="stTextArea"] textarea {
    background: rgba(15,10,30,0.7) !important;
    border: 1px solid rgba(124,58,237,0.25) !important;
    border-radius: 12px !important;
    color: #F1F5F9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important; line-height: 1.6 !important;
    padding: 12px 14px !important;
    transition: all 0.25s !important;
    caret-color: #A855F7 !important;
}
[data-testid="stTextInput"] input {
    background: rgba(15,10,30,0.7) !important;
    border: 1px solid rgba(124,58,237,0.25) !important;
    border-radius: 12px !important;
    color: #F1F5F9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    padding: 10px 14px !important;
    transition: all 0.25s !important;
    caret-color: #A855F7 !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: rgba(124,58,237,0.7) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15), 0 0 20px rgba(124,58,237,0.1) !important;
    outline: none !important;
}
[data-testid="stTextArea"] textarea::placeholder,
[data-testid="stTextInput"] input::placeholder {
    color: #334155 !important; font-style: italic !important;
}
label[data-testid="stWidgetLabel"] p {
    font-size: 11px !important; font-weight: 700 !important;
    color: #7C3AED !important; text-transform: uppercase !important;
    letter-spacing: 0.1em !important; margin-bottom: 6px !important;
}

/* ══ BUTTONS ══ */
[data-testid="stButton"] > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important; font-weight: 600 !important;
    border-radius: 12px !important; padding: 10px 18px !important;
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #94A3B8 !important;
    transition: all 0.2s !important;
}
[data-testid="stButton"] > button:hover {
    border-color: rgba(124,58,237,0.5) !important;
    color: #C4B5FD !important; background: rgba(124,58,237,0.1) !important;
    transform: translateY(-1px) !important;
}
/* Primary */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #5B21B6, #7C3AED, #9333EA) !important;
    border: none !important; color: #ffffff !important;
    box-shadow: 0 4px 24px rgba(124,58,237,0.4) !important;
    font-size: 14px !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 8px 36px rgba(124,58,237,0.6) !important;
    transform: translateY(-2px) !important;
    background: linear-gradient(135deg, #4C1D95, #6D28D9, #7C3AED) !important;
}

/* ══ STARTER CARDS ══ */
.starter-card {
    background: rgba(15,10,30,0.6);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 16px 18px 16px 22px;
    margin-bottom: 10px; position: relative; overflow: hidden;
    transition: all 0.25s ease; cursor: default;
    animation: slideInLeft 0.4s ease both;
}
.starter-card:nth-child(1) { animation-delay: 0.05s; }
.starter-card:nth-child(2) { animation-delay: 0.1s; }
.starter-card:nth-child(3) { animation-delay: 0.15s; }
.starter-card:nth-child(4) { animation-delay: 0.2s; }
.starter-card:nth-child(5) { animation-delay: 0.25s; }
.starter-card::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0;
    width: 3px; border-radius: 3px 0 0 3px;
}
.starter-card::after {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(124,58,237,0.04), transparent 60%);
    opacity: 0; transition: opacity 0.25s;
}
.starter-card:hover { border-color: rgba(124,58,237,0.35); transform: translateX(5px); }
.starter-card:hover::after { opacity: 1; }
.sc1::before { background: linear-gradient(180deg,#7C3AED,#6D28D9); }
.sc2::before { background: linear-gradient(180deg,#A855F7,#9333EA); }
.sc3::before { background: linear-gradient(180deg,#EC4899,#BE185D); }
.sc4::before { background: linear-gradient(180deg,#06B6D4,#0E7490); }
.sc5::before { background: linear-gradient(180deg,#10B981,#059669); }
.starter-num {
    font-size: 10px !important; font-weight: 800 !important;
    text-transform: uppercase !important; letter-spacing: 0.15em !important;
    color: #6D28D9 !important; margin-bottom: 6px !important;
}
.starter-body {
    font-size: 13.5px !important; color: #CBD5E1 !important;
    line-height: 1.7 !important; font-style: italic !important; margin: 0 !important;
}

/* ══ BADGES & CHIPS ══ */
.topic-wrap { display: flex; flex-wrap: wrap; gap: 7px; margin: 0.5rem 0 1rem; }
.topic-badge {
    background: rgba(88,28,135,0.2); border: 1px solid rgba(168,85,247,0.3);
    color: #C4B5FD !important; border-radius: 100px;
    padding: 4px 12px; font-size: 11.5px !important; font-weight: 600 !important;
    display: inline-flex; align-items: center; gap: 6px;
    transition: all 0.2s;
}
.topic-badge:hover { background: rgba(88,28,135,0.35); border-color: rgba(168,85,247,0.6); }
.topic-badge::before { content: '◆'; font-size: 8px !important; color: #7C3AED !important; }
.interest-badge {
    background: rgba(51,65,85,0.3); border: 1px solid rgba(100,116,139,0.25);
    color: #94A3B8 !important; border-radius: 100px;
    padding: 3px 10px; font-size: 11px !important; font-weight: 500 !important;
}
.count-chip {
    background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3);
    color: #34D399 !important; border-radius: 100px;
    padding: 4px 12px; font-size: 11.5px !important; font-weight: 700 !important;
    animation: pulseGlow 2s ease-in-out infinite;
}
.results-meta { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }

/* ══ EMPTY STATE ══ */
.empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 4rem 2rem;
    background: rgba(15,10,30,0.4);
    border: 1px dashed rgba(124,58,237,0.2);
    border-radius: 16px; text-align: center;
    animation: fadeInUp 0.5s ease both;
}
.empty-icon { font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.4; animation: floatUp 4s ease-in-out infinite; }
.empty-text { font-size: 13.5px !important; color: #475569 !important; line-height: 1.65; max-width: 280px; }
.empty-text strong { color: #6D28D9 !important; }

/* ══ FEEDBACK BUTTONS ══ */
.fb-useful [data-testid="stButton"] > button {
    background: rgba(16,185,129,0.08) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    color: #34D399 !important;
}
.fb-useful [data-testid="stButton"] > button:hover {
    background: rgba(16,185,129,0.18) !important; border-color: rgba(16,185,129,0.5) !important;
}
.fb-no [data-testid="stButton"] > button {
    background: rgba(239,68,68,0.07) !important;
    border: 1px solid rgba(239,68,68,0.25) !important;
    color: #F87171 !important;
}
.fb-no [data-testid="stButton"] > button:hover {
    background: rgba(239,68,68,0.15) !important;
}

/* ══ STATUS PILLS ══ */
.pill-useful {
    background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3);
    color: #34D399 !important; border-radius: 100px; padding: 4px 12px;
    font-size: 11px !important; font-weight: 700 !important;
    display: inline-block;
}
.pill-no {
    background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.25);
    color: #F87171 !important; border-radius: 100px; padding: 4px 12px;
    font-size: 11px !important; font-weight: 700 !important;
    display: inline-block;
}
.pill-pending {
    background: rgba(100,116,139,0.12); border: 1px solid rgba(100,116,139,0.22);
    color: #64748B !important; border-radius: 100px; padding: 4px 12px;
    font-size: 11px !important; font-weight: 700 !important;
    display: inline-block;
}

/* ══ FACT CARD ══ */
.fact-wrapper {
    background: rgba(15,10,30,0.5); border: 1px solid rgba(124,58,237,0.25);
    border-radius: 16px; overflow: hidden; margin-top: 1.5rem;
    animation: fadeInUp 0.4s ease both;
    box-shadow: 0 0 40px rgba(124,58,237,0.08);
}
.fact-head {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 20px;
    background: rgba(124,58,237,0.1);
    border-bottom: 1px solid rgba(124,58,237,0.15);
}
.fact-head-title { font-size: 14px !important; font-weight: 600 !important; color: #E2E8F0 !important; flex: 1; margin: 0; }
.verified-chip {
    background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3);
    color: #34D399 !important; border-radius: 100px; padding: 4px 12px;
    font-size: 11px !important; font-weight: 700 !important;
}
.fact-body-text {
    padding: 18px 20px; font-size: 13.5px !important;
    color: #94A3B8 !important; line-height: 1.85 !important; white-space: pre-line;
}

/* ══ HISTORY CARDS ══ */
.hist-card {
    background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px; overflow: hidden; margin-bottom: 1.1rem;
    transition: all 0.25s; animation: fadeInUp 0.5s ease both;
}
.hist-card:hover { border-color: rgba(124,58,237,0.3); box-shadow: 0 4px 30px rgba(124,58,237,0.08); }
.hist-head {
    display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
    padding: 14px 20px;
    background: rgba(255,255,255,0.02);
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.hist-event { font-size: 14px !important; font-weight: 600 !important; color: #E2E8F0 !important; margin-bottom: 3px; }
.hist-ts { font-size: 11px !important; color: #334155 !important; }
.hist-body { padding: 14px 20px; }
.hist-label { font-size: 10px !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; color: #334155 !important; margin-bottom: 8px; }
.hist-quote { font-size: 12.5px !important; color: #475569 !important; font-style: italic; margin-top: 8px; }

/* ══ EXPANDER ══ */
[data-testid="stExpander"] {
    background: rgba(15,10,30,0.4) !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: #475569 !important; font-size: 12.5px !important; font-weight: 500 !important; }
[data-testid="stExpander"] summary:hover { color: #94A3B8 !important; }
[data-testid="stExpander"] p { color: #64748B !important; font-size: 13px !important; }

/* ══ ALERTS ══ */
[data-testid="stAlert"] {
    background: rgba(124,58,237,0.08) !important;
    border: 1px solid rgba(124,58,237,0.22) !important;
    border-radius: 12px !important;
}
[data-testid="stAlert"] p { color: #A78BFA !important; font-size: 13px !important; }

/* ══ SPINNER ══ */
[data-testid="stSpinner"] p { color: #7C3AED !important; font-size: 13px !important; }

/* ══ HORIZONTAL BLOCK ══ */
[data-testid="stHorizontalBlock"] { gap: 1.25rem !important; }

/* ══ CAPTIONS ══ */
[data-testid="stCaptionContainer"] p { color: #334155 !important; font-size: 11px !important; }

/* ══ SEARCH PANEL ══ */
.fact-search-panel {
    background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 1.75rem; position: relative; overflow: hidden;
    animation: fadeInUp 0.5s ease both;
}
.fact-search-panel::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124,58,237,0.5), rgba(168,85,247,0.3), transparent);
}
.fact-hint { font-size: 13.5px !important; color: #64748B !important; line-height: 1.7 !important; margin-bottom: 1.25rem; }

/* ══ DIVIDER ══ */
hr, [data-testid="stDivider"] { border-color: rgba(255,255,255,0.06) !important; margin: 1.2rem 0 !important; }

/* ══ SCROLLBAR ══ */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 3px; }

/* ══ SECTION DIVIDER ══ */
.section-divider {
    height: 1px; background: linear-gradient(90deg, transparent, rgba(124,58,237,0.3), transparent);
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Ambient orbs (rendered once) ──
st.markdown("""
<div class="orb-container">
  <div class="orb orb-1"></div>
  <div class="orb orb-2"></div>
  <div class="orb orb-3"></div>
</div>
""", unsafe_allow_html=True)

ACCENT_CLASSES = ["sc1", "sc2", "sc3", "sc4", "sc5"]

def render_topics(topics):
    badges = "".join(f'<span class="topic-badge">{t}</span>' for t in topics)
    return f'<div class="topic-wrap">{badges}</div>'

def render_interests(interests):
    badges = "".join(f'<span class="interest-badge">{i}</span>' for i in interests)
    return f'<div class="topic-wrap">{badges}</div>'

def render_starters(suggestions):
    html = ""
    for idx, s in enumerate(suggestions):
        cls = ACCENT_CLASSES[idx % len(ACCENT_CLASSES)]
        html += f"""
        <div class="starter-card {cls}">
            <div class="starter-num">✦ Starter 0{idx+1}</div>
            <p class="starter-body">"{s}"</p>
        </div>"""
    return html

# ══ HERO ══
st.markdown("""
<div class="hero">
  <div class="hero-top-line"></div>
  <div class="particles">
    <div class="particle" style="left:10%;top:20%;--dur:7s;--delay:0s"></div>
    <div class="particle" style="left:30%;top:60%;--dur:9s;--delay:1s"></div>
    <div class="particle" style="left:60%;top:30%;--dur:6s;--delay:2s"></div>
    <div class="particle" style="left:80%;top:70%;--dur:8s;--delay:0.5s"></div>
    <div class="particle" style="left:50%;top:10%;--dur:11s;--delay:3s"></div>
  </div>
  <div style="position:relative;z-index:1">
    <div class="hero-eyebrow">
      <span class="live-dot"></span>
      AI-Powered &nbsp;·&nbsp; Wikipedia-Verified
    </div>
    <h1 class="hero-title">NexConnect</h1>
    <p class="hero-sub">Craft conversations that open doors. Smart starters tailored to your event, backed by real-time fact verification.</p>
    <div class="hero-stats">
      <div>
        <div class="hero-stat-val">3×<em>+</em></div>
        <div class="hero-stat-lbl">Engagement Boost</div>
      </div>
      <div>
        <div class="hero-stat-val">AI<em> ✦</em></div>
        <div class="hero-stat-lbl">Personalized</div>
      </div>
      <div>
        <div class="hero-stat-val">Wiki<em> ⬡</em></div>
        <div class="hero-stat-lbl">Fact-Backed</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["✦  Smart Starters", "⬡  Fact Verify", "◎  History"])

# ══ TAB 1 ══
with tab1:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("""
        <div class="glass-panel">
          <div class="panel-glow"></div>
          <div class="panel-label"><span class="panel-bar"></span>Your Details</div>
        </div>""", unsafe_allow_html=True)

        event_desc = st.text_area(
            "EVENT DESCRIPTION",
            placeholder="e.g., AI for Sustainable Cities — ML in urban transit and environmental management...",
            height=140
        )
        interests_input = st.text_input(
            "YOUR INTERESTS  (comma-separated)",
            placeholder="climate change, urban planning, machine learning"
        )
        generate_btn = st.button("✦  Generate Conversation Starters", use_container_width=True, type="primary")

    with right:
        if generate_btn:
            if not event_desc.strip():
                st.warning("Please describe the event first.")
            elif not interests_input.strip():
                st.warning("Add at least one interest to personalize results.")
            else:
                interests_list = [i.strip() for i in interests_input.split(",") if i.strip()]
                with st.spinner("Analyzing themes and crafting starters…"):
                    result = generate_starters_api(event_desc, interests_list)
                if result:
                    st.session_state.current_generation = result
                    st.session_state.feedback_submitted = None
                else:
                    st.error("Backend unreachable — ensure the server is running.")

        if "current_generation" in st.session_state:
            result = st.session_state.current_generation
            count = len(result["suggestions"])
            st.markdown(f"""
            <div class="results-meta">
              <div class="panel-label" style="margin:0"><span class="panel-bar"></span>Generated Starters</div>
              <span class="count-chip">{count} ready</span>
            </div>
            {render_topics(result["topics"])}
            <div class="section-divider"></div>
            {render_starters(result["suggestions"])}
            """, unsafe_allow_html=True)

            db_id = result.get("id")
            if db_id:
                st.markdown("<br>", unsafe_allow_html=True)
                fb_l, fb_r, _ = st.columns([1, 1, 2])
                with fb_l:
                    st.markdown('<div class="fb-useful">', unsafe_allow_html=True)
                    if st.button("👍  Useful", key=f"up_{db_id}", use_container_width=True):
                        if send_feedback_api(db_id, True):
                            st.success("Marked as useful!")
                    st.markdown('</div>', unsafe_allow_html=True)
                with fb_r:
                    st.markdown('<div class="fb-no">', unsafe_allow_html=True)
                    if st.button("👎  Not quite", key=f"dn_{db_id}", use_container_width=True):
                        if send_feedback_api(db_id, False):
                            st.info("Feedback logged.")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
              <div class="empty-icon">✦</div>
              <p class="empty-text">Fill in your <strong>event</strong> and <strong>interests</strong>, then hit <strong>Generate</strong> to see tailored starters.</p>
            </div>
            """, unsafe_allow_html=True)

# ══ TAB 2 ══
with tab2:
    st.markdown("""
    <div class="fact-search-panel">
      <div class="panel-label"><span class="panel-bar"></span>Verify a Concept</div>
      <p class="fact-hint">
        Heading into a conversation and want to sound sharp?
        Enter any term below — we'll pull a Wikipedia-backed summary instantly.
      </p>
    </div>
    """, unsafe_allow_html=True)

    fc1, fc2 = st.columns([3, 1])
    with fc1:
        fact_query = st.text_input(
            "TERM OR CONCEPT",
            placeholder="e.g., zero-shot learning, blockchain, microgrids...",
            key="factcheck_input"
        )
    with fc2:
        st.markdown("<br>", unsafe_allow_html=True)
        verify_btn = st.button("⬡  Verify", use_container_width=True, type="primary")

    if verify_btn:
        if not fact_query.strip():
            st.warning("Enter a concept to verify.")
        else:
            with st.spinner(f'Querying Wikipedia for "{fact_query}"…'):
                fact_result = factcheck_api(fact_query)
            if fact_result:
                st.markdown(f"""
                <div class="fact-wrapper">
                  <div class="fact-head">
                    <span style="font-size:18px">📌</span>
                    <p class="fact-head-title">{fact_query}</p>
                    <span class="verified-chip">✓ Verified</span>
                  </div>
                  <div class="fact-body-text">{fact_result['summary']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Verification failed — check that the backend server is running.")

# ══ TAB 3 ══
with tab3:
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("""
        <div class="panel-label" style="margin-bottom:0.4rem">
          <span class="panel-bar"></span>Networking Strategy History
        </div>
        <p style="font-size:13px;color:#334155;margin-bottom:1.5rem">All past starter sets — review, rate, and reflect.</p>
        """, unsafe_allow_html=True)
    with h2:
        if st.button("↻  Refresh", use_container_width=True):
            st.rerun()

    history = get_history_api()

    if not history:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">◎</div>
          <p class="empty-text">No history yet. Generate your first set of starters in the <strong>Smart Starters</strong> tab.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for item in history:
            fb = item["feedback"]
            pill = (
                '<span class="pill-useful">👍 Useful</span>' if fb is True else
                '<span class="pill-no">👎 Not Useful</span>' if fb is False else
                '<span class="pill-pending">⏳ Unrated</span>'
            )
            desc_short = item['description'][:90] + ("…" if len(item['description']) > 90 else "")
            first_q = f'"{item["suggestions"][0]}"' if item["suggestions"] else ""

            st.markdown(f"""
            <div class="hist-card">
              <div class="hist-head">
                <div>
                  <div class="hist-event">{desc_short}</div>
                  <div class="hist-ts">{item['created_at']}</div>
                </div>
                {pill}
              </div>
              <div class="hist-body">
                <div class="hist-label">Interests</div>
                {render_interests(item["interests"])}
                <div class="hist-label" style="margin-top:10px">Themes</div>
                {render_topics(item["topics"])}
                <div class="hist-quote">{first_q}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("View all conversation starters"):
                for s in item["suggestions"]:
                    st.markdown(
                        f'<p style="font-size:13px;color:#475569;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-style:italic;margin:0">"{s}"</p>',
                        unsafe_allow_html=True
                    )

            if fb is not True or fb is not False:
                bc1, bc2, _ = st.columns([1, 1, 3])
                with bc1:
                    if fb is not True:
                        st.markdown('<div class="fb-useful">', unsafe_allow_html=True)
                        if st.button("👍 Useful", key=f"hist_up_{item['id']}", use_container_width=True):
                            send_feedback_api(item["id"], True); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                with bc2:
                    if fb is not False:
                        st.markdown('<div class="fb-no">', unsafe_allow_html=True)
                        if st.button("👎 Not Useful", key=f"hist_dn_{item['id']}", use_container_width=True):
                            send_feedback_api(item["id"], False); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)