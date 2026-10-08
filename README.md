# Generative AI Mini-Project: Local GitHub Repository Code Explainer

An end-to-end Generative AI application that accepts any public GitHub repository URL, clones and analyzes its codebase, and uses an Open-Source Large Language Model (LLM) to generate a simple-language, structured architectural explanation.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=Kailash246/Generative-AI&branch=main&mainModule=streamlit_app.py)

---

## 🌐 Live Streamlit Deployment

- **Streamlit App Entrypoint:** `streamlit_app.py`
- **One-Click Deploy:** [Deploy on Streamlit Community Cloud](https://share.streamlit.io/deploy?repository=Kailash246/Generative-AI&branch=main&mainModule=streamlit_app.py)

---

## 🏗️ System Architecture & Pipeline

```
GitHub Repository URL
         │
         ▼
[ 1. Repository Processing (GitPython) ]
  • Shallow Clone (depth=1) with local caching
  • Intelligent file filtering (ignoring binaries, lockfiles, node_modules, .venv)
  • Priority scoring & code excerpt extraction
         │
         ▼
[ 2. GenAI Inference Engine ]
  • Local Hugging Face Transformers (`Qwen/Qwen2.5-0.5B-Instruct`, `SmolLM2-360M`, `SmolLM2-135M`)
  • Optional Local Ollama daemon (`qwen2.5`, `llama3.2`, `phi3`)
         │
         ▼
[ 3. Backend & Engine Layer ]
  • Standalone in-process execution (for Streamlit Cloud deployment)
  • Or FastAPI REST Backend (`http://127.0.0.1:8000`) with Pydantic validation
         │
         ▼
[ 4. Frontend Dashboard (Streamlit) ]
  • Enterprise Developer UI (Linear / Vercel style, zero emojis)
  • Structured Explanation (Overview, Features, Main Tech, System Flow)
  • Interactive Directory Structure (ASCII tree & language chart)
  • Source Code Explorer with syntax highlighting
  • One-click Markdown Specification Export
```

---

## 📑 Project Reports

The formal mini-project report is included in multiple formats:

- **PDF Report (Standard Academic Format):** [`Project_Report.pdf`](Project_Report.pdf) / [`Mini_Project_Report_Local_GitHub_Code_Explainer.pdf`](Mini_Project_Report_Local_GitHub_Code_Explainer.pdf)
- **Word Document:** [`Project_Report.docx`](Project_Report.docx)

---

## 💻 Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Streamlit, Altair |
| **Backend API** | FastAPI, Uvicorn, Pydantic |
| **Repo Processing** | GitPython, Python File Handling, Regex |
| **GenAI Inference** | Hugging Face Transformers, PyTorch, Ollama |
| **Supported Models** | Qwen 2.5 (0.5B / 1.5B), SmolLM2 (135M / 360M), TinyLlama (1.1B) |

---

## 🚀 Local Setup & Execution

### 1. Clone the Repository
```bash
git clone https://github.com/Kailash246/Generative-AI.git
cd Generative-AI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application

#### Option A: Streamlit Direct Mode (Recommended & Cloud-Ready)
```bash
streamlit run streamlit_app.py
```

#### Option B: Full-Stack Mode (FastAPI Backend + Streamlit Frontend)
**Terminal 1 (Start Backend):**
```bash
cd local_code_explainer
python run_backend.py
```
*Backend runs on `http://127.0.0.1:8000` (Docs at `/docs`)*

**Terminal 2 (Start Frontend):**
```bash
cd local_code_explainer
python run_frontend.py
```

#### Option C: Windows One-Click Launcher
Double-click `local_code_explainer/run_all.bat`.

---

## 📋 Sample Explanation Output

```markdown
### Project Overview
This project is an interactive data visualization web application that analyzes and maps historical Uber taxi pickup patterns across New York City.

### Key Features
The application allows users to:
• View and interact with Uber pickup data on a dynamic 3D map.
• Filter pickup activity by specific hours of the day using interactive sliders.
• Visualize geographic pickup density using hexagon layers.
• Cache large datasets locally for fast user interactions.

### Main Technologies
• Python (Core application runtime)
• Streamlit (Web frontend framework and reactive UI)
• PyDeck & Altair (3D geospatial mapping and statistical charts)
• Pandas & NumPy (Data manipulation and filtering)

### How It Works
1. The user opens the web application and selects an hour on the Streamlit slider widget.
2. The Python backend filters the raw Uber pickup records for the selected time window.
3. PyDeck computes coordinates and renders the geographic density map.
4. The frontend displays the updated map and summary charts directly to the user.
```
