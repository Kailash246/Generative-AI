import os
import time
import json
import logging
from typing import Optional, Dict, Any, List
import requests

from .models import RepoAnalysis

logger = logging.getLogger("code_explainer.llm")

SYSTEM_PROMPT = """You are an expert software engineer and technical educator.
Your task is to analyze the provided source code, file tree, and configuration files of a GitHub repository, and generate a clear, simple-language explanation of what the codebase does.

You MUST format your output strictly with the following sections in Markdown:

### Project Overview
A clear, non-jargon explanation of what the repository is and what problem it solves.

### Key Features
The application allows users to:
• [Bullet point 1]
• [Bullet point 2]
• [Bullet point 3]
• [Bullet point 4]

### Main Technologies
• [Technology 1: purpose/role]
• [Technology 2: purpose/role]
• [Technology 3: purpose/role]

### How It Works
Provide a step-by-step walkthrough of the data and user flow:
1. The user interacts with...
2. The frontend/client sends requests to...
3. The backend/engine processes...
4. The data is stored or retrieved from...
5. The result is returned to...

Be concise, accurate, and explain in simple terms without unnecessary technical jargon. Focus on what the actual code implements."""

class LocalLLMEngine:
    def __init__(self):
        self.hf_pipeline = None
        self.hf_model_name = None
        self.hf_tokenizer = None
        self.hf_model = None
        self.device = "cpu"
        
        # Optimize CPU threads for faster local inference
        try:
            import torch
            num_cores = os.cpu_count() or 4
            torch.set_num_threads(max(1, num_cores - 1))
            if torch.cuda.is_available():
                self.device = "cuda"
        except Exception:
            pass

    def check_ollama_available(self, host: str = "http://127.0.0.1:11434") -> bool:
        """Fast non-blocking check if local Ollama daemon is running."""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            result = sock.connect_ex(('127.0.0.1', 11434))
            sock.close()
            return result == 0
        except Exception:
            return False

    def get_ollama_models(self, host: str = "http://127.0.0.1:11434") -> List[str]:
        """Fetch list of downloaded Ollama models if service is up."""
        if not self.check_ollama_available(host):
            return []
        try:
            res = requests.get(f"{host}/api/tags", timeout=1.0)
            if res.status_code == 200:
                data = res.json()
                return [m.get("name") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def load_transformers_model(self, model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"):
        """Loads Hugging Face model and tokenizer into memory."""
        if self.hf_pipeline is not None and self.hf_model_name == model_name:
            return self.hf_pipeline

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        logger.info(f"Loading Hugging Face model: {model_name} on device: {self.device}")
        print(f"Loading Hugging Face model: {model_name} on {self.device}...")

        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        dtype = torch.float32 if self.device == "cpu" else torch.float16
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            dtype=dtype,
            device_map="auto" if self.device == "cuda" else None,
            trust_remote_code=True
        )

        if self.device == "cpu":
            model = model.to("cpu")

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=0 if self.device == "cuda" else -1
        )

        self.hf_pipeline = pipe
        self.hf_tokenizer = tokenizer
        self.hf_model = model
        self.hf_model_name = model_name
        return pipe

    def build_prompt_context(self, analysis: RepoAnalysis) -> str:
        """Constructs code analysis context for LLM prompt."""
        context_parts = []
        context_parts.append(f"Repository Name: {analysis.repo_name} (Owner: {analysis.repo_owner})")
        
        techs = ", ".join([f"{lang} ({count} files)" for lang, count in analysis.detected_languages.items()])
        context_parts.append(f"Detected Languages/Files: {techs}")
        
        context_parts.append("\n=== REPOSITORY STRUCTURE ===")
        context_parts.append(analysis.file_tree_str)

        if analysis.readme_preview:
            context_parts.append("\n=== README EXCERPT ===")
            context_parts.append(analysis.readme_preview)

        context_parts.append("\n=== SOURCE CODE EXCERPTS ===")
        for file in analysis.extracted_files:
            context_parts.append(f"\n--- File: {file.path} ({file.language}) ---")
            context_parts.append(file.content)

        return "\n".join(context_parts)

    def generate_with_transformers(
        self,
        analysis: RepoAnalysis,
        model_name: str = "Qwen/Qwen2.5-0.5B-Instruct",
        max_new_tokens: int = 800,
        temperature: float = 0.3
    ) -> str:
        """Generates explanation using local Hugging Face Transformers."""
        pipe = self.load_transformers_model(model_name)
        context = self.build_prompt_context(analysis)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the repository information and source code for {analysis.repo_name}:\n\n{context}\n\nPlease generate a simple-language structured explanation of this codebase."}
        ]

        # Use tokenizer chat template
        if hasattr(self.hf_tokenizer, "apply_chat_template") and self.hf_tokenizer.chat_template:
            prompt = self.hf_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            prompt = f"{SYSTEM_PROMPT}\n\nUser: Analyze this repository:\n{context}\n\nAssistant:"

        output = pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=True if temperature > 0 else False,
            temperature=max(temperature, 0.1),
            top_p=0.9,
            repetition_penalty=1.1,
            return_full_text=False
        )

        generated_text = output[0]["generated_text"].strip()
        return generated_text

    def generate_with_ollama(
        self,
        analysis: RepoAnalysis,
        model_name: str = "qwen2.5:latest",
        host: str = "http://localhost:11434",
        max_tokens: int = 1000,
        temperature: float = 0.3
    ) -> str:
        """Generates explanation using local Ollama instance."""
        context = self.build_prompt_context(analysis)
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is the repository information and source code for {analysis.repo_name}:\n\n{context}\n\nPlease generate a simple-language structured explanation of this codebase."}
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        res = requests.post(f"{host}/api/chat", json=payload, timeout=120)
        if res.status_code == 200:
            data = res.json()
            return data.get("message", {}).get("content", "").strip()
        else:
            raise RuntimeError(f"Ollama error ({res.status_code}): {res.text}")

    def generate_explanation(
        self,
        analysis: RepoAnalysis,
        provider: str = "transformers",
        model_name: Optional[str] = None,
        max_tokens: int = 800,
        temperature: float = 0.3
    ) -> str:
        """Main dispatcher for explanation generation."""
        if provider == "ollama":
            ollama_model = model_name or "qwen2.5:latest"
            return self.generate_with_ollama(analysis, model_name=ollama_model, max_tokens=max_tokens, temperature=temperature)
        else:
            hf_model = model_name or "Qwen/Qwen2.5-0.5B-Instruct"
            return self.generate_with_transformers(analysis, model_name=hf_model, max_new_tokens=max_tokens, temperature=temperature)
