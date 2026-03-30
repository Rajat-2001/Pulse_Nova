import streamlit as st
from components.theme import apply_theme

apply_theme()

st.markdown(
    """
    <div class="pulse-title">
        Hey, I'm PulseNova 👋
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="pulse-subtitle">
    Your personal AI assistant — chat, email, calendar & more
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.write("")

# Chat input
prompt = st.chat_input("Ask PulseNova anything...")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        st.write("PulseNova is thinking...")

st.write("")
st.write("")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="pulse-card">
    📧 <b>Email</b><br>
    Read, summarize & send emails
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="pulse-card">
    📅 <b>Calendar</b><br>
    Manage your Google Calendar
    </div>
    """, unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    <div class="pulse-card">
    🧠 <b>Knowledge</b><br>
    Upload PDFs & query with RAG
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="pulse-card">
    🎙️ <b>Voice</b><br>
    Speak commands, hear responses
    </div>
    """, unsafe_allow_html=True)