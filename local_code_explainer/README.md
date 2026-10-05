# 🧠 Local GitHub Repository Code Explainer

A full-stack, local-first Generative AI application that accepts any GitHub repository URL, clones and inspects its source code, and uses a locally running Open-Source Large Language Model (LLM) to generate a simple-language, structured explanation of the codebase.

---

## 🏗️ Architecture & Flow

```
[ GitHub Repository URL ]
            │
            ▼
[ 1. Repository Processing (GitPython) ]
  • Shallow Clone (depth=1) & Cache
  • Ignore binaries, dependencies, lockfiles
  • Language Detection & Priority Sorting (README, configs, entrypoints)
  • ASCII Tree & Code Snippet Extraction
            │
            ▼
[ 2. Local GenAI Engine ]
  • Hugging Face Transformers (`Qwen/Qwen2.5-0.5B-Instruct`, `SmolLM2-360M`, etc.)
  • Or local Ollama Daemon (`qwen2.5`, `llama3.2`, `phi3`, `gemma2`)
  • System prompt enforcing structured explanation format
            │
            ▼
[ 3. FastAPI Backend (Uvicorn / Pydantic) ]
  • `/api/explain` - Main explanation endpoint
  • `/api/models` - Model discovery endpoint
  • `/api/health` - Health check & hardware detection
            │
            ▼
[ 4. Streamlit Frontend ]
  • Interactive Web UI with live pipeline status
  • Formatted Codebase Explanation (Overview, Features, Tech Stack, Flow)
  • Repository Structure Tree & Language Distribution Chart
  • Source Code Viewer with Syntax Highlighting
  • Download / Export explanation to Markdown (.md)
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed
- Git installed on your system

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launching the Application

#### Option A: One-Click Launch (Windows)
Double-click `run_all.bat` or run:
```powershell
.\run_all.bat
```

#### Option B: Launch Backend and Frontend Manually

**Terminal 1 (Start FastAPI Backend):**
```bash
python run_backend.py
```
Backend runs at: `http://127.0.0.1:8000` (API documentation at `http://127.0.0.1:8000/docs`)

**Terminal 2 (Start Streamlit Frontend):**
```bash
python run_frontend.py
```
Frontend opens automatically in your browser at: `http://localhost:8501`

---

## 🧪 Testing the Components

### 1. Test Repo Processing (Cloning & Code Extraction)
```bash
python test_pipeline.py
```

### 2. Test Local LLM Inference End-to-End
```bash
python test_llm.py
```

---

## 💻 Tech Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | Streamlit, Altair Charts |
| **Backend** | FastAPI, Uvicorn, Pydantic |
| **Repo Processing** | GitPython, Python File Handling, Regex |
| **Local GenAI** | Hugging Face Transformers, PyTorch, Ollama API |
| **Supported Models** | Qwen 2.5 (0.5B / 1.5B), SmolLM2 (360M), TinyLlama (1.1B), Phi-3, Gemma-2 |

---

## 📋 Example Output

```markdown
### Project Overview
This project is an expense tracking application.

### Key Features
The application allows users to:
• Add expenses
• View previous expenses
• Categorize expenses
• Calculate total spending

### Main Technologies
• Python (Backend)
• Flask (Web Framework)
• SQLite (Relational Database)

### How It Works
1. The user interacts with the frontend interface to enter expense details.
2. The frontend sends HTTP requests to the Flask backend routes.
3. The backend processes the request and stores expense records in SQLite database.
4. The backend queries the stored records and sends summarized data back to the user.
```
