import os
import sys
import json
import base64
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BIS Standards Finder — Building Materials",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main { background: #0d1117; }

  .hero {
    background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 60%, #1a1f2e 100%);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 2.5rem 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
  }
  .hero h1 { color: #f97316; font-size: 2rem; font-weight: 700; margin: 0; }
  .hero p  { color: #8b949e; font-size: 1rem; margin: 0.5rem 0 0; }

  .standard-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
  }
  .standard-card:hover { border-color: #f97316; }

  .card-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.6rem;
  }
  .rank-badge {
    background: #f97316;
    color: #fff;
    border-radius: 50%;
    width: 28px; height: 28px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85rem; flex-shrink: 0;
  }
  .std-number { color: #58a6ff; font-weight: 600; font-size: 1rem; }
  .std-title  { color: #e6edf3; font-size: 0.95rem; }

  .category-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }
  .cat-cement    { background: #1a3a4a; color: #56b4d3; }
  .cat-steel     { background: #2a1f3a; color: #b98fff; }
  .cat-concrete  { background: #1a3a2a; color: #56d38a; }
  .cat-aggregates{ background: #3a2a1a; color: #d38a56; }
  .cat-masonry   { background: #3a1a1a; color: #d35656; }
  .cat-general   { background: #1a1a3a; color: #5672d3; }

  .rationale-box {
    background: #0d1117;
    border-left: 3px solid #f97316;
    padding: 0.7rem 1rem;
    border-radius: 0 8px 8px 0;
    color: #c9d1d9;
    font-size: 0.88rem;
    margin: 0.6rem 0;
  }
  .key-req {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 0.5rem 0.8rem;
    color: #8b949e;
    font-size: 0.82rem;
    font-family: monospace;
  }
  .score-chip {
    background: #21262d;
    color: #3fb950;
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 12px;
    font-weight: 500;
  }
  .section-label {
    color: #8b949e;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
  }

  div[data-testid="stExpander"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
  }

  div.stButton > button {
    background: linear-gradient(90deg, #f97316, #ea580c);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.5rem;
    font-size: 0.95rem;
  }
  div.stButton > button:hover {
    background: linear-gradient(90deg, #ea580c, #c2410c);
  }

  textarea, input[type="text"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
  }

  .sidebar-logo { font-size: 1.5rem; font-weight: 700; color: #f97316; }
  .sidebar-sub  { color: #8b949e; font-size: 0.8rem; margin-top: -4px; }
</style>
""", unsafe_allow_html=True)

# ─── Load secrets/env ────────────────────────────────────────────────────────
def _set_env(key: str, st_key: str):
    val = st.secrets.get(st_key, "") if hasattr(st, "secrets") else ""
    if val:
        os.environ[key] = val

_set_env("DATABRICKS_TOKEN", "DATABRICKS_TOKEN")
_set_env("SARVAM_API_KEY", "SARVAM_API_KEY")

# Allow runtime key entry (overrides secrets if provided)
if "databricks_token" not in st.session_state:
    st.session_state.databricks_token = os.environ.get("DATABRICKS_TOKEN", "")
if "sarvam_key" not in st.session_state:
    st.session_state.sarvam_key = os.environ.get("SARVAM_API_KEY", "")

# Persist search results and TTS audio across reruns
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "search_lang" not in st.session_state:
    st.session_state.search_lang = "English"
if "tts_audio" not in st.session_state:
    st.session_state.tts_audio = None
if "tts_error" not in st.session_state:
    st.session_state.tts_error = ""

# ─── Imports (after env setup) ───────────────────────────────────────────────
from src.rag_pipeline import get_pipeline
from src.translator import (
    translate_to_english, translate_from_english,
    speech_to_text, text_to_speech, LANGUAGE_CODES,
)

LANGUAGES = list(LANGUAGE_CODES.keys())

CATEGORY_CSS = {
    "Cement": "cat-cement",
    "Steel": "cat-steel",
    "Concrete": "cat-concrete",
    "Aggregates": "cat-aggregates",
    "Masonry": "cat-masonry",
}


def category_css(cat: str) -> str:
    return CATEGORY_CSS.get(cat, "cat-general")


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🏗️ BIS Finder</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">BIS Standards Discovery — Building Materials</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("**API Keys**")
    db_token = st.text_input(
        "Databricks Token",
        value=st.session_state.databricks_token,
        type="password",
        placeholder="dapi…",
        help="Required for AI-generated rationale. Get from Databricks workspace.",
    )
    if db_token:
        st.session_state.databricks_token = db_token
        os.environ["DATABRICKS_TOKEN"] = db_token

    sarvam_key = st.text_input(
        "Sarvam AI API Key",
        value=st.session_state.sarvam_key,
        type="password",
        placeholder="sk-…",
        help="Required for translation, voice input, and voice output.",
    )
    if sarvam_key:
        st.session_state.sarvam_key = sarvam_key
        os.environ["SARVAM_API_KEY"] = sarvam_key

    st.divider()
    lang = st.selectbox("🌐 Language / भाषा", LANGUAGES, index=0)
    top_k = st.slider("Number of Standards", min_value=3, max_value=5, value=3)

    st.divider()
    st.markdown("**About**")
    st.caption(
        "AI-powered RAG system that maps product descriptions to "
        "relevant Bureau of Indian Standards (BIS) for building materials. "
        "Covers 25+ categories including Cement, Steel, Plastics, Glass, and more."
    )


# ─── Hero ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🏗️ BIS Standards Recommendation Engine</h1>
  <p>Describe your building material or product — get the top applicable BIS standards with rationale in seconds</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 Find Standards", "📚 About BIS"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FIND STANDARDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_input, col_results = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown("#### Describe Your Product")

        input_mode = st.radio("Input mode", ["✍️ Type", "🎙️ Voice"], horizontal=True, label_visibility="collapsed")

        product_description = ""

        if input_mode == "✍️ Type":
            placeholder = {
                "English": "e.g. 43 grade cement for a multi-storey reinforced concrete building",
                "Hindi": "उदाहरण: बहुमंजिली प्रबलित कंक्रीट इमारत के लिए 43 ग्रेड सीमेंट",
            }.get(lang, "Describe your product or building material...")

            user_text = st.text_area(
                "Product description",
                placeholder=placeholder,
                height=120,
                label_visibility="collapsed",
            )
            product_description = user_text.strip()

        else:
            st.info("🎙️ Record your voice query below. Requires Sarvam AI API key.")
            try:
                from audio_recorder_streamlit import audio_recorder
                audio_bytes = audio_recorder(
                    text="Click to record",
                    recording_color="#f97316",
                    neutral_color="#30363d",
                    icon_size="2x",
                )
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/wav")
                    with st.spinner("Transcribing…"):
                        transcript = speech_to_text(audio_bytes, lang)
                    if transcript:
                        st.success(f"Transcribed: **{transcript}**")
                        product_description = transcript
                    else:
                        st.warning("Could not transcribe. Check your Sarvam AI key.")
            except ImportError:
                st.warning("Install `audio-recorder-streamlit` to enable voice input.")

        st.markdown("")
        search_clicked = st.button("🔍 Find Applicable BIS Standards", use_container_width=True)

        if lang != "English" and product_description:
            with st.expander("🔄 Translation preview"):
                en_text = translate_to_english(product_description, lang)
                st.caption("English query sent to the model:")
                st.code(en_text)
        else:
            en_text = product_description

        # Example queries
        st.markdown("---")
        st.markdown("##### Example Queries")
        examples = [
            "High strength deformed steel bars for RCC columns and beams",
            "Ordinary Portland Cement for plastering and masonry work",
            "Coarse aggregate for M25 concrete mix design",
            "Hollow concrete blocks for non-load bearing partition walls",
            "Fly ash based concrete admixture for mass concrete dam",
            "Structural steel sections for industrial shed",
        ]
        for ex in examples:
            if st.button(ex, key=f"ex_{ex[:20]}", use_container_width=False):
                product_description = ex
                en_text = ex
                search_clicked = True

    with col_results:
        st.markdown("#### Recommended BIS Standards")

        if search_clicked and product_description:
            query_en = en_text if en_text else product_description
            if lang != "English" and not en_text:
                query_en = translate_to_english(product_description, lang)

            with st.spinner("🔎 Retrieving relevant BIS standards…"):
                pipeline = get_pipeline()
                pipeline.top_k = top_k
                output = pipeline.query(query_en)

            # Pre-translate rationales once so reruns don't re-call Sarvam
            for r in output["results"]:
                if lang != "English":
                    r["rationale_display"] = translate_from_english(r["rationale"], lang)
                else:
                    r["rationale_display"] = r["rationale"]

            st.session_state.search_results = output
            st.session_state.search_lang = lang
            st.session_state.tts_audio = None
            st.session_state.tts_error = ""

        elif search_clicked and not product_description:
            st.warning("Please enter a product description.")

        # ── Render from session state (survives TTS button reruns) ──────────
        output = st.session_state.search_results
        render_lang = st.session_state.search_lang

        if output:
            results = output["results"]
            latency = output["latency_seconds"]
            st.caption(f"⚡ {latency}s · Found {len(results)} standards")

            for r in results:
                cat_css = category_css(r["category"])
                rationale = r.get("rationale_display", r["rationale"])
                key_req = r["key_requirement"]

                with st.container():
                    st.markdown(f"""
<div class="standard-card">
  <div class="card-header">
    <div class="rank-badge">{r['rank']}</div>
    <div>
      <div class="std-number">{r['standard_number']}</div>
    </div>
    <span class="score-chip">Score: {r['relevance_score']:.3f}</span>
  </div>
  <span class="category-badge {cat_css}">{r['category']}</span>
  <div class="std-title">{r['title']}</div>
  <div class="rationale-box">💡 {rationale}</div>
  <div class="section-label">Key Requirement</div>
  <div class="key-req">{key_req}</div>
</div>
""", unsafe_allow_html=True)

                    with st.expander(f"More details — {r['standard_number']}"):
                        st.markdown(f"**Description:** {r['description']}")
                        st.markdown(f"**Scope:** {r['scope']}")
                        if r.get("key_requirements"):
                            st.markdown("**Key Requirements:**")
                            for req in r["key_requirements"]:
                                st.markdown(f"- {req}")
                        if r.get("applicable_products"):
                            st.markdown("**Applicable Products:**")
                            for p in r["applicable_products"]:
                                st.markdown(f"- {p}")
                        if r.get("year"):
                            st.caption(f"Year: {r['year']}")

            # ── Voice output — all results, any language ─────────────────
            st.divider()
            if st.button("🔊 Listen to All Results", use_container_width=True):
                tts_parts = []
                for r in results:
                    tts_parts.append(
                        f"Standard {r['rank']}. {r['standard_number']}. "
                        f"{r['title']}. {r.get('rationale_display', r['rationale'])}."
                    )
                tts_text = " ".join(tts_parts)
                with st.spinner("Generating audio…"):
                    audio, err = text_to_speech(tts_text, render_lang)
                if audio:
                    st.session_state.tts_audio = audio
                    st.session_state.tts_error = ""
                else:
                    st.session_state.tts_audio = None
                    st.session_state.tts_error = err

            if st.session_state.tts_audio:
                st.audio(st.session_state.tts_audio, format="audio/wav")
            elif st.session_state.get("tts_error"):
                st.error(f"Audio failed: {st.session_state.tts_error}")

            # Download results
            st.divider()
            dl_data = json.dumps(output, ensure_ascii=False, indent=2)
            st.download_button(
                "⬇️ Download Results (JSON)",
                dl_data,
                file_name="bis_recommendations.json",
                mime="application/json",
                use_container_width=True,
            )

        else:
            st.markdown("""
<div style="text-align:center; color:#484f58; padding: 3rem 0;">
  <div style="font-size:3rem;">🏗️</div>
  <div style="font-size:1rem; margin-top:0.5rem;">Enter a product description and click <strong style="color:#f97316">Find Applicable BIS Standards</strong></div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ABOUT BIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## About BIS Standards for Building Materials")
    st.markdown("""
Bureau of Indian Standards (BIS) is the National Standards Body of India operating under the Ministry of Consumer Affairs.
BIS standards ensure the **quality, safety, and reliability** of building materials used in construction across India.

### Why BIS Compliance Matters for MSEs

Indian Micro and Small Enterprises (MSEs) in the construction materials sector are required to comply with BIS standards:
- **Mandatory certification** for many building materials (cement, steel, etc.) under the BIS Act, 2016
- **Quality assurance** for consumers and contractors
- **Avoiding penalties** for non-compliant products
- **Market access** — many tenders require BIS-certified materials
""")

    st.markdown("### Categories Covered in this System")

    categories_info = {
        "Cement": {
            "icon": "🏭",
            "desc": "OPC 33/43/53 grades, Portland Pozzolana (fly ash & calcined clay), Portland Slag, High Alumina, and Low Heat cements.",
            "standards": ["IS 269", "IS 8112", "IS 12269", "IS 1489", "IS 455", "IS 6452", "IS 12600"],
        },
        "Steel": {
            "icon": "⚙️",
            "desc": "TMT/HYSD reinforcement bars (Fe415 to Fe600), structural steel plates and sections.",
            "standards": ["IS 1786", "IS 432", "IS 2062", "IS 808", "IS 3502"],
        },
        "Concrete": {
            "icon": "🧱",
            "desc": "Code of practice, mix design, admixtures, fly ash, strength testing, and NDT methods.",
            "standards": ["IS 456", "IS 10262", "IS 516", "IS 9103", "IS 3812", "IS 13311"],
        },
        "Aggregates": {
            "icon": "🪨",
            "desc": "Coarse and fine aggregate specifications, particle size, shape, mechanical strength tests.",
            "standards": ["IS 383", "IS 2386 (P1)", "IS 2386 (P3)", "IS 2386 (P4)", "IS 515"],
        },
        "Masonry": {
            "icon": "🏠",
            "desc": "Burnt clay bricks, hollow blocks, concrete blocks, calcium silicate bricks, fly ash bricks.",
            "standards": ["IS 1077", "IS 3952", "IS 2185", "IS 4139", "IS 2212", "IS 12894"],
        },
        "Structural/General": {
            "icon": "📐",
            "desc": "Design loads (dead, imposed, wind), earthquake design, ductile detailing, raft foundations.",
            "standards": ["IS 875 (P1/P2/P3)", "IS 1893", "IS 13920", "IS 2950", "IS 4082"],
        },
    }

    cols = st.columns(2)
    for i, (cat, info) in enumerate(categories_info.items()):
        with cols[i % 2]:
            with st.expander(f"{info['icon']} {cat}"):
                st.markdown(info["desc"])
                st.markdown("**Key Standards:** " + " · ".join(info["standards"]))

    st.markdown("---")
    st.markdown("""
### How the RAG System Works

```
Product Description
       │
       ▼
  ┌─────────────────────┐
  │  Translation Layer   │  (Sarvam AI — 10 Indian languages ↔ English)
  └────────┬────────────┘
           │
           ▼
  ┌─────────────────────┐
  │  Embedding Encoder  │  (sentence-transformers/all-MiniLM-L6-v2)
  └────────┬────────────┘
           │
           ▼
  ┌─────────────────────┐
  │   FAISS Vector DB   │  (Cosine similarity search over 441 BIS standards)
  └────────┬────────────┘
           │
           ▼
  ┌─────────────────────┐
  │   LLM Rationale     │  (Databricks / Llama-3.1-8B-Instruct)
  └────────┬────────────┘
           │
           ▼
  Top 3–5 BIS Standards + Rationale + Key Requirements
```

### Tech Stack
| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Store | FAISS (IndexFlatIP) |
| LLM | Databricks / Llama-3.1-8B-Instruct |
| Translation | Sarvam AI (mayura:v1) — 11 Indian languages |
| ASR (Voice) | Sarvam AI (saarika:v2.5) |
| TTS (Voice) | Sarvam AI (bulbul:v2) |

### Evaluation Metrics
- **Hit Rate @3**: Fraction of queries where the correct standard appears in top-3
- **MRR @5**: Mean Reciprocal Rank across top-5 results
- **Latency**: Average query response time in seconds
""")
