# streamlit_app.py
import os
from contextlib import suppress
import streamlit as st

# ========= CONFIG =========
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "http://backend:8011")
st.set_page_config(
    page_title="Farol — Plataforma",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========= THEME / CSS =========
st.markdown(
    """
    <style>
      :root{
        --bg:#0b0f17; --bg-2:#0e1421; --card:#121826; --card-2:#141c2b;
        --muted:#97a7bd; --txt:#f2f5f9; --edge:#1c2435;
        --accent:#7c3aed; --accent-2:#6d28d9;
      }
      html,body,[data-testid="stAppViewContainer"]{ background:var(--bg)!important; color:var(--txt)!important; }
      [data-testid="stHeader"]{ background:transparent; }
      .card{ background:linear-gradient(180deg,var(--card),var(--card-2));
             border:1px solid var(--edge); border-radius:16px; padding:16px 18px; box-shadow:0 6px 18px rgba(0,0,0,.28);}
      .title-lg{ font-weight:800; font-size:1.3rem; }
      .kpis{ display:grid; gap:12px; grid-template-columns: repeat(4, minmax(0,1fr)); }
      .kpi{ background:#0f1626; border:1px solid var(--edge); border-radius:14px; padding:14px; }
      .kpi .v{ font-size:1.6rem; font-weight:800; }
      .divider{ height:1px; background:linear-gradient(90deg, transparent, #22304a, transparent); margin:10px 0 16px; }
      .page-title{ font-size:1.4rem; font-weight:800; margin:0 0 6px 0; }

      /* ===== Sidebar geral ===== */
      section[data-testid="stSidebar"] { background:#0a1220; border-right:1px solid #111827; }
      .sb-header{ padding:10px 6px 6px 6px; }
      .sb-badge{
        display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:999px;
        border:1px solid #21314d; background:#0e1523; color:#cbd5e1; font-weight:700;
      }

      /* ===== Botões de navegação (1 clique, área grande) ===== */
      section[data-testid="stSidebar"] .nav-btn > button {
        width:100%;
        text-align:left;
        padding:14px 14px;
        margin:8px 0;
        border-radius:14px;
        border:1px solid #1f2a41;
        background:#0c1526;
        color:#e5e7eb;
        font-weight:700;
      }
      section[data-testid="stSidebar"] .nav-btn > button:hover {
        background:#0f1b34; border-color:#2f3e60;
      }
      /* estado ativo (aplico via HTML ao renderizar o item atual) */
      section[data-testid="stSidebar"] .nav-btn.active > button {
        background:linear-gradient(180deg,#1b2438,#0f1b2f);
        border-color:#334155; box-shadow:0 0 0 2px #334155 inset;
      }

      /* botão grande da ação secundária */
      section[data-testid="stSidebar"] .action-btn > button{
        width:100%; padding:14px 12px; border-radius:12px; font-weight:700;
        background:#1b2438; border:1px solid #334155; color:#e5e7eb;
      }
      section[data-testid="stSidebar"] .action-btn > button:hover{
        background:#222d47; border-color:#3b4d6e;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ========= PÁGINAS =========
PAGES = [
    ("Boas-vindas", "👋"),
    ("Cadastro por Voz", "📝"),
    ("Home", "🏠"),
    ("Vagas", "💼"),
    ("Hub de Desenvolvimento", "🧩"),
    ("Entrevista (Realtime)", "🎙️"),
    ("Simulação em Andamento", "🟢"),
    ("Feedback", "📊"),
]
if "page" not in st.session_state:
    st.session_state.page = PAGES[0][0]

def card(title, body_md, footer=None):
    st.markdown(f'<div class="card"><div class="title-lg">{title}</div>', unsafe_allow_html=True)
    st.markdown(body_md, unsafe_allow_html=True)
    if footer: st.markdown(footer, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def page_boas_vindas():
    st.markdown('<div class="page-title">Bem-vindo ao <b>Farol</b></div>', unsafe_allow_html=True)
    st.caption("Navegação por voz, descrição de tela e preparação para entrevistas — tudo em um só lugar.")
    c1, c2, c3 = st.columns(3)
    with c1: card("Cadastro guiado", "Preencha seu perfil **falando**.")
    with c2: card("Assistente de carreira", "Recomenda **vagas** e **cursos**.")
    with c3: card("Simulador de entrevista", "Converse em **tempo real** e receba **feedback**.")

def page_cadastro():
    st.markdown('<div class="page-title">Cadastro guiado por voz</div>', unsafe_allow_html=True)
    with st.form("cadastro_voz"):
        st.text_input("Seu nome", key="cad_nome")
        st.text_input("Objetivo/cargo desejado", placeholder="Ex.: Desenvolvedor(a) Front-end Acessível", key="cad_cargo")
        st.text_input("Preferência de local/remote/híbrido", key="cad_loc")
        st.multiselect("Necessidades de acessibilidade", ["Leitor de tela","Alto contraste","Navegação por voz","Subtítulos automáticos"], key="cad_acess")
        st.text_area("Resumo da experiência", height=120, key="cad_exp")
        if st.form_submit_button("Salvar e continuar →"):
            st.success("Cadastro salvo!")

def page_home():
    st.markdown('<div class="page-title">Seu painel</div>', unsafe_allow_html=True)
    st.caption("Resumo do seu progresso e recomendações.")
    st.markdown('<div class="kpis">', unsafe_allow_html=True)
    for label, val, hint in [
        ("Progresso no Hub", "42%", "Módulos finalizados"),
        ("Entrevistas concluídas", "3", "Última há 2 dias"),
        ("Vagas alinhadas", "12", "filtradas para seu perfil"),
        ("Feedback médio", "8.5", "de 0 a 10"),
    ]:
        st.markdown(f'<div class="kpi"><div style="color:#9fb3c8">{label}</div><div class="v">{val}</div><div style="color:#9fb3c8">{hint}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def page_vagas():
    st.markdown('<div class="page-title">Busca de Vagas</div>', unsafe_allow_html=True)
    colf = st.columns(4)
    with colf[0]: st.selectbox("Área", ["Desenvolvimento","QA","Design","Dados"])
    with colf[1]: st.selectbox("Nível", ["Júnior","Pleno","Sênior"])
    with colf[2]: st.selectbox("Modelo", ["Remoto","Híbrido","Presencial"])
    with colf[3]: st.multiselect("Acessibilidade", ["Leitor de tela","Alto contraste","Navegação por voz"])
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i in range(6):
        with cols[i%3]:
            card(
                f"Vaga #{i+1} — Dev Acessível",
                "Empresa X · Remoto · **Pleno**\n\nRequisitos: WAI-ARIA, acessibilidade web, testes automatizados.",
                '<a href="#" style="text-decoration:none" class="btn">Candidatar-se</a>'
            )

def page_hub():
    st.markdown('<div class="page-title">Hub de Desenvolvimento</div>', unsafe_allow_html=True)
    st.caption("Trilhas, cursos e desafios práticos.")
    cols = st.columns(4)
    items = [
        ("Trilha ARIA Essentials", "Domine papéis, estados e propriedades."),
        ("Acessibilidade em React", "Padrões, focos e atalhos."),
        ("Testes automatizados", "axe-core + Playwright."),
        ("Navegação por voz", "Comandos e SR."),
        ("Escrita inclusiva", "Tom, legibilidade e UX writing."),
        ("WAI e WCAG 2.2", "Critérios e checklists."),
        ("Leitor de tela", "NVDA/JAWS — boas práticas."),
        ("Portfólio acessível", "Componentes e exemplos."),
    ]
    for i,(t,d) in enumerate(items):
        with cols[i%4]:
            card(t, d, '<a class="btn" href="#">Iniciar</a>')

def page_entrevista():
    st.markdown('<div class="page-title">Simulador de Entrevistas (voz em tempo real)</div>', unsafe_allow_html=True)
    st.caption("Ao carregar, o navegador pode pedir permissão de microfone. As respostas tocam automaticamente.")
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
    st.info("Se o áudio não tocar, clique na página para liberar o autoplay do navegador.")

def page_simulacao():
    st.markdown('<div class="page-title">Simulação em andamento</div>', unsafe_allow_html=True)
    st.caption("Acompanhe suas falas e as respostas do agente enquanto a entrevista ocorre.")

def page_feedback():
    st.markdown('<div class="page-title">Feedback da Simulação</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        card("Pontos fortes", "- Comunicação clara\n- Conceitos ARIA corretos\n- Boa senioridade em testes")
    with c2:
        card("Oportunidades de melhoria", "- Estruturar STAR\n- Detalhar métricas de impacto\n- Falar de trade-offs")

# ========= SIDEBAR / NAV =========
def sidebar_nav():
    st.markdown('<div class="sb-header"><span class="sb-badge">🧭 Farol — Plataforma</span></div>', unsafe_allow_html=True)

    # Se a lib estiver instalada, usa option_menu (1 clique garantido)
    use_option_menu = False
    with suppress(Exception):
        from streamlit_option_menu import option_menu
        use_option_menu = True

    if use_option_menu:
        icons = ["hand-thumbs-up","pencil-square","house","briefcase","puzzle","mic","record-circle","bar-chart"]
        current = option_menu(
            menu_title=None,
            options=[n for n,_ in PAGES],
            icons=icons,
            default_index=[n for n,_ in PAGES].index(st.session_state.page),
            orientation="vertical",
            styles={
                "container": {"padding": "8px 0 8px 0"},
                "nav-link": {
                    "font-weight": "700",
                    "padding": "16px 16px",
                    "border-radius": "14px",
                    "margin": "8px 0",
                    "background-color": "#0c1526",
                    "border": "1px solid #1f2a41",
                    "color": "#e5e7eb",
                },
                "nav-link-hover": {"background-color": "#0f1b34", "border-color": "#2f3e60"},
                "nav-link-selected": {
                    "background": "linear-gradient(180deg,#1b2438,#0f1b2f)",
                    "border-color": "#334155",
                    "box-shadow": "0 0 0 2px #334155 inset",
                },
                "icon": {"color": "#cbd5e1"},
            },
        )
        if current != st.session_state.page:
            st.session_state.page = current
            st.rerun()
    else:
        # Fallback 1-clique com botões
        for name, icon in PAGES:
            active_cls = " active" if st.session_state.page == name else ""
            st.markdown(f'<div class="nav-btn{active_cls}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {name}", key=f"navbtn_{name}", use_container_width=True):
                st.session_state.page = name
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="action-btn">', unsafe_allow_html=True)
    if st.button("Ir para Entrevista 🎙️", use_container_width=True):
        st.session_state.page = "Entrevista (Realtime)"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("Dica: o simulador pedirá acesso ao microfone.")

with st.sidebar:
    sidebar_nav()

# ========= ROTEAMENTO =========
page = st.session_state.page
if page == "Boas-vindas":
    page_boas_vindas()
elif page == "Cadastro por Voz":
    page_cadastro()
elif page == "Home":
    page_home()
elif page == "Vagas":
    page_vagas()
elif page == "Hub de Desenvolvimento":
    page_hub()
elif page == "Entrevista (Realtime)":
    page_entrevista()
elif page == "Simulação em Andamento":
    page_simulacao()
elif page == "Feedback":
    page_feedback()
