from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

class RepoRequest(BaseModel):
    repo_url: str = Field(..., description="Full GitHub repository URL, e.g. https://github.com/username/repo")
    model_provider: str = Field(default="transformers", description="'transformers' or 'ollama'")
    model_name: Optional[str] = Field(default="Qwen/Qwen2.5-0.5B-Instruct", description="Name of the model to use")
    max_tokens: Optional[int] = Field(default=1024, description="Maximum tokens for explanation generation")
    temperature: Optional[float] = Field(default=0.3, description="Temperature for sampling")

class FileNode(BaseModel):
    name: str
    path: str
    is_dir: bool
    size_bytes: int = 0
    language: Optional[str] = None
    children: Optional[List['FileNode']] = None

class FileContent(BaseModel):
    path: str
    language: str
    content: str
    line_count: int

class RepoAnalysis(BaseModel):
    repo_name: str
    repo_owner: str
    clone_url: str
    branch: str
    total_files: int
    source_files_count: int
    detected_languages: Dict[str, int]
    file_tree_str: str
    extracted_files: List[FileContent]
    readme_preview: Optional[str] = None

class ExplanationResponse(BaseModel):
    status: str
    repo_name: str
    repo_url: str
    explanation: str
    raw_llm_output: str
    analysis: Optional[RepoAnalysis] = None
    model_used: str
    provider_used: str
    processing_time_seconds: float
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    transformers_available: bool
    ollama_available: bool
    active_transformers_model: Optional[str] = None
    torch_device: str
