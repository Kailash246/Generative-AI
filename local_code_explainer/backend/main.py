import time
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import RepoRequest, ExplanationResponse, HealthResponse, RepoAnalysis
from .repo_processor import RepoProcessor
from .llm_engine import LocalLLMEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("code_explainer.api")

app = FastAPI(
    title="Local GitHub Repository Code Explainer API",
    description="Backend service for cloning, processing, and generating simple-language codebase explanations using local LLMs.",
    version="1.0.0"
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
repo_processor = RepoProcessor()
llm_engine = LocalLLMEngine()

SUPPORTED_HF_MODELS = [
    {"id": "Qwen/Qwen2.5-0.5B-Instruct", "name": "Qwen 2.5 (0.5B Instruct - Fast & Lightweight CPU)", "default": True},
    {"id": "HuggingFaceTB/SmolLM2-360M-Instruct", "name": "SmolLM2 (360M Instruct - Ultra Fast)", "default": False},
    {"id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "name": "TinyLlama (1.1B Chat)", "default": False},
    {"id": "Qwen/Qwen2.5-1.5B-Instruct", "name": "Qwen 2.5 (1.5B Instruct - Balanced)", "default": False},
    {"id": "microsoft/Phi-3-mini-4k-instruct", "name": "Microsoft Phi-3 Mini (3.8B - Requires GPU/High RAM)", "default": False},
]

@app.get("/")
def read_root():
    return {
        "message": "Local GitHub Repository Code Explainer API is running.",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health", response_model=HealthResponse)
def get_health():
    ollama_ok = llm_engine.check_ollama_available()
    return HealthResponse(
        status="healthy",
        transformers_available=True,
        ollama_available=ollama_ok,
        active_transformers_model=llm_engine.hf_model_name,
        torch_device=llm_engine.device
    )

@app.get("/api/models")
def get_available_models():
    ollama_ok = llm_engine.check_ollama_available()
    ollama_models = llm_engine.get_ollama_models() if ollama_ok else []
    
    return {
        "transformers_models": SUPPORTED_HF_MODELS,
        "ollama_available": ollama_ok,
        "ollama_models": ollama_models
    }

@app.post("/api/analyze-tree", response_model=RepoAnalysis)
def analyze_repo_tree(request: RepoRequest):
    """Clones repo and extracts file tree and code without invoking LLM."""
    try:
        analysis = repo_processor.analyze_repository(request.repo_url)
        return analysis
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/explain", response_model=ExplanationResponse)
def explain_repository(request: RepoRequest):
    """Full pipeline: GitHub Repo -> Clone -> Process & Extract -> Local LLM -> Structured Explanation."""
    start_time = time.time()
    logger.info(f"Received explanation request for: {request.repo_url} using {request.model_provider} ({request.model_name})")

    # Step 1-3: Clone, Filter, and Extract Code
    try:
        analysis = repo_processor.analyze_repository(request.repo_url)
    except Exception as e:
        logger.error(f"Repository processing error: {str(e)}")
        return ExplanationResponse(
            status="error",
            repo_name="unknown",
            repo_url=request.repo_url,
            explanation=f"Failed to clone and process repository: {str(e)}",
            raw_llm_output="",
            model_used=request.model_name or "unknown",
            provider_used=request.model_provider,
            processing_time_seconds=round(time.time() - start_time, 2),
            error=str(e)
        )

    # Step 4-5: Run Local LLM
    try:
        explanation = llm_engine.generate_explanation(
            analysis=analysis,
            provider=request.model_provider,
            model_name=request.model_name,
            max_tokens=request.max_tokens or 800,
            temperature=request.temperature or 0.3
        )
        total_time = round(time.time() - start_time, 2)

        return ExplanationResponse(
            status="success",
            repo_name=analysis.repo_name,
            repo_url=request.repo_url,
            explanation=explanation,
            raw_llm_output=explanation,
            analysis=analysis,
            model_used=request.model_name or "Qwen/Qwen2.5-0.5B-Instruct",
            provider_used=request.model_provider,
            processing_time_seconds=total_time
        )
    except Exception as e:
        logger.error(f"LLM Generation error: {str(e)}")
        return ExplanationResponse(
            status="error",
            repo_name=analysis.repo_name,
            repo_url=request.repo_url,
            explanation=f"Error generating explanation with local LLM: {str(e)}",
            raw_llm_output="",
            analysis=analysis,
            model_used=request.model_name or "unknown",
            provider_used=request.model_provider,
            processing_time_seconds=round(time.time() - start_time, 2),
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
