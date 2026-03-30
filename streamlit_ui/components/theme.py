import streamlit as st

def apply_theme():
    st.markdown("""
    <style>

    /* -----------------------------
       GLOBAL BACKGROUND
    ------------------------------*/

    .stApp {
        background-color: #0D0D0D;
    }

    .main .block-container {
        max-width: 920px;
        padding-top: 3rem;
        padding-bottom: 2rem;
    }

    /* -----------------------------
       FADE IN ANIMATION
    ------------------------------*/

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(8px);
        }
        to {
            opacity: 1;
            transform: translateY(0px);
        }
    }

    .block-container {
        animation: fadeIn 0.6s ease-out;
    }

    /* -----------------------------
       CHAT INPUT (CLAUDE PREMIUM)
    ------------------------------*/

    .stChatInput > div {
        border-radius: 999px;
        background: #111111;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 8px;
        transition: all 0.2s ease;
    }

    .stChatInput > div:focus-within {
        border: 1px solid rgba(34,211,238,0.35);
        box-shadow: 0 0 0 1px rgba(34,211,238,0.15);
        background: #121212;
    }

    /* -----------------------------
       BUTTONS (PILL PREMIUM)
    ------------------------------*/

    button {
        border-radius: 999px !important;
        background: #111111 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        transition: all 0.2s ease !important;
    }

    button:hover {
        border: 1px solid rgba(255,255,255,0.16) !important;
        background: #151515 !important;
        transform: translateY(-1px);
    }

    /* -----------------------------
       CARDS
    ------------------------------*/

    .pulse-card {
        background: #111111;
        border-radius: 16px;
        padding: 18px;
        border: 1px solid rgba(255,255,255,0.05);
        transition: all 0.25s ease;
    }

    .pulse-card:hover {
        border: 1px solid rgba(34,211,238,0.25);
        box-shadow: 0 0 30px rgba(34,211,238,0.06);
        transform: translateY(-2px);
    }

    /* -----------------------------
       TITLE GRADIENT
    ------------------------------*/

    .pulse-title {
        font-size: 42px;
        font-weight: 600;
        letter-spacing: -0.02em;
        background: linear-gradient(
            90deg,
            #22D3EE,
            #3B82F6,
            #8B5CF6
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* -----------------------------
       SUBTITLE
    ------------------------------*/

    .pulse-subtitle {
        color: #9A9A9A;
        font-size: 16px;
    }

    /* -----------------------------
       CHAT MESSAGE
    ------------------------------*/

    .stChatMessage {
        animation: fadeIn 0.3s ease;
    }

    </style>
    """, unsafe_allow_html=True)