"""
Interface Streamlit pour ResumeRadar
Mode Analyse + Mode CVs & Contact
Premium SaaS Dark Mode UI
"""
import streamlit as st
from urllib.parse import quote

from config.settings import EMAIL_SUBJECT, EMAIL_BODY

# Configuration de la page
st.set_page_config(
    page_title="ResumeRadar",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS - Premium SaaS Dark Mode
# ============================================================
st.markdown("""
<style>
    /* === GOOGLE FONTS === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* === RESET & GLOBAL === */
    *, *::before, *::after { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

    #MainMenu, footer { visibility: hidden; }

    /* Header transparent */
    header[data-testid="stHeader"] {
        background: transparent;
        backdrop-filter: none;
    }

    /* Masquer le texte "keyboard_double_arrow_left" du bouton collapse sidebar */
    [data-testid="stSidebar"] button[kind="header"] {
        font-size: 0 !important;
        color: transparent !important;
        overflow: hidden;
        width: 2rem;
        height: 2rem;
        padding: 0 !important;
    }

    [data-testid="collapsedControl"] {
        font-size: 0 !important;
        color: transparent !important;
    }

    /* Cibler le texte Material Icons directement */
    .st-emotion-cache-1egp75f,
    [data-testid="stSidebar"] [data-testid="stBaseButton-header"] {
        font-size: 0 !important;
        color: transparent !important;
    }

    /* Forcer le masquage de tout texte dans les boutons header sidebar */
    [data-testid="stSidebar"] button[kind="header"] span,
    [data-testid="stSidebar"] button[kind="headerNoPadding"] span,
    button[data-testid="stBaseButton-header"] span,
    button[data-testid="baseButton-header"] span {
        font-size: 0 !important;
        color: transparent !important;
        display: block;
        width: 1.2rem;
        height: 1.2rem;
        overflow: hidden;
    }

    .stApp {
        background-color: #0E1117;
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 980px;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }

    /* === SIDEBAR - GLASSMORPHISM === */
    [data-testid="stSidebar"] {
        background: #13161d;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    /* === SIDEBAR NAV ITEMS === */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.7rem 1rem;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 0.3rem;
        font-size: 0.88rem;
        font-weight: 500;
        text-decoration: none;
        color: rgba(255,255,255,0.5);
    }

    .nav-item:hover {
        background: rgba(255,255,255,0.05);
        color: rgba(255,255,255,0.85);
    }

    .nav-item.active {
        background: rgba(41, 98, 255, 0.12);
        color: #5B8DEF;
        font-weight: 600;
    }

    .nav-item .nav-icon {
        font-size: 1.1rem;
        width: 1.4rem;
        text-align: center;
    }

    /* === SIDEBAR BUTTONS (fallback for st.button) === */
    [data-testid="stSidebar"] .stButton > button {
        border-radius: 10px;
        padding: 0.65rem 1rem;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        border: none;
        text-align: left;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(41, 98, 255, 0.15);
        color: #5B8DEF;
        box-shadow: none;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: transparent;
        color: rgba(255,255,255,0.45);
        border: none;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.05);
        color: rgba(255,255,255,0.8);
    }

    /* === SIDEBAR LOGO === */
    .sidebar-logo {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: white;
        padding: 0 0.5rem 1.2rem 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .sidebar-logo .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #2962FF;
        display: inline-block;
        box-shadow: 0 0 10px rgba(41, 98, 255, 0.5);
    }

    /* === SIDEBAR STATS CARD === */
    .stats-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-top: 0.5rem;
    }

    .stats-card .stats-title {
        color: rgba(255,255,255,0.3);
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }

    .stats-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.3rem 0;
    }

    .stats-row .label {
        color: rgba(255,255,255,0.4);
        font-size: 0.82rem;
    }

    .stats-row .value {
        color: rgba(255,255,255,0.9);
        font-weight: 600;
        font-size: 0.85rem;
    }

    .stats-row .value.accent {
        color: #5B8DEF;
    }

    /* === HEADER === */
    .app-header {
        margin-bottom: 2rem;
    }

    .app-header h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: rgba(255,255,255,0.95);
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }

    .app-header .subtitle {
        color: rgba(255,255,255,0.35);
        font-size: 0.9rem;
        font-weight: 400;
        line-height: 1.5;
    }

    /* === SECTION LABELS === */
    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: rgba(255,255,255,0.25);
        margin-bottom: 0.8rem;
        margin-top: 1.5rem;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: rgba(255,255,255,0.9);
        margin-bottom: 0.3rem;
        letter-spacing: -0.3px;
    }

    /* === BOUTONS PRINCIPAUX === */
    .main .stButton > button[kind="primary"] {
        background: #2962FF;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.2px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(41, 98, 255, 0.25);
    }

    .main .stButton > button[kind="primary"]:hover {
        background: #1E54E6;
        box-shadow: 0 4px 16px rgba(41, 98, 255, 0.35);
        transform: translateY(-1px);
    }

    .main .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.04);
        color: rgba(255,255,255,0.6);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s;
    }

    .main .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.08);
        border-color: rgba(255,255,255,0.15);
        color: white;
    }

    /* === FILE UPLOADER === */
    [data-testid="stFileUploader"] {
        background: transparent;
    }

    [data-testid="stFileUploader"] section {
        border: 1.5px dashed rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        background: rgba(255,255,255,0.01);
    }

    [data-testid="stFileUploader"] section:hover {
        border-color: rgba(41, 98, 255, 0.4);
        background: rgba(41, 98, 255, 0.03);
    }

    [data-testid="stFileUploader"] section > button {
        background: rgba(41, 98, 255, 0.1) !important;
        color: #5B8DEF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
    }

    /* === TEXT AREA & INPUTS === */
    .stTextArea textarea, .stTextInput input {
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.07);
        background: rgba(255,255,255,0.03);
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
        padding: 0.8rem 1rem;
        transition: all 0.2s ease;
    }

    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: rgba(41, 98, 255, 0.5);
        box-shadow: 0 0 0 3px rgba(41, 98, 255, 0.08);
        background: rgba(255,255,255,0.04);
    }

    .stTextArea textarea::placeholder, .stTextInput input::placeholder {
        color: rgba(255,255,255,0.2);
    }

    /* Labels */
    .stTextArea label, .stTextInput label, .stSlider label, .stFileUploader label {
        color: rgba(255,255,255,0.5) !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
    }

    /* === SLIDER === */
    .stSlider [data-testid="stThumbValue"] {
        color: #5B8DEF;
        font-weight: 700;
    }

    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: #2962FF;
    }

    /* === TABLE === */
    .stTable table {
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.06);
        width: 100%;
    }

    .stTable thead th {
        background: rgba(255,255,255,0.03);
        color: rgba(255,255,255,0.4);
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.8px;
        padding: 0.85rem 1rem;
        border: none;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .stTable tbody td {
        padding: 0.8rem 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.03);
        font-size: 0.88rem;
        color: rgba(255,255,255,0.75);
    }

    .stTable tbody tr:last-child td {
        border-bottom: none;
    }

    .stTable tbody tr:hover td {
        background: rgba(41, 98, 255, 0.04);
    }

    /* === CARDS === */
    .card {
        background: rgba(255,255,255,0.02);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        margin: 0.8rem 0;
    }

    .card .card-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: rgba(255,255,255,0.3);
        margin-bottom: 0.2rem;
    }

    .card .card-value {
        font-size: 0.92rem;
        color: rgba(255,255,255,0.8);
        font-weight: 400;
    }

    .card .card-value a {
        color: #5B8DEF;
        text-decoration: none;
    }

    /* === SCORE BADGE === */
    .score-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.9rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
        letter-spacing: 0.3px;
    }

    .score-high {
        background: rgba(46, 160, 67, 0.15);
        color: #3FB950;
    }

    .score-mid {
        background: rgba(210, 153, 34, 0.15);
        color: #D29922;
    }

    .score-low {
        background: rgba(207, 34, 46, 0.15);
        color: #F85149;
    }

    /* === NAVIGATION CANDIDAT === */
    .nav-header {
        text-align: center;
        padding: 0.6rem;
    }

    .nav-header .name {
        font-size: 1.25rem;
        font-weight: 700;
        color: rgba(255,255,255,0.95);
        letter-spacing: -0.3px;
    }

    /* === PROGRESS BAR === */
    .stProgress > div > div > div > div {
        background: #2962FF;
        border-radius: 4px;
    }

    /* === LINK BUTTON === */
    .stLinkButton a {
        background: #2962FF !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        box-shadow: 0 2px 8px rgba(41, 98, 255, 0.25);
        transition: all 0.2s ease !important;
    }

    .stLinkButton a:hover {
        background: #1E54E6 !important;
        box-shadow: 0 4px 16px rgba(41, 98, 255, 0.35) !important;
        transform: translateY(-1px);
    }

    /* === DIVIDER === */
    hr {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin: 2rem 0;
    }

    /* === EXPANDER === */
    .streamlit-expanderHeader {
        border-radius: 10px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        font-weight: 500;
        font-size: 0.88rem;
    }

    /* Masquer le texte brut "arrow_right" des icones Material dans les expanders.
       Streamlit utilise des <span> avec la police Material Symbols. Si la police
       ne charge pas, le texte "arrow_right" s'affiche en clair. On le cache. */
    [data-testid="stExpander"] summary span[class*="icon"],
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"],
    [data-testid="stExpander"] details summary > div > span:first-child,
    [data-testid="stExpander"] summary span.material-symbols-rounded {
        font-size: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }

    /* === ALERT BOXES === */
    [data-testid="stAlert"] {
        border-radius: 10px;
        border: none;
        font-size: 0.88rem;
    }

    /* === LLM ANALYSIS === */
    .llm-card {
        background: rgba(41, 98, 255, 0.04);
        border: 1px solid rgba(41, 98, 255, 0.12);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .llm-card .llm-label {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #5B8DEF;
        margin-bottom: 0.5rem;
    }

    /* === EMPTY STATE === */
    .empty-state {
        text-align: center;
        padding: 5rem 2rem;
    }

    .empty-state .empty-icon {
        font-size: 2.5rem;
        margin-bottom: 1.2rem;
        opacity: 0.3;
    }

    .empty-state .empty-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: rgba(255,255,255,0.4);
        margin-bottom: 0.4rem;
    }

    .empty-state .empty-desc {
        font-size: 0.88rem;
        color: rgba(255,255,255,0.2);
        line-height: 1.6;
    }

    /* === CANDIDATE INFO GRID === */
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem;
        margin: 1rem 0;
    }

    .info-item {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 1rem 1.2rem;
    }

    .info-item .info-label {
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: rgba(255,255,255,0.25);
        margin-bottom: 0.3rem;
    }

    .info-item .info-value {
        font-size: 0.92rem;
        color: rgba(255,255,255,0.8);
        font-weight: 500;
    }

    /* === PDF VIEWER === */
    .pdf-frame {
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.06);
        overflow: hidden;
        margin-top: 0.5rem;
    }

    .pdf-frame iframe {
        border: none;
        border-radius: 10px;
    }

    /* === SUBTLE SEPARATOR === */
    .sep {
        height: 1px;
        background: rgba(255,255,255,0.05);
        margin: 1.8rem 0;
        border: none;
    }
</style>
""", unsafe_allow_html=True)


# === FONCTIONS UTILITAIRES ===

def extract_text_from_pdf(uploaded_file) -> str:
    """Extrait le texte brut d'un fichier PDF uploade"""
    from pypdf import PdfReader
    import io
    reader = PdfReader(io.BytesIO(uploaded_file.getbuffer()))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def build_mailto_link(emails, subject, body):
    """Construit un lien mailto avec BCC"""
    bcc = ",".join(emails)
    return f"mailto:?bcc={quote(bcc)}&subject={quote(subject)}&body={quote(body)}"


def get_score_class(score_pct):
    """Retourne la classe CSS selon le score"""
    if score_pct >= 70:
        return "score-high"
    elif score_pct >= 50:
        return "score-mid"
    return "score-low"


# ============================================================
# SIDEBAR
# ============================================================

# Logo
st.sidebar.markdown("""
<div class="sidebar-logo">
    <span class="dot"></span> ResumeRadar
</div>
""", unsafe_allow_html=True)

# Navigation
if "mode" not in st.session_state:
    st.session_state.mode = "Analyse"

mode = st.session_state.mode

# Nav items via HTML + boutons Streamlit en fallback
analyse_type = "primary" if mode == "Analyse" else "secondary"
cvs_type = "primary" if mode == "CVs & Contact" else "secondary"

if st.sidebar.button("Analyse", use_container_width=True, type=analyse_type):
    st.session_state.mode = "Analyse"
    st.rerun()
if st.sidebar.button("CVs & Contact", use_container_width=True, type=cvs_type):
    st.session_state.mode = "CVs & Contact"
    st.rerun()

mode = st.session_state.mode

# Stats si resultats existent
if "review_candidates" in st.session_state:
    st.sidebar.markdown('<div class="sep"></div>', unsafe_allow_html=True)

    cands = st.session_state.review_candidates
    candidates_count = len(cands)
    emails_count = len([c for c in cands if c["email"]])
    avg_score = int(sum(c["score"] for c in cands) / candidates_count * 100)

    st.sidebar.markdown(f"""
    <div class="stats-card">
        <div class="stats-title">Derniere analyse</div>
        <div class="stats-row">
            <span class="label">Candidats retenus</span>
            <span class="value">{candidates_count}</span>
        </div>
        <div class="stats-row">
            <span class="label">Emails trouves</span>
            <span class="value">{emails_count}</span>
        </div>
        <div class="stats-row">
            <span class="label">Score moyen</span>
            <span class="value accent">{avg_score}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# MODE ANALYSE
# ============================================================

if mode == "Analyse":

    # Header
    st.markdown("""
    <div class="app-header">
        <h1>Analyse et tri de CVs</h1>
        <div class="subtitle">Uploadez des CVs et collez une description de poste. Le scoring par embeddings et le LLM travaillent ensemble pour identifier les meilleurs profils.</div>
    </div>
    """, unsafe_allow_html=True)

    # Upload
    st.markdown('<div class="section-label">Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Uploadez vos CVs (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
        key="review_uploader",
        label_visibility="collapsed"
    )

    # Description du poste
    st.markdown('<div class="section-label">Description du poste</div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Description du poste",
        height=180,
        placeholder="Ex: Recherche Data Engineer Python avec experience Kafka, Spark, et SQL...",
        label_visibility="collapsed"
    )

    # Nombre de candidats
    max_candidates = len(uploaded_files) if uploaded_files else 100
    top_n = st.number_input(
        "Candidats a retenir",
        min_value=1,
        max_value=max(max_candidates, 1),
        value=None,
        step=1,
        placeholder="Entrez un nombre"
    )

    st.markdown("")  # spacing

    # CTA
    analyze_btn = st.button("Analyser et Trier", type="primary", use_container_width=True)

    if analyze_btn and uploaded_files and job_description:
        from utils.email_extractor import extract_email
        from utils.scoring import score_candidates
        from utils.email_extractor import extract_name_from_filename
        from langchain_ollama import OllamaLLM as Ollama
        from config.settings import (
            OLLAMA_MODEL, OLLAMA_BASE_URL, OLLAMA_TEMPERATURE,
            OLLAMA_NUM_CTX, DEFAULT_CONTEXT_WINDOW,
        )

        candidates = []
        progress = st.progress(0)
        status = st.empty()

        # --- Etape 1 : Extraction texte + email ---
        for i, uploaded_file in enumerate(uploaded_files):
            status.text(f"Extraction de {uploaded_file.name}...")
            text = extract_text_from_pdf(uploaded_file)
            email = extract_email(text)
            name = extract_name_from_filename(uploaded_file.name)
            pdf_bytes = uploaded_file.getvalue()

            candidates.append({
                "name": name,
                "email": email,
                "text": text,
                "filename": uploaded_file.name,
                "pdf_bytes": pdf_bytes
            })
            progress.progress((i + 1) / len(uploaded_files))

        # --- Etape 2 : Scoring Hybride (cosinus + LLM reranker) ---
        status.text("Initialisation du LLM...")
        llm = Ollama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=OLLAMA_TEMPERATURE,
            num_ctx=OLLAMA_NUM_CTX,
        )

        status.text("Scoring hybride en cours (embeddings + reranking LLM)...")
        ranked = score_candidates(job_description, candidates, top_n, llm=llm)

        # --- Etape 3 : Synthese finale par le LLM ---
        # On utilise les resultats structures du reranker (evidence, warnings)
        # au lieu de renvoyer le CV brut. Cela evite de depasser le num_ctx
        # et elimine la confusion entre candidats.
        status.text("Generation de la synthese finale...")

        candidates_summary = ""
        for i, c in enumerate(ranked):
            score_pct = int(c["score"] * 100)
            cosine_pct = int(c.get("score_cosine", 0) * 100)
            llm_pct = int(c.get("score_llm", 0) * 100)

            # Scores detailles du reranker
            details = c.get("llm_details", {})
            details_str = ""
            for key, label in [("adequation_metier", "Adequation Metier"),
                               ("hard_skills", "Hard Skills"),
                               ("experience_pertinente", "Experience")]:
                d = details.get(key, {})
                if isinstance(d, dict):
                    details_str += f"  - {label}: {d.get('score', 0)}/100 — {d.get('justification', 'N/A')}\n"

            # Warnings du reranker
            warnings_str = ""
            for w in c.get("warnings", []):
                warnings_str += f"  - {w}\n"

            candidates_summary += (
                f"\n--- {c['name']} (Hybride: {score_pct}% | Cosinus: {cosine_pct}% | LLM: {llm_pct}%) ---\n"
                f"Evaluation detaillee :\n{details_str}"
                f"Points de vigilance :\n{warnings_str if warnings_str else '  - Aucun\n'}"
            )

        llm_prompt = f"""Tu es un expert en recrutement. Voici les resultats d'evaluation de candidats pour un poste.

POSTE : {job_description}

RESULTATS :
{candidates_summary}
Redige une synthese concise pour le recruteur. Pour chaque candidat, explique en 2-3 phrases si le profil correspond et pourquoi. Termine par une recommandation globale."""

        llm_analysis = llm.invoke(llm_prompt)

        st.session_state.review_candidates = ranked
        st.session_state.review_analysis = llm_analysis

        progress.empty()
        status.empty()
        st.rerun()

    # === RESULTATS ===
    if "review_candidates" in st.session_state and "review_analysis" in st.session_state:

        st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

        # Classement Hybride
        st.markdown('<div class="section-title">Classement Hybride</div>', unsafe_allow_html=True)
        st.markdown("")

        recap_data = []
        for c in st.session_state.review_candidates:
            score_pct = int(c["score"] * 100)
            cosine_pct = int(c.get("score_cosine", 0) * 100)
            llm_pct = int(c.get("score_llm", 0) * 100)
            if score_pct >= 70:
                indicator = "🟢"
            elif score_pct >= 50:
                indicator = "🟡"
            else:
                indicator = "🔴"
            recap_data.append({
                "": indicator,
                "Candidat": c["name"],
                "Hybride": f"{score_pct}%",
                "Cosinus": f"{cosine_pct}%",
                "LLM": f"{llm_pct}%",
                "Email": c["email"] if c["email"] else "N/A"
            })

        st.table(recap_data)

        # Detail par candidat : preuves et vigilance
        for c in st.session_state.review_candidates:
            score_pct = int(c["score"] * 100)
            score_class = get_score_class(score_pct)

            with st.expander(f"{c['name']} — Score Hybride : {score_pct}%"):
                # Scores detailles
                details = c.get("llm_details", {})
                if details:
                    cols = st.columns(3)
                    labels = {
                        "adequation_metier": "Adequation Metier",
                        "hard_skills": "Hard Skills",
                        "experience_pertinente": "Experience",
                    }
                    for i, (key, label) in enumerate(labels.items()):
                        with cols[i]:
                            detail = details.get(key, {})
                            detail_score = detail.get("score", 0) if isinstance(detail, dict) else 0
                            st.metric(label, f"{detail_score}/100")

                # Preuves trouvees
                evidence = c.get("evidence", [])
                if evidence:
                    st.markdown("**Preuves trouvees :**")
                    for e in evidence:
                        st.markdown(f"- {e}")

                # Points de vigilance
                warnings = c.get("warnings", [])
                if warnings:
                    st.markdown("**Points de vigilance :**")
                    for w in warnings:
                        st.warning(w)

        # Synthese LLM
        st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="llm-card">
            <div class="llm-label">Synthese du LLM</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(st.session_state.review_analysis)

        st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
        st.info("Passez en mode **CVs & Contact** pour consulter les CVs et contacter les candidats.")

        if st.button("Nouvelle analyse", use_container_width=True):
            for key in ["review_candidates", "review_analysis", "review_index"]:
                st.session_state.pop(key, None)
            st.rerun()


# ============================================================
# MODE CVS & CONTACT
# ============================================================

elif mode == "CVs & Contact":

    if "review_candidates" not in st.session_state:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📄</div>
            <div class="empty-title">Aucun candidat selectionne</div>
            <div class="empty-desc">Lancez d'abord une analyse dans le mode Analyse<br>pour voir les CVs ici.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        candidates = st.session_state.review_candidates
        if "review_index" not in st.session_state:
            st.session_state.review_index = 0

        idx = st.session_state.review_index
        total = len(candidates)
        current = candidates[idx]
        score_pct = int(current["score"] * 100)
        score_class = get_score_class(score_pct)

        # Header
        st.markdown(f"""
        <div class="app-header">
            <h1>CVs selectionnes</h1>
            <div class="subtitle">Candidat {idx + 1} sur {total}</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        col_prev, col_info, col_next = st.columns([1, 3, 1])

        with col_prev:
            if st.button("< Precedent", use_container_width=True, disabled=(idx == 0)):
                st.session_state.review_index = idx - 1
                st.rerun()

        with col_info:
            st.markdown(
                f"<div class='nav-header'>"
                f"<span class='name'>{current['name']}</span>"
                f" &nbsp; <span class='score-badge {score_class}'>{score_pct}%</span>"
                f"</div>",
                unsafe_allow_html=True
            )

        with col_next:
            if st.button("Suivant >", use_container_width=True, disabled=(idx >= total - 1)):
                st.session_state.review_index = idx + 1
                st.rerun()

        # Infos candidat - Grid
        email_display = current['email'] if current['email'] else '<span style="color:rgba(255,255,255,0.2);">Non trouve</span>'
        st.markdown(f"""
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Email</div>
                <div class="info-value">{email_display}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Fichier</div>
                <div class="info-value">{current['filename']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # PDF
        if "pdf_bytes" in current and current["pdf_bytes"]:
            st.markdown('<div class="section-label">Apercu du CV</div>', unsafe_allow_html=True)
            import base64
            pdf_b64 = base64.b64encode(current["pdf_bytes"]).decode()
            st.markdown(
                f'<div class="pdf-frame">'
                f'<iframe src="data:application/pdf;base64,{pdf_b64}" '
                f'width="100%" height="600" type="application/pdf"></iframe>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            with st.expander("Apercu du CV (texte)"):
                st.text(current["text"][:3000])

        # Contact
        st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Contacter les candidats</div>', unsafe_allow_html=True)
        st.markdown("")

        emails_found = [c["email"] for c in candidates if c["email"]]

        if emails_found:
            mailto_link = build_mailto_link(emails_found, EMAIL_SUBJECT, EMAIL_BODY)
            st.link_button(
                f"Contacter les {len(emails_found)} candidat(s) retenus",
                url=mailto_link,
                use_container_width=True
            )
            st.caption(f"Emails en BCC : {', '.join(emails_found)}")
        else:
            st.warning("Aucun email trouve dans les CVs.")
