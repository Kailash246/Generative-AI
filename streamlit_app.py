import streamlit as st
import requests
import time
import json
import os
import sys
from pathlib import Path

# Add project directories to sys.path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "local_code_explainer"))

# Page Configuration
st.set_page_config(
    page_title="RepoScope | Codebase Intelligence & Architecture Engine",
    page_icon="none",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Professional Enterprise CSS (Linear / Vercel Developer Aesthetic)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
        -webkit-font-smoothing: antialiased;
    }
    
    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .app-header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 18px;
        margin-bottom: 24px;
    }
    .app-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .app-subtitle {
        font-size: 0.88rem;
        color: #64748B;
        margin-top: 4px;
        font-weight: 400;
    }
    .badge-status {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid;
    }
    .status-online {
        background-color: #F0FDF4;
        color: #166534;
        border-color: #BBF7D0;
    }
    .status-cloud {
        background-color: #EFF6FF;
        color: #1E40AF;
        border-color: #BFDBFE;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .dot-online { background-color: #16A34A; }
    .dot-cloud { background-color: #2563EB; }

    .pipeline-container {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 8px 14px;
        margin-bottom: 24px;
        overflow-x: auto;
    }
    .pipeline-step {
        font-size: 0.78rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .pipeline-arrow {
        color: #94A3B8;
        font-size: 0.75rem;
    }

    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0F172A;
        font-feature-settings: "tnum";
        letter-spacing: -0.02em;
    }
    .metric-label {
        font-size: 0.78rem;
        font-weight: 500;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-top: 2px;
    }

    .report-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 24px;
        margin-top: 10px;
        line-height: 1.65;
    }
    .report-card h3 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0F172A;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 8px;
        margin-top: 20px;
        margin-bottom: 12px;
        letter-spacing: -0.01em;
    }
    .report-card h3:first-child {
        margin-top: 0;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 6px;
        border: 1px solid #CBD5E1;
        font-size: 0.92rem;
        padding: 10px 12px;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #0F172A;
        box-shadow: 0 0 0 1px #0F172A;
    }
    div[data-testid="stButton"] button {
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.88rem;
        padding: 8px 18px;
        letter-spacing: 0.01em;
        border: 1px solid #0F172A;
        background-color: #0F172A;
        color: #FFFFFF;
        transition: all 0.15s ease-in-out;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #1E293B;
        border-color: #1E293B;
        color: #FFFFFF;
    }

    button[data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.88rem;
        color: #64748B;
        padding: 10px 16px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0F172A !important;
        border-bottom-color: #0F172A !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Import Core Engine -----------------
try:
    from backend.repo_processor import RepoProcessor
    from backend.llm_engine import LocalLLMEngine
except ImportError:
    try:
        from local_code_explainer.backend.repo_processor import RepoProcessor
        from local_code_explainer.backend.llm_engine import LocalLLMEngine
    except ImportError:
        RepoProcessor = None
        LocalLLMEngine = None

# Initialize Singletons in Session State
if "repo_processor" not in st.session_state and RepoProcessor is not None:
    st.session_state["repo_processor"] = RepoProcessor()

if "llm_engine" not in st.session_state and LocalLLMEngine is not None:
    st.session_state["llm_engine"] = LocalLLMEngine()

# ----------------- Sidebar Configuration -----------------
st.sidebar.markdown("### Execution Mode")

# Mode: Standalone Direct Engine vs FastAPI Backend
backend_url = st.sidebar.text_input("FastAPI Backend URL", value="http://127.0.0.1:8000")

backend_online = False
health_info = {}
try:
    health_res = requests.get(f"{backend_url}/api/health", timeout=0.8)
    if health_res.status_code == 200:
        backend_online = True
        health_info = health_res.json()
except Exception:
    pass

mode_options = ["Direct Engine (Cloud & Local Standalone)"]
if backend_online:
    mode_options.append("FastAPI Backend Service")

selected_mode = st.sidebar.selectbox("Active Pipeline", options=mode_options)

st.sidebar.markdown("---")
st.sidebar.markdown("### Inference Engine")

supported_models = [
    {"id": "Qwen/Qwen2.5-0.5B-Instruct", "name": "Qwen 2.5 (0.5B Instruct - Fast & Balanced)"},
    {"id": "HuggingFaceTB/SmolLM2-360M-Instruct", "name": "SmolLM2 (360M - Ultra Lightweight)"},
    {"id": "HuggingFaceTB/SmolLM2-135M-Instruct", "name": "SmolLM2 (135M - Maximum Speed)"},
    {"id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "name": "TinyLlama (1.1B Chat)"}
]

model_ids = [m["id"] for m in supported_models]
model_labels = {m["id"]: m["name"] for m in supported_models}
selected_model = st.sidebar.selectbox("Base Model", options=model_ids, format_func=lambda x: model_labels.get(x, x))

temperature = st.sidebar.slider("Sampling Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
max_tokens = st.sidebar.slider("Max Generation Length", min_value=256, max_value=1536, value=550, step=64)

st.sidebar.markdown("---")
st.sidebar.markdown("### System Specs")
device_name = "CPU"
if st.session_state.get("llm_engine"):
    device_name = st.session_state["llm_engine"].device.upper()
st.sidebar.markdown(f"**Execution Device:** `{device_name}`")
st.sidebar.markdown(f"**Runtime State:** `{'FastAPI Connected' if 'FastAPI' in selected_mode else 'Standalone In-Process'}`")

# ----------------- Top Navigation & Header -----------------
status_label = "Service Ready (FastAPI)" if "FastAPI" in selected_mode else "Service Ready (Direct Engine)"
status_class = "status-online" if "FastAPI" in selected_mode else "status-cloud"
dot_class = "dot-online" if "FastAPI" in selected_mode else "dot-cloud"

st.markdown(f"""
<div class="app-header-container">
    <div>
        <h1 class="app-title">Local Repository Code Explainer</h1>
        <div class="app-subtitle">Automated codebase inspection and architectural synthesis running on-premise.</div>
    </div>
    <div>
        <span class="badge-status {status_class}">
            <span class="status-dot {dot_class}"></span>
            {status_label}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Architecture Ribbon
st.markdown("""
<div class="pipeline-container">
    <span class="pipeline-step">Git Ingestion</span>
    <span class="pipeline-arrow">&rarr;</span>
    <span class="pipeline-step">File Filtering &amp; Tree</span>
    <span class="pipeline-arrow">&rarr;</span>
    <span class="pipeline-step">Context Assembly</span>
    <span class="pipeline-arrow">&rarr;</span>
    <span class="pipeline-step">Local LLM Inference</span>
    <span class="pipeline-arrow">&rarr;</span>
    <span class="pipeline-step">Architecture Summary</span>
</div>
""", unsafe_allow_html=True)

# ----------------- Main Input Bar -----------------
if "repo_input" not in st.session_state:
    st.session_state.repo_input = "https://github.com/streamlit/demo-uber-nyc-pickups"

input_col, btn_col = st.columns([4, 1.2])

with input_col:
    repo_url_input = st.text_input(
        "GitHub Repository URL",
        value=st.session_state.repo_input,
        placeholder="https://github.com/organization/repository",
        label_visibility="collapsed"
    )

with btn_col:
    analyze_btn = st.button("Analyze Codebase", use_container_width=True)

# Preset Selectors
st.markdown("<span style='font-size: 0.78rem; font-weight: 600; color: #64748B; text-transform: uppercase;'>Quick Presets:</span>", unsafe_allow_html=True)
p_col1, p_col2, p_col3, p_col4 = st.columns(4)

preset_repos = [
    ("Streamlit Demo", "https://github.com/streamlit/demo-uber-nyc-pickups"),
    ("Developer Portfolio", "https://github.com/Kailash246/kailash-portfolio"),
    ("Flask Framework", "https://github.com/pallets/flask"),
    ("Click CLI Library", "https://github.com/pallets/click")
]

for idx, (label, url) in enumerate(preset_repos):
    col = [p_col1, p_col2, p_col3, p_col4][idx]
    if col.button(label, key=f"preset_{idx}", use_container_width=True):
        st.session_state.repo_input = url
        st.rerun()

# ----------------- Execution Pipeline -----------------
if analyze_btn:
    st.session_state["result"] = None
    if not repo_url_input or "github.com" not in repo_url_input:
        st.error("Please provide a valid GitHub repository URL.")
    else:
        with st.status("Executing repository analysis pipeline...", expanded=True) as status_box:
            st.write("Cloning repository shallowly (depth 1)...")
            st.write("Parsing directory tree and selecting high-priority source files...")
            st.write(f"Executing model inference via {selected_model}...")

            t0 = time.time()

            # Execution Branch 1: FastAPI Backend
            if "FastAPI" in selected_mode and backend_online:
                payload = {
                    "repo_url": repo_url_input,
                    "model_provider": "transformers",
                    "model_name": selected_model,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                try:
                    resp = requests.post(f"{backend_url}/api/explain", json=payload, timeout=300)
                    elapsed = time.time() - t0
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state["result"] = data
                        status_box.update(label=f"Analysis completed in {data.get('processing_time_seconds', elapsed):.2f}s", state="complete", expanded=False)
                    else:
                        st.session_state["result"] = None
                        status_box.update(label="Analysis failed", state="error", expanded=True)
                        st.error(f"Backend error: {resp.text}")
                except Exception as e:
                    status_box.update(label="Execution error", state="error", expanded=True)
                    st.error(f"Request failed: {str(e)}")

            # Execution Branch 2: Direct Standalone Engine (Default for Streamlit Cloud & In-Process)
            else:
                try:
                    processor = st.session_state["repo_processor"]
                    llm = st.session_state["llm_engine"]

                    analysis = processor.analyze_repository(repo_url_input)
                    explanation = llm.generate_explanation(
                        analysis=analysis,
                        provider="transformers",
                        model_name=selected_model,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    elapsed = round(time.time() - t0, 2)

                    result_data = {
                        "status": "success",
                        "repo_name": analysis.repo_name,
                        "repo_url": repo_url_input,
                        "explanation": explanation,
                        "raw_llm_output": explanation,
                        "analysis": analysis.dict() if hasattr(analysis, "dict") else analysis.__dict__,
                        "model_used": selected_model,
                        "provider_used": "transformers (in-process)",
                        "processing_time_seconds": elapsed
                    }
                    st.session_state["result"] = result_data
                    status_box.update(label=f"Analysis completed in {elapsed:.2f}s", state="complete", expanded=False)
                except Exception as e:
                    st.session_state["result"] = None
                    status_box.update(label="Execution error", state="error", expanded=True)
                    st.error(f"Analysis failed: {str(e)}")

# ----------------- Results Dashboard -----------------
if "result" in st.session_state and st.session_state["result"]:
    res = st.session_state["result"]

    if res.get("status") == "error":
        st.error(f"Analysis Failed: {res.get('error') or res.get('explanation')}")
    else:
        analysis = res.get("analysis", {})
        
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        
        # Metric Stats Bar
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{res.get('repo_name', 'N/A')}</div>
                <div class="metric-label">Target Repository</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{analysis.get('source_files_count', 0)}</div>
                <div class="metric-label">Source Files Scanned</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(analysis.get('detected_languages', {}))}</div>
                <div class="metric-label">Detected Languages</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{res.get('processing_time_seconds', 0)}s</div>
                <div class="metric-label">Local Inference Latency</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Tabbed Data Views
        tab_summary, tab_tree, tab_files, tab_diagnostics = st.tabs([
            "Architecture Summary",
            "File Hierarchy",
            "Extracted Source Modules",
            "System Diagnostics"
        ])

        with tab_summary:
            st.markdown("<div class='report-card'>", unsafe_allow_html=True)
            st.markdown(res.get("explanation", "No output returned."))
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.download_button(
                label="Export Specification (.md)",
                data=res.get("explanation", ""),
                file_name=f"{res.get('repo_name', 'repository')}_architecture.md",
                mime="text/markdown"
            )

        with tab_tree:
            st.markdown("#### Directory Structure")
            st.code(analysis.get("file_tree_str", "No directory tree available."), language="text")

            langs = analysis.get("detected_languages", {})
            if langs:
                st.markdown("#### Language Composition")
                st.bar_chart(langs)

        with tab_files:
            st.markdown("#### Source Files Provided to Context Window")
            extracted = analysis.get("extracted_files", [])
            if not extracted:
                st.info("No source files captured.")
            else:
                for f_info in extracted:
                    with st.expander(f"{f_info.get('path')} ({f_info.get('language')} • {f_info.get('line_count')} lines)"):
                        lang_hint = f_info.get("language", "python").lower()
                        if "react" in lang_hint or "javascript" in lang_hint:
                            lang_hint = "javascript"
                        elif "typescript" in lang_hint:
                            lang_hint = "typescript"
                        elif "html" in lang_hint:
                            lang_hint = "html"
                        elif "css" in lang_hint:
                            lang_hint = "css"
                        elif "json" in lang_hint:
                            lang_hint = "json"
                        elif "markdown" in lang_hint:
                            lang_hint = "markdown"
                        else:
                            lang_hint = "python"

                        st.code(f_info.get("content", ""), language=lang_hint)

        with tab_diagnostics:
            st.markdown("#### Execution Metadata")
            st.json({
                "model_identifier": res.get("model_used"),
                "runtime_provider": res.get("provider_used"),
                "inference_time_seconds": res.get("processing_time_seconds"),
                "active_branch": analysis.get("branch"),
                "clone_url": analysis.get("clone_url"),
                "total_source_files_scanned": analysis.get("source_files_count"),
                "torch_device": device_name
            })
            
            with st.expander("Raw LLM Output Stream"):
                st.text(res.get("raw_llm_output", ""))
