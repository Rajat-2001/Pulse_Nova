import streamlit as st
from components.theme import apply_theme

apply_theme()

st.markdown('<div class="pulse-title">Email</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pulse-subtitle">
Read, summarize and send emails
</div>
""", unsafe_allow_html=True)

st.write("")

st.markdown("""
<div class="pulse-card">
Email features coming soon...
</div>
""", unsafe_allow_html=True)