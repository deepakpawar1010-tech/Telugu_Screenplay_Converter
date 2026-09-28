# -*- coding: utf-8 -*-
"""
Telugu Screenplay Converter - Modern Streamlit Studio
Translates screenplays into Tollywood industry-standard format with Telugu script action and dialogues.
Features sidebar navigation, cinematic theme, 50:50 live editor, batch file converter, and pre-loaded demo.
"""

import os
import io
import time
from typing import List, Tuple
import streamlit as st
from dotenv import load_dotenv

# Project modules
from screenplay_parser import parse_screenplay_text, BlockType, ScreenplayBlock
from translator import convert_block, translate_action
from transliterator import transliterate_dialogue, transliterate_parenthetical
from quality_checker import ScreenplayQualityChecker
from extractor import extract_screenplay_blocks, extract_text_from_docx, extract_text_from_pdf
from formatter import create_screenplay_docx, save_screenplay_docx

# Page configuration
st.set_page_config(
    page_title="Tollywood Screenplay Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Cinematic CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@300;400;500;600;700&family=Noto+Sans+Telugu:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global reset and backgrounds */
    .stApp {
        background-color: #0B0F19;
        color: #F1F5F9;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1F2937;
    }
    
    .sidebar-brand {
        padding: 10px 0 18px 0;
        border-bottom: 1px solid #1F2937;
        margin-bottom: 20px;
    }
    .brand-title {
        font-family: 'Cinzel', serif;
        font-size: 1.45rem;
        font-weight: 800;
        background: linear-gradient(135deg, #F59E0B 0%, #F97316 50%, #EF4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }
    .brand-subtitle {
        font-size: 0.78rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 2px;
    }

    /* Studio Header */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 14px;
        margin-bottom: 18px;
        border-bottom: 1px solid #1F2937;
    }
    .studio-title {
        font-family: 'Cinzel', serif;
        font-size: 1.85rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: 0.5px;
    }
    .studio-badge {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(239, 68, 68, 0.15));
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #FBBF24;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Screenplay Paper - Midnight Mode (Default) */
    .screenplay-paper-dark {
        background: #0D1117;
        border: 1px solid #21262D;
        border-radius: 8px;
        padding: 28px 34px;
        font-family: 'Nirmala UI', 'Noto Sans Telugu', monospace;
        line-height: 1.65;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
        min-height: 480px;
        color: #E6EDF3;
    }

    /* Screenplay Paper - Classic Manuscript Mode */
    .screenplay-paper-light {
        background: #FAF7F2;
        border: 1px solid #E5E0D8;
        border-radius: 8px;
        padding: 28px 34px;
        font-family: 'Nirmala UI', 'Noto Sans Telugu', monospace;
        line-height: 1.65;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
        min-height: 480px;
        color: #1F2937;
    }

    /* Elements - Dark */
    .screenplay-paper-dark .sc-heading {
        color: #F59E0B;
        font-weight: 700;
        font-size: 1.05rem;
        text-transform: uppercase;
        margin-top: 16px;
        margin-bottom: 6px;
        letter-spacing: 0.8px;
    }
    .screenplay-paper-dark .sc-action {
        color: #D1D5DB;
        font-size: 1.0rem;
        margin-bottom: 12px;
        line-height: 1.65;
    }
    .screenplay-paper-dark .sc-character {
        color: #38BDF8;
        font-weight: 700;
        font-size: 1.02rem;
        margin-left: 28%;
        margin-top: 14px;
        margin-bottom: 2px;
        letter-spacing: 0.8px;
    }
    .screenplay-paper-dark .sc-parenthetical {
        color: #94A3B8;
        font-style: italic;
        font-size: 0.94rem;
        margin-left: 22%;
        margin-bottom: 3px;
    }
    .screenplay-paper-dark .sc-dialogue {
        color: #FFFFFF;
        font-size: 1.05rem;
        margin-left: 14%;
        margin-right: 14%;
        margin-bottom: 14px;
        line-height: 1.65;
    }
    .screenplay-paper-dark .sc-command {
        color: #F43F5E;
        font-weight: 700;
        text-align: right;
        font-size: 0.98rem;
        margin-top: 14px;
        margin-bottom: 14px;
        letter-spacing: 0.8px;
    }

    /* Elements - Light */
    .screenplay-paper-light .sc-heading {
        color: #991B1B;
        font-weight: 700;
        font-size: 1.05rem;
        text-transform: uppercase;
        margin-top: 16px;
        margin-bottom: 6px;
        letter-spacing: 0.8px;
    }
    .screenplay-paper-light .sc-action {
        color: #1F2937;
        font-size: 1.0rem;
        margin-bottom: 12px;
        line-height: 1.65;
    }
    .screenplay-paper-light .sc-character {
        color: #0369A1;
        font-weight: 700;
        font-size: 1.02rem;
        margin-left: 28%;
        margin-top: 14px;
        margin-bottom: 2px;
        letter-spacing: 0.8px;
    }
    .screenplay-paper-light .sc-parenthetical {
        color: #6B7280;
        font-style: italic;
        font-size: 0.94rem;
        margin-left: 22%;
        margin-bottom: 3px;
    }
    .screenplay-paper-light .sc-dialogue {
        color: #111827;
        font-size: 1.05rem;
        margin-left: 14%;
        margin-right: 14%;
        margin-bottom: 14px;
        line-height: 1.65;
    }
    .screenplay-paper-light .sc-command {
        color: #BE123C;
        font-weight: 700;
        text-align: right;
        font-size: 0.98rem;
        margin-top: 14px;
        margin-bottom: 14px;
        letter-spacing: 0.8px;
    }

    /* Toolbar chip buttons */
    .stButton > button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton > button:hover {
        border-color: #F59E0B !important;
        color: #F59E0B !important;
        transform: translateY(-1px);
    }

    /* Primary button gradient */
    button[kind="primary"] {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
        border: none !important;
        color: #000000 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.3) !important;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%) !important;
        color: #000000 !important;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.45) !important;
    }

    /* Radio button custom styling in sidebar */
    div[data-testid="stRadio"] > div {
        gap: 6px;
    }
    div[data-testid="stRadio"] label {
        background: #1F2937;
        border: 1px solid #374151;
        padding: 10px 14px;
        border-radius: 8px;
        cursor: pointer;
        width: 100%;
        transition: all 0.2s;
    }
    div[data-testid="stRadio"] label:hover {
        border-color: #F59E0B;
        background: #273549;
    }

    /* Stats card styling */
    .stat-card {
        background: #161F30;
        border: 1px solid #233047;
        padding: 14px 16px;
        border-radius: 8px;
        text-align: center;
    }
    .stat-val {
        font-size: 1.4rem;
        font-weight: 700;
        color: #F59E0B;
    }
    .stat-lbl {
        font-size: 0.75rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "api_key" not in st.session_state:
    project_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(project_dir, ".env"))
    st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

if "live_english" not in st.session_state:
    st.session_state.live_english = (
        "SCENE 2: EXT. HIGHWAY DHABA - MORNING (PROLOGUE)\n\n"
        "Dense fog covers the highway. A motorcycle cuts through the mist and stops at a roadside dhaba.\n\n"
        "SATYA:\n"
        "(In Hindi)\n"
        "Em chepali veediki... TU SUNDAR... MANCHODIVI... AACHA... TEA ICHAV!\n\n"
        "PARTHA:\n"
        "(In Punjabi)\n"
        "Khush kar dita paaji? Kithon aajya rahe ho?\n\n"
        "FADE OUT."
    )

if "live_converted" not in st.session_state:
    st.session_state.live_converted = []

if "paper_theme" not in st.session_state:
    st.session_state.paper_theme = "Dark Obsidian"


def render_html_screenplay(blocks_with_text: List[Tuple[ScreenplayBlock, str]], is_light: bool = False) -> str:
    """Renders parsed and converted blocks into styled screenplay HTML."""
    theme_class = "screenplay-paper-light" if is_light else "screenplay-paper-dark"
    placeholder_color = "#9CA3AF" if is_light else "#6B7280"

    if not blocks_with_text:
        return f"""
        <div class='{theme_class}' style='display:flex;flex-direction:column;align-items:center;justify-content:center;color:{placeholder_color};text-align:center;'>
            <div style='font-size:2.5rem;margin-bottom:10px;'>🎬</div>
            <div style='font-size:1.1rem;font-weight:600;'>Your Converted Tollywood Script Appears Here</div>
            <div style='font-size:0.85rem;margin-top:6px;'>Click 'Translate Screenplay to Telugu' on the left to see live output</div>
        </div>
        """

    html = [f"<div class='{theme_class}'>"]
    for block, text in blocks_with_text:
        clean = text.strip()
        if not clean:
            continue
        if block.type == BlockType.SCENE_HEADING:
            html.append(f"<div class='sc-heading'>{clean}</div>")
        elif block.type == BlockType.ACTION:
            html.append(f"<div class='sc-action'>{clean}</div>")
        elif block.type == BlockType.CHARACTER:
            html.append(f"<div class='sc-character'>{clean}</div>")
        elif block.type == BlockType.PARENTHETICAL:
            html.append(f"<div class='sc-parenthetical'>{clean}</div>")
        elif block.type == BlockType.DIALOGUE:
            html.append(f"<div class='sc-dialogue'>{clean}</div>")
        elif block.type in (BlockType.SCREENPLAY_COMMAND, BlockType.TRANSITION):
            html.append(f"<div class='sc-command'>{clean}</div>")
        else:
            html.append(f"<div class='sc-action'>{clean}</div>")
    html.append("</div>")
    return "".join(html)


# =====================================================================
# SIDEBAR: Branding, Navigation & Configuration
# =====================================================================
with st.sidebar:
    # Branding
    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-title">🎬 TOLYSCREEN</div>
        <div class="brand-subtitle">Telugu Screenplay Studio</div>
    </div>
    """, unsafe_allow_html=True)

    # Primary Navigation (Moved to Sidebar per user request)
    st.markdown("### 🧭 NAVIGATION")
    nav_option = st.radio(
        "Select Studio Workspace:",
        options=[
            "⚡ 50:50 Live Split Screenwriter",
            "📁 Upload & Convert Script (.docx / .pdf)",
            "📖 Pre-Loaded Script Demo"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚙️ ENGINE SETTINGS")

    # Paper Theme Switcher
    theme_choice = st.selectbox(
        "Screenplay Paper Theme:",
        options=["Dark Obsidian (Cinema)", "Classic Ivory (Manuscript)"],
        index=0
    )
    is_light_mode = (theme_choice == "Classic Ivory (Manuscript)")

    # API Status
    if st.session_state.api_key:
        st.success("🟢 Gemini API: Active (.env)")
    else:
        st.warning("🟡 Gemini API: Key Required")

    with st.expander("🔑 API Key & Model Settings"):
        user_key = st.text_input(
            "Gemini API Key:",
            value=st.session_state.api_key,
            type="password",
            help="Loaded securely from .env. You can optionally override it here."
        )
        if user_key != st.session_state.api_key:
            st.session_state.api_key = user_key

        model_choice = st.selectbox(
            "Gemini Model:",
            options=[
                "gemini-flash-lite-latest",
                "gemini-3.5-flash-lite",
                "gemini-3.1-flash-lite",
                "gemini-flash-latest"
            ],
            index=0,
            help="High-speed model configured for Tollywood screenwriting."
        )

    # Screenplay Convention Reference
    with st.expander("📜 Tollywood Formatting Standards"):
        st.markdown("""
        - **Scene Headings**: UPPERCASE English (`EXT. LOCATION - DAY`)
        - **Character Headers**: UPPERCASE English (`SATYA:`)
        - **Action**: Cinematic Telugu prose
        - **Dialogue**: Telugu Unicode script
        - **Other Languages**: Phonetic Telugu script
        - **Layout**: 1.4" Left Margin, Nirmala UI Font
        """)

    st.caption("Tollywood Screenplay Studio v2.0")


# Header Banner
st.markdown("""
<div class="header-container">
    <div>
        <div class="studio-title">TOLYWOOD SCREENPLAY STUDIO</div>
        <div style="font-size:0.88rem;color:#94A3B8;margin-top:2px;">Automated Telugu Cinema Screenplay Translation & Layout Engine</div>
    </div>
    <div>
        <span class="studio-badge">NIRMALA UI • 1.4" BINDING MARGIN</span>
    </div>
</div>
""", unsafe_allow_html=True)


# =====================================================================
# VIEW 1: 50:50 Live Split Screenwriter
# =====================================================================
if nav_option == "⚡ 50:50 Live Split Screenwriter":
    st.markdown("##### ⚡ 50:50 Real-Time Screenplay Studio")
    st.caption("Type or paste your English / Roman-script screenplay on the left. The engine converts it into standard Tollywood Telugu on the right.")

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("**📝 English Screenplay Input**")

        # Snippet Toolbar
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        if t_col1.button("➕ Scene Heading"):
            st.session_state.live_english += "\n\nEXT. LOCATION - DAY\n"
        if t_col2.button("➕ Action Line"):
            st.session_state.live_english += "\n\nThe hero steps into the room.\n"
        if t_col3.button("➕ Dialogue"):
            st.session_state.live_english += "\n\nHERO:\n(Smiles)\nNenu cheppinatte jarigindhi kada!\n"
        if t_col4.button("➕ Transition"):
            st.session_state.live_english += "\n\nCUT TO:\n"

        input_text = st.text_area(
            "Screenplay Editor",
            value=st.session_state.live_english,
            height=490,
            label_visibility="collapsed"
        )
        st.session_state.live_english = input_text

        btn_translate = st.button("🚀 Translate Screenplay to Telugu", type="primary", use_container_width=True)

    with col_right:
        st.markdown("**🇮🇳 Formatted Tollywood Screenplay (Telugu Output)**")

        if btn_translate:
            if not st.session_state.api_key:
                st.error("Please configure your Gemini API Key in the sidebar.")
            else:
                from google import genai
                client = genai.Client(api_key=st.session_state.api_key)

                blocks = parse_screenplay_text(st.session_state.live_english)
                progress_bar = st.progress(0, text="Analyzing and converting screenplay elements...")

                converted_list = []
                total = len(blocks)
                for idx, b in enumerate(blocks):
                    progress_bar.progress((idx + 1) / total, text=f"Converting #{idx+1}/{total}: {b.type.value}...")
                    c_text = convert_block(b, client=client, model_name=model_choice)
                    converted_list.append((b, c_text))

                progress_bar.empty()
                st.session_state.live_converted = converted_list
                st.success(f"Conversion complete! Converted {len(converted_list)} blocks.")

        # Render preview
        html_view = render_html_screenplay(st.session_state.live_converted, is_light=is_light_mode)
        st.markdown(html_view, unsafe_allow_html=True)

        # Download Actions
        if st.session_state.live_converted:
            st.markdown("<br>", unsafe_allow_html=True)
            d_col1, d_col2 = st.columns(2)

            docx_buffer = io.BytesIO()
            save_screenplay_docx(st.session_state.live_converted, docx_buffer, title="Tollywood Telugu Screenplay")
            docx_buffer.seek(0)

            d_col1.download_button(
                label="📥 Download Formatted .DOCX",
                data=docx_buffer,
                file_name="Telugu_Screenplay.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )

            plain_lines = [f"{t}" for b, t in st.session_state.live_converted]
            full_plain = "\n\n".join(plain_lines)
            d_col2.download_button(
                label="📄 Download Plain Text",
                data=full_plain.encode("utf-8"),
                file_name="Telugu_Screenplay.txt",
                mime="text/plain",
                use_container_width=True
            )


# =====================================================================
# VIEW 2: Upload & Convert Script File
# =====================================================================
elif nav_option == "📁 Upload & Convert Script (.docx / .pdf)":
    st.markdown("##### 📁 Full Screenplay Document Ingestion & Translation")
    st.caption("Upload your script file (.docx, .pdf, or .txt). The engine automatically detects scenes, characters, and dialogues, translating them into standard Tollywood format.")

    uploaded_file = st.file_uploader(
        "Drag and drop your screenplay file here:",
        type=["docx", "pdf", "txt"],
        help="Supports industry-standard DOCX and PDF screenplay documents."
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_ext = uploaded_file.name.split(".")[-1].lower()

        st.info(f"Loaded **{uploaded_file.name}** ({len(file_bytes):,} bytes)")

        # Extract blocks
        blocks = extract_screenplay_blocks(file_bytes, file_type=file_ext)

        # Breakdown Metrics
        type_counts = {}
        for b in blocks:
            type_counts[b.type.value] = type_counts.get(b.type.value, 0) + 1

        st.markdown("###### 📊 Screenplay Elements Breakdown")
        stat_cols = st.columns(len(type_counts))
        for i, (k, v) in enumerate(type_counts.items()):
            stat_cols[i].markdown(f"""
            <div class="stat-card">
                <div class="stat-val">{v}</div>
                <div class="stat-lbl">{k}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        start_batch = st.button("🚀 Start Full Script Conversion to Telugu", type="primary", use_container_width=True)

        if start_batch:
            if not st.session_state.api_key:
                st.error("Please configure your Gemini API Key in the sidebar.")
            else:
                from google import genai
                client = genai.Client(api_key=st.session_state.api_key)

                progress_bar = st.progress(0, text="Translating screenplay blocks...")
                status_placeholder = st.empty()

                converted_results = []
                total = len(blocks)
                start_time = time.time()

                for idx, b in enumerate(blocks):
                    progress_pct = (idx + 1) / total
                    status_placeholder.markdown(f"**Converting element {idx+1}/{total}**: `{b.type.value}` - *{b.text[:50]}...*")
                    progress_bar.progress(progress_pct)

                    c_text = convert_block(b, client=client, model_name=model_choice)
                    converted_results.append((b, c_text))

                elapsed = time.time() - start_time
                progress_bar.empty()
                status_placeholder.empty()
                st.success(f"Screenplay converted successfully! {len(converted_results)} blocks in {elapsed:.1f}s.")

                # Inspection Table
                st.markdown("#### 🔍 Converted Script Inspection")
                preview_data = []
                for idx, (b, c_text) in enumerate(converted_results, 1):
                    preview_data.append({
                        "#": idx,
                        "Type": b.type.value,
                        "Original English/Roman": b.text,
                        "Tollywood Telugu Result": c_text
                    })
                st.dataframe(preview_data, use_container_width=True)

                # Export DOCX
                doc_buf = io.BytesIO()
                save_screenplay_docx(converted_results, doc_buf, title=uploaded_file.name)
                doc_buf.seek(0)

                clean_name = uploaded_file.name.rsplit('.', 1)[0]
                st.download_button(
                    label=f"📥 Download Formatted {clean_name}_Telugu.docx",
                    data=doc_buf,
                    file_name=f"{clean_name}_Telugu.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )


# =====================================================================
# VIEW 3: Pre-Loaded Script Demo (Prema Parichayam)
# =====================================================================
elif nav_option == "📖 Pre-Loaded Script Demo":
    st.markdown("##### 📖 Reference Conversion: *Prema Parichayam* Prologue")
    st.caption("Verified standard output demonstrating English sluglines and character cues with natural cinematic Telugu action and Punjabi-to-Telugu transliteration.")

    demo_blocks_text = [
        (ScreenplayBlock(BlockType.SCENE_HEADING, "SCENE 2: EXT. HIGHWAY DHABA - MORNING (PROLOGUE)"), "SCENE 2: EXT. HIGHWAY DHABA - MORNING (PROLOGUE)"),
        (ScreenplayBlock(BlockType.ACTION, "Dense fog covers the highway. A motorcycle cuts through the mist and stops at a roadside dhaba."), "దట్టమైన పొగమంచు హైవేను కమ్మేసింది. పొగమంచును చీల్చుకుంటూ ఒక మోటార్‌సైకిల్ దూసుకొచ్చి రోడ్డు పక్కనే ఉన్న ధాబా దగ్గర ఆగుతుంది."),
        (ScreenplayBlock(BlockType.ACTION, "SATYA (45), rugged in a heavy biker jacket and full travel gear, gets off the bike with a travel bag strapped to his back."), "సత్య (వయసు 45). బరువైన బైకర్ జాకెట్, పూర్తి ట్రావెల్ గేర్‌తో రఫ్‌గా కనిపిస్తాడు. వీపుకు ట్రావెల్ బ్యాగ్ తగిలించుకుని బైక్ దిగుతాడు."),
        (ScreenplayBlock(BlockType.CHARACTER, "SATYA:"), "SATYA:"),
        (ScreenplayBlock(BlockType.PARENTHETICAL, "(In Hindi)"), "(హిందీలో)"),
        (ScreenplayBlock(BlockType.DIALOGUE, "Em chepali veediki... TU SUNDAR... MANCHODIVI... AACHA... TEA ICHAV!"), "ఏం చెప్పాలి వీడికి... తు సుందర్... మంచోదివి... ఆచా... టీ ఇచావ్!"),
        (ScreenplayBlock(BlockType.CHARACTER, "PARTHA:"), "PARTHA:"),
        (ScreenplayBlock(BlockType.PARENTHETICAL, "(In Punjabi)"), "(పంజాబీలో)"),
        (ScreenplayBlock(BlockType.DIALOGUE, "Khush kar dita paaji? Kithon aajya rahe ho?"), "ఖుష్ కర్ దితా పాజీ? కిత్థోం ఆజ్యా రహే హో?"),
        (ScreenplayBlock(BlockType.SCREENPLAY_COMMAND, "FADE OUT."), "FADE OUT.")
    ]

    demo_html = render_html_screenplay(demo_blocks_text, is_light=is_light_mode)
    st.markdown(demo_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    buf = io.BytesIO()
    save_screenplay_docx(demo_blocks_text, buf, title="Prema Parichayam Prologue")
    buf.seek(0)

    st.download_button(
        label="📥 Download Reference Prema Parichayam Prologue (.DOCX)",
        data=buf,
        file_name="Prema_Parichayam_Telugu_Prologue.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        use_container_width=True
    )
