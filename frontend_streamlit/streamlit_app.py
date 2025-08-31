import os
import streamlit as st

BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "http://backend:8000")

st.set_page_config(
    page_title="Farol Realtime",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      :root {
        --farol-bg: #0b0f17;
        --farol-card: #121826;
        --farol-text: #f2f5f9;
        --farol-muted: #9fb3c8;
      }
      html, body, [data-testid="stAppViewContainer"] { background-color: var(--farol-bg) !important; color: var(--farol-text) !important; }
      .farol-card { background: var(--farol-card); border: 2px solid #1c2435; border-radius: 14px; padding: 18px 20px; }
      .farol-title { font-size: 1.8rem; font-weight: 800; letter-spacing: 0.3px; }
      .farol-sub { font-size: 1.05rem; color: var(--farol-muted); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="farol-card" role="region" aria-label="Farol Realtime">
      <div class="farol-title">🎙️ Farol — Voz em tempo real</div>
      <div class="farol-sub">Sem botões. Ao abrir, pedimos o microfone e escutamos continuamente. As respostas tocam assim que chegam.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.components.v1.html(
    f"""
    <iframe
      src="{BACKEND_PUBLIC_URL}/webrtc"
      title="Farol Realtime"
      width="100%"
      height="380"
      style="border-radius:16px;border:1px solid rgba(255,255,255,.1);"
      allow="microphone; autoplay; clipboard-read; clipboard-write"
    ></iframe>
    """,
    height=420,
)

st.caption(
    "Dica: se o áudio não tocar automaticamente, o navegador pode exigir uma interação mínima (toque/tecla) para liberar autoplay."
)

