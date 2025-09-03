# streamlit_app.py — sólido, a11y-first, accent azul, sem scroll na sidebar, HTML seguro

import os, textwrap
from contextlib import suppress
import streamlit as st

# ================== CONFIG ==================
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "http://backend:8000")
st.set_page_config(page_title="Farol — Plataforma", page_icon="🧭",
                   layout="wide", initial_sidebar_state="expanded")

# ================== ESTADO ==================
def init_state():
    st.session_state.setdefault("page", "Home")
    st.session_state.setdefault("zoom", 1.125)      # ~18px
    st.session_state.setdefault("mode", "dark")     # dark / light
    st.session_state.setdefault("high_contrast", False)
    st.session_state.setdefault("reduce_motion", True)
init_state()

# ================== TEMA ==================
def inject_theme_css(zoom: float, mode: str, high_contrast: bool, reduce_motion: bool):
    ACCENT = "#3B82F6"; ACCENT_STRONG = "#1D4ED8"
    if mode == "light":
        base = dict(bg="#FFFFFF", panel="#FFFFFF", card="#FAFAFA",
                    edge="#111111", edge2="#333333", txt="#000000", muted="#111111",
                    accent=ACCENT, accent_strong=ACCENT_STRONG)
    else:
        base = dict(bg="#000000", panel="#0B0B0B", card="#111111",
                    edge="#2F2F2F", edge2="#525252", txt="#FFFFFF", muted="#E5E7EB",
                    accent=ACCENT, accent_strong=ACCENT_STRONG)
    if high_contrast:
        base["edge"] = "#FFFFFF" if mode == "dark" else "#000000"
        base["edge2"] = base["edge"]; base["accent"] = "#1E90FF"; base["accent_strong"] = "#005BBB"
    motion_css = "*,*::before,*::after{transition:none!important;animation:none!important}" if reduce_motion else ""

    st.markdown(f"""
    <style>
      :root {{
        --padding-card: 15px;
        --zoom:{zoom}; --bg:{base['bg']}; --panel:{base['panel']}; --card:{base['card']};
        --edge:{base['edge']}; --edge-2:{base['edge2']}; --txt:{base['txt']}; --muted:{base['muted']};
        --accent:{base['accent']}; --accent-strong:{base['accent_strong']};
        --gap:16px; --radius:14px;
      }}
      *,*::before,*::after {{ box-sizing:border-box; }}
      html,body,[data-testid="stAppViewContainer"] {{
        background:var(--bg)!important; color:var(--txt)!important;
        font-size:calc(16px*var(--zoom)); line-height:1.6;
        font-family:ui-sans-serif,-apple-system,Segoe UI,Roboto,Arial,"Helvetica Neue",sans-serif;
      }}
      [data-testid="stHeader"]{{ background:transparent; }}
      .page-container{{ max-width:1280px; }}
      p{{ margin:0 0 .75rem 0; }} ul{{ margin:.25rem 0 .75rem 1.25rem; padding:0; }}
      ul li{{ margin:.15rem 0; }} h1,h2,h3,h4{{ margin:0 0 .75rem 0; line-height:1.3; }}
      .stack>*+*{{ margin-top:var(--gap); }}
      .skip-link{{ position:absolute; left:-999px; top:auto; width:1px; height:1px; overflow:hidden; z-index:1000;
                   background:var(--accent); color:#000; padding:.6rem .9rem; border-radius:.5rem; }}
      .skip-link:focus{{ left:10px; top:10px; width:auto; height:auto; box-shadow:0 0 0 4px var(--edge); }}
      :focus-visible{{ outline:3px solid var(--accent); outline-offset:3px; border-radius:10px; }}
      a,.stMarkdown a{{ color:var(--accent); text-decoration:underline; }}
      a:hover{{ color:var(--accent-strong); }}

      /* ===== Sidebar compacta (sem rolagem em telas comuns) ===== */
      section[data-testid="stSidebar"]{{ background:var(--panel); border-right:3px solid var(--edge); }}
      .sb-badge{{ display:inline-flex; align-items:center; gap:.5rem; padding:.4rem .6rem; border-radius:10px;
                   border:2px solid var(--edge); background:var(--panel); color:var(--txt); font-weight:900; }}
      /* expander compacto */
      details[open] summary ~ * {{ margin-top:.5rem; }}
      [data-testid="stSidebar"] [data-testid="stVerticalBlock"]>div{{ margin-bottom:.5rem; }}
      section[data-testid="stSidebar"] .nav-btn>button{{
        width:100%; text-align:left; padding:10px 12px; margin:6px 0; border-radius:10px;
        border:2px solid var(--edge); background:var(--card); color:var(--txt); font-weight:800;
      }}
      section[data-testid="stSidebar"] .nav-btn.active>button{{
        border-color:var(--accent); box-shadow:0 0 0 2px var(--accent) inset;
      }}
      .st-emotion-cache-dyadyc{{padding:0 12px 12px 12px;}}
      .stMarkdown{{padding:0 12px 12px 12px;}}
      /* ===== Cards ===== */
      .card{{ display:block; background:var(--card); border:2px solid var(--edge);
             border-radius:var(--radius); overflow:hidden; }}
      .card>.content{{ padding:var(--padding-card); overflow-wrap:anywhere; word-break:normal; }}
      .card>.content>*:last-child{{ margin-bottom:0; }}
      .page-title{{ font-size:2.2rem; font-weight:900; margin:0 0 14px 0; }}
      
      /* ===== Grids ===== */
      .grid-2{{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:var(--gap); }}
      .grid-3{{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:var(--gap); }}
      .grid-4{{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:var(--gap); }}
      @media (max-width:1200px){{ .grid-3,.grid-4{{ grid-template-columns:repeat(2,1fr); }} }}
      @media (max-width:780px){{ .grid-2,.grid-3,.grid-4{{ grid-template-columns:1fr; }} }}

      /* ===== KPIs ===== */
      .kpi{{ background:var(--card); border:2px solid var(--edge); border-radius:var(--radius); padding:var(--gap); }}
      .kpi .lbl{{ color:var(--muted); font-weight:700; }}
      .kpi .val{{ font-size:2rem; font-weight:900; margin:.2rem 0; }}
      .progress{{ height:14px; border-radius:999px; background:{'#111' if st.session_state.mode=='dark' else '#E5E7EB'};
                   border:2px solid var(--edge); }}
      .progress>div{{ height:100%; width:0; border-radius:999px; background:var(--accent); }}

      /* ===== Botões ===== */
      .btn{{ display:inline-flex; align-items:center; gap:.5rem; padding:.6rem .9rem; border-radius:10px;
             font-weight:900; border:2px solid var(--edge); background:var(--panel); color:var(--txt); text-decoration:none; }}
      .btn.primary{{ background:var(--accent); color:#000; border-color:var(--accent); }}

      /* ===== Inputs ===== */
      .stTextInput input, .stTextArea textarea,
      .stSelectbox div[data-baseweb="select"]>div, .stMultiSelect div[data-baseweb="select"]>div{{
        background:var(--panel)!important; color:var(--txt)!important;
        border:2px solid var(--edge)!important; border-radius:10px!important;
      }}

      {motion_css}
    </style>

    """, unsafe_allow_html=True)

# ============= helpers (dedent para impedir “code block”) =============
def _clean_html(s: str) -> str:
    return textwrap.dedent(s).strip() if s else ""

def card(title, body_html: str = "", footer_html: str = "", aria_label: str | None = None):
    html = f"""
    <section class="card" role="region" aria-label="{aria_label or title}">
      <div class="content">
        <h2 style="font-size:1.25rem">{title}</h2>
        {_clean_html(body_html)}
        {_clean_html(footer_html)}
      </div>
    </section>"""
    st.markdown(html, unsafe_allow_html=True)

def kpi_chip(label, value, hint=None, percent=None):
    p_html = ""
    if percent is not None:
        p = max(0, min(100, int(percent)))
        p_html = f'<div class="progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{p}" aria-label="{label} progresso"><div style="width:{p}%"></div></div><p style="margin-top:.25rem">Progresso: {p}%</p>'
    st.markdown(f"""
    <div class="kpi" role="group" aria-label="{label}">
      <div class="content">
        <div class="lbl">{label}</div>
        <div class="val">{value}</div>
        {f'<div style="color:var(--muted)">{hint}</div>' if hint else ""}
        {p_html}
      </div>
    </div>
    """, unsafe_allow_html=True)

def job_card(i: int, match: int | None = None, selo: bool = False):
    desc = "Requisitos: WAI-ARIA, acessibilidade web, testes automatizados."
    selo_html = '<span style="background:#052; padding:.15rem .4rem; border-radius:.4rem; margin-left:.4rem;">Selo Empresa Inclusiva</span>' if selo else ""
    match_html = f'<div style="margin-top:.4rem"><b>Compatibilidade (IA):</b> {match}% — <span style="color:var(--muted)">explicação breve do match</span></div>' if match is not None else ""
    body = f"""
    <p><b>Empresa X</b> · Remoto · <b>Pleno</b>{selo_html}</p>
    <p>{desc}</p>
    {match_html}
    """
    card(f"Vaga #{i} — Desenvolvedor(a) Acessibilidade", body,
         '<a href="#" aria-label="Candidatar-se" class="btn">Candidatar-se</a>',
         aria_label=f"Vaga {i}")

# ================== PÁGINAS ==================
PAGES = [
    ("Boas-vindas", "👋"), 
    ("Home", "🏠"),                      # NÃO alterar
    ("Cadastro por Voz", "📝"),          # Módulo 1
    ("Vagas", "💼"),                    # Módulo 2
    ("Hub de Desenvolvimento", "🧩"),    # Módulo 3
    ("Portfólio de Acessibilidade", "🧰"),# Módulo 5 (parte 1)
    ("Comunidade", "👥"),                # Módulo 5 (parte 2)
    ("Biblioteca", "📚"),                # Módulo 5 (parte 3)
    ("Entrevista (Realtime)", "🎙️"),    # NÃO alterar
    ("Simulação em Andamento", "🟢"),
    ("Feedback", "📊"),
]

# --------- Boas-vindas (com saudação + visão geral) ----------
def page_boas_vindas():
    st.markdown('<div class="page-container stack"><h1 class="page-title">Bem-vindo ao Farol</h1>', unsafe_allow_html=True)
    card("Saudação e Conceito Central",
         """
         <p><b>Farol</b> é uma plataforma de empregabilidade <b>100% acessível e navegável por voz</b> que usa <b>IA</b>
         para criar seu perfil, analisar seu currículo, encontrar vagas compatíveis, preparar entrevistas e apoiar seu desenvolvimento contínuo —
         com foco em profissionais com deficiência visual.</p>
         """)
    card("Como funciona",
         """
         <ul>
           <li><b>Navegação por voz</b> com comandos naturais.</li>
           <li><b>IA em todo o fluxo</b>: currículo, match, recomendações e feedbacks.</li>
           <li><b>Design sólido</b>: foco visível, contrastes e compatibilidade com leitores de tela.</li>
         </ul>
         """)
    st.markdown('<div class="grid-3">', unsafe_allow_html=True)
    card("Módulo 1 — Onboarding e Perfil",
         "<p>Cadastro guiado por voz, importação de currículo com IA e mapeamento de habilidades.</p>")
    card("Módulo 2 — Vagas & Match",
         "<p>Busca por voz, filtros inteligentes, índice de compatibilidade e Selo Empresa Inclusiva.</p>")
    card("Módulo 3 — Desenvolvimento",
         "<p>Gaps de competências, recomendações de cursos e mentoria conectada.</p>")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="grid-3">', unsafe_allow_html=True)
    card("Módulo 4 — Simulador de Entrevistas (IA)",
         "<p>Simulações 100% por voz e relatório final em texto e áudio com pontos fortes e melhorias.</p>")
    card("Módulo 5 — Apoio & Comunidade",
         "<p>Portfólio de acessibilidade, comunidade acessível por voz e biblioteca de direitos.</p>")
    card("Nó Central",
         "<p><b>Empregabilidade acessível por voz com IA</b> — do currículo à contratação.</p>"
         '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:.35rem">'
         '<a class="btn primary" href="#Cadastro-por-Voz">📝 Começar cadastro</a>'
         '<a class="btn" href="#Vagas">💼 Ver vagas</a>'
         '<a class="btn" href="#Hub-de-Desenvolvimento">🧩 Abrir hub</a>'
         '</div>')
    st.markdown('</div></div>', unsafe_allow_html=True)

# --------- Home (mantida) ----------
def page_home():
    st.markdown('<div class="page-container stack"><h1 class="page-title">Seu painel</h1>', unsafe_allow_html=True)

    st.markdown('<div class="grid-4">', unsafe_allow_html=True)
    kpi_chip("Progresso no Hub", "42%", "Módulos finalizados", percent=42)
    kpi_chip("Entrevistas concluídas", "3", "Última há 2 dias")
    kpi_chip("Vagas alinhadas", "12", "Filtradas para seu perfil")
    kpi_chip("Feedback médio", "8.5", "De 0 a 10")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.7, 1])
    with col1:
        card("Próximas ações",
             "<ul><li>Concluir <b>Trilha ARIA Essentials</b> (15 min)</li><li>Agendar <b>simulação de entrevista</b></li><li>Atualizar <b>objetivo profissional</b></li></ul>",
             aria_label="Sugestões de próximas ações")
    with col2:
        card("Lembretes",
             "<ul><li>Atualize o currículo (PDF acessível).</li><li>Revise portfólio com textos alternativos.</li><li>Revise portfólio com textos alternativos.</li></ul>",
             aria_label="Lembretes")
    st.markdown('</div>', unsafe_allow_html=True)

# --------- Cadastro por Voz (Módulo 1) ----------
def page_cadastro():
    st.markdown('<div class="page-container stack"><h1 class="page-title">Cadastro guiado por voz</h1>', unsafe_allow_html=True)

    card("Assistente de Boas-Vindas (voz)",
         "<p>Durante o cadastro, o Farol guia você por voz e confirma cada etapa.</p>")

    # Importação de currículo
    with st.expander("Importação Inteligente de Currículo (PDF/Word)"):
        st.file_uploader("Envie seu currículo", type=["pdf","doc","docx"])
        st.caption("A IA extrai dados e preenche seu perfil. Você confirma tudo por voz.")

    # Formulário rápido (conversacional simplificado)
    with st.form("cadastro_voz"):
        st.text_input("Seu nome", key="cad_nome")
        st.text_input("Objetivo/cargo desejado", placeholder="Ex.: Desenvolvedor(a) Front-end Acessível", key="cad_cargo")
        st.text_input("Preferência de local/remote/híbrido", key="cad_loc")
        st.multiselect("Necessidades de acessibilidade", ["Leitor de tela","Alto contraste","Navegação por voz","Subtítulos automáticos"], key="cad_acess")
        st.text_area("Resumo da experiência", height=160, key="cad_exp")
        if st.form_submit_button("Salvar e continuar"):
            st.success("Cadastro salvo!")

    st.markdown('<div class="grid-2">', unsafe_allow_html=True)
    card("Análise e Melhoria de Currículo (IA)",
         "<p>A IA identifica clareza, estrutura e resultados; sugere melhorias e gera relatório em áudio.</p>")
    card("Mapeamento de Habilidades e Interesses",
         "<p>Identificação de soft/hard skills + questionário adaptativo por voz para entender preferências.</p>")
    st.markdown('</div></div>', unsafe_allow_html=True)

# --------- Vagas & Match (Módulo 2) ----------
def page_vagas():
    st.markdown('<div class="page-container stack"><h1 class="page-title">Busca de Vagas</h1>', unsafe_allow_html=True)
    card("Busca 100% por voz",
         '<p>Diga: <i>“Farol, buscar vagas de analista de marketing remoto em São Paulo.”</i></p>'
         "<p>Use os filtros abaixo para refinar resultados.</p>")
    colf = st.columns(4)
    with colf[0]: st.selectbox("Área", ["Desenvolvimento","QA","Design","Dados"])
    with colf[1]: st.selectbox("Nível", ["Júnior","Pleno","Sênior"])
    with colf[2]: st.selectbox("Modelo", ["Remoto","Híbrido","Presencial"])
    with colf[3]: st.multiselect("Acessibilidade", ["Leitor de tela","Alto contraste","Navegação por voz"])
    st.write("")
    st.markdown('<div class="grid-2">', unsafe_allow_html=True)
    for i in range(1,7):
        job_card(i, match=70+i*3%25+60, selo=(i%2==0))
    st.markdown('</div></div>', unsafe_allow_html=True)

# --------- Desenvolvimento (Módulo 3) ----------
def page_hub():
    st.markdown('<div class="page-container stack"><h1 class="page-title">Hub de Desenvolvimento</h1>', unsafe_allow_html=True)
    st.caption("Trilhas, cursos e desafios práticos — sólidos, legíveis e com foco visível.")
    st.markdown('<div class="grid-4">', unsafe_allow_html=True)
    items = [
        ("Gaps de competências", "Identifique habilidades mais demandadas nas suas vagas-alvo."),
        ("Recomendações de cursos", "Curadoria de conteúdos acessíveis (vídeos, podcasts, microlearning em áudio)."),
        ("Mentoria conectada", "Conecte-se com mentores do mercado."),
        ("Trilha ARIA Essentials", "Papéis, estados e propriedades."),
        ("Acessibilidade em React", "Foco, rótulos e atalhos."),
        ("Testes automatizados", "axe-core + Playwright."),
        ("Leitor de tela", "NVDA/JAWS — práticas."),
        ("Portfólio acessível", "Componentes e exemplos."),
    ]
    for t,d in items:
        card(t, d, '<a href="#" class="btn primary" aria-label="Iniciar">Iniciar</a>', aria_label=t)
    st.markdown('</div></div>', unsafe_allow_html=True)

# --------- Entrevista (Realtime) (NÃO alterar) ----------
def page_entrevista():
    st.markdown('<div class="page-container stack"><h1 class="page-title">Simulador de Entrevistas (voz em tempo real)</h1>', unsafe_allow_html=True)
    cc = st.columns([1.5,1])
    with cc[0]:
        st.markdown(f"""
<section class="card" role="region" aria-label="Simulador"><div class="content">
  <iframe src="{BACKEND_PUBLIC_URL}/webrtc" title="Farol Realtime" width="100%" height="380"
          style="border-radius:10px;border:2px solid var(--edge); background: var(--panel);"
          allow="microphone; autoplay; clipboard-read; clipboard-write"></iframe>
  <p>Se o áudio não tocar, clique na página para liberar o autoplay do navegador.
     <a href="{BACKEND_PUBLIC_URL}/webrtc">Abrir em nova aba</a>.</p>
</div></section>""", unsafe_allow_html=True)
    with cc[1]:
        card("Dicas de uso",
             "<ul><li>Permita o microfone quando solicitado.</li><li>Use fones para evitar eco.</li><li>Pressione TAB para navegar pelos controles.</li></ul>")
    st.markdown('</div>', unsafe_allow_html=True)

# --------- Simulação em andamento ----------
def page_simulacao():
    st.markdown('<div class="page-container stack"><h1 class="page-title">Simulação em andamento</h1>', unsafe_allow_html=True)
    card("Status", "Acompanhe suas falas e as respostas do agente enquanto a entrevista ocorre.")
    st.markdown('</div>', unsafe_allow_html=True)

# --------- Feedback ----------
def page_feedback():
    st.markdown('<div class="page-container stack"><h1 class="page-title">Feedback da Simulação</h1>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        card("Pontos fortes", "<ul><li>Comunicação clara</li><li>Conceitos ARIA corretos</li><li>Boa senioridade em testes</li></ul>")
    with c2:
        card("Oportunidades de melhoria", "<ul><li>Estruturar STAR</li><li>Detalhar métricas de impacto</li><li>Explicar trade-offs</li></ul>")
    st.markdown('</div>', unsafe_allow_html=True)

# --------- Portfólio (Módulo 5) ----------
def page_portfolio():
    st.markdown('<div class="page-container stack"><h1 class="page-title">Meu Portfólio de Acessibilidade</h1>', unsafe_allow_html=True)
    card("Preferências e tecnologias assistivas",
         "<p>Registre leitores de tela, atalhos, contrastes, fontes e adaptações preferidas.</p>")
    with st.form("portfolio"):
        st.multiselect("Tecnologias assistivas que uso", ["NVDA","JAWS","VoiceOver","TalkBack","Teclado apenas","Comandos de voz"])
        st.text_area("Notas / observações", height=120)
        st.form_submit_button("Salvar")
    st.markdown('</div>', unsafe_allow_html=True)

# --------- Comunidade (Módulo 5) ----------
def page_comunidade():
    st.markdown('<div class="page-container stack"><h1 class="page-title">Comunidade</h1>', unsafe_allow_html=True)
    card("Fórum acessível por voz (em breve)",
         "<p>Espaço moderado por IA para perguntas, trocas e networking — 100% acessível.</p>")
    card("Regras de convivência",
         "<ul><li>Respeito e inclusão.</li><li>Conteúdo útil e verificável.</li><li>Zero tolerância a discriminação.</li></ul>")
    st.markdown('</div>', unsafe_allow_html=True)

# --------- Biblioteca (Módulo 5) ----------
def page_biblioteca():
    st.markdown('<div class="page-container stack"><h1 class="page-title">Biblioteca de Direitos e Legislação</h1>', unsafe_allow_html=True)
    card("Conteúdos em áudio",
         "<p>Resumos em áudio e texto sobre leis e direitos trabalhistas voltados à empregabilidade inclusiva.</p>")
    st.markdown('<div class="grid-3">', unsafe_allow_html=True)
    card("Lei de Cotas", "<p>Resumo acessível e exemplos práticos de aplicação.</p>")
    card("Acessibilidade no trabalho", "<p>Direitos a adaptações razoáveis e tecnologias assistivas.</p>")
    card("Recursos e canais", "<p>Instituições e serviços de apoio ao trabalhador com deficiência.</p>")
    st.markdown('</div></div>', unsafe_allow_html=True)

# ================== SIDEBAR ==================
def a11y_controls_sidebar():
    st.markdown('<span class="sb-badge">🧭 Farol — Plataforma</span>', unsafe_allow_html=True)
    # Acessibilidade compacta
    with st.expander("Acessibilidade", expanded=False):
        st.session_state.mode = st.radio("Esquema de cores", ["dark","light"],
                                         index=0 if st.session_state.mode=="dark" else 1, horizontal=True)
        st.session_state.high_contrast = st.toggle("Alto contraste", value=st.session_state.high_contrast)
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("A−"): st.session_state.zoom = max(1.0, round(st.session_state.zoom-0.125,3)); st.rerun()
        with c2:
            if st.button("Reset"): st.session_state.zoom = 1.125; st.rerun()
        with c3:
            if st.button("A+"): st.session_state.zoom = min(2.0, round(st.session_state.zoom+0.125,3)); st.rerun()
        st.session_state.reduce_motion = st.toggle("Reduzir animações", value=st.session_state.reduce_motion)
    st.divider()

def sidebar_nav():
    use_option_menu = False
    with suppress(Exception):
        from streamlit_option_menu import option_menu
        use_option_menu = True

    if use_option_menu:
        # deve ter o MESMO tamanho de PAGES
        icons = [
            "hand-thumbs-up",  # Boas-vindas
            "house",           # Home
            "pencil-square",   # Cadastro por Voz
            "briefcase",       # Vagas
            "puzzle",          # Hub
            "tools",           # Portfólio
            "people",          # Comunidade
            "book",            # Biblioteca
            "mic",             # Entrevista
            "record-circle",   # Simulação
            "bar-chart"        # Feedback
        ]
        current = option_menu(
            menu_title=None, options=[n for n,_ in PAGES], icons=icons,
            default_index=[n for n,_ in PAGES].index(st.session_state.page),
            orientation="vertical",
            styles={
                "container": {"padding": "4px 0 4px 0"},
                "nav-link": {
                    "font-weight": "800","padding":"10px 12px","border-radius":"10px","margin":"6px 0",
                    "background-color":"var(--card)","border":"2px solid var(--edge)","color":"var(--txt)",
                },
                "nav-link-selected": {
                    "background-color":"var(--panel)","border":"2px solid var(--accent)","color":"var(--txt)",
                },
                "icon": {"color":"var(--accent)"},
            },
        )
        if current != st.session_state.page:
            st.session_state.page = current; st.rerun()
    else:
        for name, icon in PAGES:
            st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
            if st.button(f"{icon}  {name}", key=f"navbtn_{name}", use_container_width=True):
                st.session_state.page = name; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    if st.button("Ir para Entrevista 🎙️", use_container_width=True):
        st.session_state.page = "Entrevista (Realtime)"; st.rerun()
    st.caption("Tudo acessível por teclado (TAB / SHIFT+TAB / ENTER).")

# ================== APP ==================
st.markdown('<a href="#conteudo-principal" class="skip-link">Pular para conteúdo principal</a>', unsafe_allow_html=True)
with st.sidebar:
    a11y_controls_sidebar()
    sidebar_nav()
inject_theme_css(st.session_state.zoom, st.session_state.mode, st.session_state.high_contrast, st.session_state.reduce_motion)

# Região viva p/ leitores de tela
sr = st.empty()
sr.markdown(f'<div aria-live="polite" style="position:absolute; left:-10000px; top:auto; width:1px; height:1px; overflow:hidden">Página atual: {st.session_state.page}</div>', unsafe_allow_html=True)

st.markdown('<main id="conteudo-principal" role="main" aria-label="Conteúdo principal">', unsafe_allow_html=True)
page = st.session_state.page
if page == "Boas-vindas": page_boas_vindas()
elif page == "Home": page_home()
elif page == "Cadastro por Voz": page_cadastro()
elif page == "Vagas": page_vagas()
elif page == "Hub de Desenvolvimento": page_hub()
elif page == "Portfólio de Acessibilidade": page_portfolio()
elif page == "Comunidade": page_comunidade()
elif page == "Biblioteca": page_biblioteca()
elif page == "Entrevista (Realtime)": page_entrevista()
elif page == "Simulação em Andamento": page_simulacao()
elif page == "Feedback": page_feedback()
st.markdown('</main>', unsafe_allow_html=True)
