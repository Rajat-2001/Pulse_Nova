import streamlit as st
import sys, os
from components.theme import apply_theme

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="PulseNova",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_theme()

# ----------------------------
# HERO
# ----------------------------

st.markdown("""
<div style="text-align:center; padding-top:40px;">
    <div class="pulse-title">
        ⚡ PulseNova
    </div>
    <div class="pulse-subtitle">
        Your personal AI assistant — chat, email, calendar & more
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
st.write("")

# ----------------------------
# FEATURES GRID
# ----------------------------

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div class="pulse-card">
    💬 <b>Smart Chat</b><br>
    Text and voice commands via LLaMA 3.1 8B
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class="pulse-card">
    🧠 <b>Knowledge RAG</b><br>
    Upload PDFs and query with AI
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="pulse-card">
    📧 <b>Email AI</b><br>
    Read, summarize and send emails
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class="pulse-card">
    🎙️ <b>Voice I/O</b><br>
    Speak commands, hear responses
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="pulse-card">
    📅 <b>Calendar</b><br>
    Manage Google Calendar naturally
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class="pulse-card">
    🤖 <b>Discord Bot</b><br>
    Access PulseNova from anywhere
    </div>
    """, unsafe_allow_html=True)

# ----------------------------
# CTA BUTTON
# ----------------------------

st.write("")
st.write("")
st.write("")

col1, col2, col3 = st.columns([1,1,1])

with col2:
    if st.button("Enter PulseNova →", use_container_width=True):
        st.switch_page("pages/1_Chat.py")

# ----------------------------
# STATUS
# ----------------------------

st.write("")
st.markdown("""
<div style="
text-align:center;
opacity:0.5;
font-size:13px;
padding-top:10px;
">
● LLaMA 3.1 8B Online — Running Locally
</div>
""", unsafe_allow_html=True)