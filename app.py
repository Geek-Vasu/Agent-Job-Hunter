import sys
import asyncio

# 🔥 Fix Windows subprocess issue for browser_use
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import nest_asyncio
nest_asyncio.apply()

import streamlit as st
from pipeline import run_agent
import time

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Vision-Driven Job Hunter",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# ==========================================
# SESSION STATE
# ==========================================
if "result_data" not in st.session_state:
    st.session_state.result_data = None

if "loading" not in st.session_state:
    st.session_state.loading = False

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1d3f 50%, #0f1129 100%);
    background-attachment: fixed;
}

.block-container {
    padding-top: 2rem !important;
    max-width: 1100px !important;
}

.hero-container {
    text-align: center;
    padding: 3rem 0 2rem 0;
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
}

.stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: white !important;
}

.stButton button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.8rem 1.5rem !important;
}

.card {
    background: rgba(255,255,255,0.03);
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
    border: 1px solid rgba(255,255,255,0.08);
}

.section-header {
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #e2e8f0;
}

.priority-label {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 6px;
    display: inline-block;
}

.priority-high {
    background: rgba(239,68,68,0.15);
    color: #fca5a5;
}

.priority-medium {
    background: rgba(245,158,11,0.15);
    color: #fcd34d;
}

.priority-low {
    background: rgba(107,114,128,0.15);
    color: #9ca3af;
}

.email-card {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 1.5rem;
}

.email-subject {
    color: #667eea;
    font-weight: 600;
    margin-bottom: 1rem;
}

.summary-block {
    border-left: 4px solid #667eea;
    padding-left: 1rem;
    font-style: italic;
    color: #cbd5e1;
}

.match-card {
    background: rgba(102,126,234,0.08);
    border-radius: 14px;
    padding: 1.5rem;
}

.progress-bar {
    background: rgba(255,255,255,0.1);
    border-radius: 8px;
    height: 8px;
    overflow: hidden;
}

.progress-fill {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    height: 100%;
}

.link-button {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.6rem 1.2rem;
    background: rgba(102,126,234,0.2);
    border-radius: 8px;
    color: #667eea !important;
    text-decoration: none;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(102,126,234,0.5), transparent);
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HERO
# ==========================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🧠 Vision-Driven Job Hunter</div>
    <div class="hero-subtitle">Autonomous AI that finds and prepares applications for you</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# INPUT
# ==========================================
query = st.text_input(
    "",
    placeholder="e.g., Machine Learning Intern, Data Science Intern...",
    label_visibility="collapsed"
)

if st.button("🚀 Start Agent", use_container_width=True):

    if not query.strip():
        st.warning("Please enter a role.")
    else:
        st.session_state.loading = True
        with st.spinner("🔍 Agent is scouting internships..."):
            time.sleep(0.5)
            result = run_agent(query)
            st.session_state.result_data = result
        st.session_state.loading = False

# ==========================================
# RENDER RESULTS
# ==========================================
if st.session_state.result_data:

    result = st.session_state.result_data
    best = result["best_match"]
    package = result["tailored_package"]
    alternatives = result.get("alternatives", [])

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ==========================================
    # SKILL GAP
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🔥 Skill Gap Analysis</div>', unsafe_allow_html=True)

    priorities = package["skill_gap_analysis"]["priority_levels"]

    for level, label, css in [
        ("high", "🔴 High Priority", "priority-high"),
        ("medium", "🟡 Medium Priority", "priority-medium"),
        ("low", "⚪ Low Priority", "priority-low"),
    ]:
        st.markdown(f'<div class="priority-label {css}">{label}</div>', unsafe_allow_html=True)
        st.write(priorities[level])

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # COLD EMAIL
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">✉ Cold Email</div>', unsafe_allow_html=True)

    email_subject = package['cold_email']['subject']
    email_body = package['cold_email']['body']
    full_email = f"Subject: {email_subject}\n\n{email_body}"

    st.markdown(f"""
    <div class="email-card">
        <div class="email-subject">{email_subject}</div>
        <div>{email_body}</div>
    </div>
    """, unsafe_allow_html=True)

    # Real copy button
    st.code(full_email, language="text")

    if st.button("📋 Copy Email"):
     st.success("Email ready to copy above 👆")


    st.markdown('</div>', unsafe_allow_html=True)   

    # ==========================================
    # SUMMARY
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📝 Tailored Resume Summary</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-block">{package["tailored_summary"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # BEST MATCH
    # ==========================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🏆 Best Internship Match</div>', unsafe_allow_html=True)

    match_score = best.get("match_score", 90)

    st.markdown(f"""
    <div class="match-card">
        <h3>{best["title"]}</h3>
        <div style="color:#667eea;">@ {best["company"]}</div>
        <div style="margin-top:1rem;">Match Score: {match_score}%</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width:{match_score}%"></div>
        </div>
        <a href="{best["source_url"]}" target="_blank" class="link-button">
            🔗 View Internship →
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # ALTERNATIVES
    # ==========================================
    if alternatives:
        with st.expander("🔍 Alternative Opportunities"):
            for idx, alt in enumerate(alternatives, 1):
                st.markdown(f"""
                <div style="margin:0.5rem 0;">
                    <strong>{idx}. {alt["title"]}</strong><br/>
                    <span style="color:#94a3b8;">{alt["company"]}</span><br/>
                    <a href="{alt["source_url"]}" target="_blank" style="color:#667eea;">
                        View Details →
                    </a>
                </div>
                """, unsafe_allow_html=True)
