import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import git

from .models import FileContent, RepoAnalysis

# Supported code extensions and their language names
SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Shell",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".json": "JSON",
    ".toml": "TOML",
    ".md": "Markdown",
}

# Directories to ignore
IGNORED_DIRS = {
    ".git", ".github", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".env", "dist", "build", "target", ".idea", ".vscode", ".next", ".nuxt",
    ".cache", "coverage", ".pytest_cache", ".mypy_cache", ".tox", "vendor",
    "bin", "obj", ".turbo", "Pods", ".gradle"
}

# Ignored specific files (lockfiles, generated, binaries)
IGNORED_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    "Pipfile.lock", "Cargo.lock", "composer.lock", "go.sum", ".DS_Store",
    "Thumbs.db", "LICENSE", "LICENSE.txt", "LICENCE"
}

# Key entrypoint/configuration filenames for high-priority inspection
PRIORITY_FILENAMES = {
    "readme.md", "readme.txt", "readme",
    "requirements.txt", "package.json", "pyproject.toml", "cargo.toml",
    "go.mod", "pom.xml", "build.gradle", "dockerfile", "docker-compose.yml",
    "app.py", "main.py", "server.py", "index.py", "wsgi.py", "asgi.py",
    "index.js", "server.js", "app.js", "main.js", "index.ts", "app.ts", "main.ts",
    "main.go", "main.rs", "routes.py", "urls.py", "views.py", "models.py",
    "schema.prisma", "application.properties", "application.yml"
}

class RepoProcessor:
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(tempfile.gettempdir()) / "repo_explainer_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def parse_repo_url(self, repo_url: str) -> Tuple[str, str, str]:
        """Extracts owner, repo_name, and normalized clone URL."""
        url = repo_url.strip().rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]
        
        # Match github.com/owner/repo pattern
        match = re.search(r"github\.com[/:]([\w\.-]+)/([\w\.-]+)", url)
        if not match:
            # Fallback for generic git URLs or simple names
            parts = url.split("/")
            if len(parts) >= 2:
                owner, repo_name = parts[-2], parts[-1]
                return owner, repo_name, f"https://github.com/{owner}/{repo_name}.git"
            raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
        
        owner, repo_name = match.group(1), match.group(2)
        clone_url = f"https://github.com/{owner}/{repo_name}.git"
        return owner, repo_name, clone_url

    @staticmethod
    def _force_delete_dir(target_dir: Path):
        """Force delete a directory on Windows handling read-only git pack/lock files."""
        import stat
        def on_rm_error(func, path, exc_info):
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass

        if target_dir.exists():
            shutil.rmtree(target_dir, onerror=on_rm_error)

    def clone_or_update_repo(self, repo_url: str, force_refresh: bool = False) -> Tuple[Path, str, str, str]:
        """Clones a repository shallowly or returns cached path with auto-recovery."""
        owner, repo_name, clone_url = self.parse_repo_url(repo_url)
        target_dir = self.cache_dir / f"{owner}_{repo_name}"

        if target_dir.exists():
            if force_refresh:
                self._force_delete_dir(target_dir)
            else:
                # Remove any stale git lock files
                git_dir = target_dir / ".git"
                if git_dir.exists():
                    for lock_file in git_dir.glob("*.lock"):
                        try:
                            os.chmod(lock_file, stat.S_IWRITE)
                            lock_file.unlink(missing_ok=True)
                        except Exception:
                            pass
                # Check if it's a valid usable repo
                try:
                    repo = git.Repo(target_dir)
                    active_branch = repo.active_branch.name if not repo.head.is_detached else "main"
                    return target_dir, owner, repo_name, active_branch
                except Exception:
                    self._force_delete_dir(target_dir)

        # Attempt shallow clone (depth 1)
        try:
            repo = git.Repo.clone_from(clone_url, target_dir, depth=1)
            active_branch = repo.active_branch.name if not repo.head.is_detached else "main"
            return target_dir, owner, repo_name, active_branch
        except Exception as first_err:
            # If clone failed (e.g. leftover lockfile, network glitch), purge target_dir and retry once
            self._force_delete_dir(target_dir)
            try:
                repo = git.Repo.clone_from(clone_url, target_dir, depth=1)
                active_branch = repo.active_branch.name if not repo.head.is_detached else "main"
                return target_dir, owner, repo_name, active_branch
            except Exception as retry_err:
                self._force_delete_dir(target_dir)
                raise RuntimeError(f"Failed to clone repository '{clone_url}': {str(retry_err)}")

    def build_file_tree(self, root_dir: Path, max_depth: int = 4, max_files: int = 150) -> Tuple[str, List[Path]]:
        """Generates an ASCII file tree and returns collected source file paths."""
        tree_lines = []
        collected_files: List[Path] = []
        count = 0

        def _walk(current_path: Path, prefix: str = "", depth: int = 0):
            nonlocal count
            if depth > max_depth or count >= max_files:
                return

            try:
                entries = sorted(list(current_path.iterdir()), key=lambda e: (not e.is_dir(), e.name.lower()))
            except PermissionError:
                return

            # Filter entries
            filtered_entries = [
                e for e in entries
                if e.name not in IGNORED_DIRS and not e.name.startswith(".")
                and (e.is_dir() or e.suffix.lower() in SUPPORTED_EXTENSIONS or e.name.lower() in PRIORITY_FILENAMES)
                and e.name not in IGNORED_FILES
            ]

            total = len(filtered_entries)
            for idx, entry in enumerate(filtered_entries):
                if count >= max_files:
                    tree_lines.append(f"{prefix}\\-- ... (truncated)")
                    break

                is_last = (idx == total - 1)
                connector = "\\-- " if is_last else "|-- "
                next_prefix = prefix + ("    " if is_last else "|   ")

                if entry.is_dir():
                    tree_lines.append(f"{prefix}{connector}[DIR] {entry.name}/")
                    _walk(entry, next_prefix, depth + 1)
                else:
                    count += 1
                    tree_lines.append(f"{prefix}{connector}{entry.name}")
                    collected_files.append(entry)

        tree_lines.append(f"[{root_dir.name}]")
        _walk(root_dir)
        return "\n".join(tree_lines), collected_files

    def analyze_repository(self, repo_url: str, force_refresh: bool = False, max_content_chars: int = 12000) -> RepoAnalysis:
        """Clones, scans, extracts files, and prepares repository context."""
        repo_dir, owner, repo_name, branch = self.clone_or_update_repo(repo_url, force_refresh)
        file_tree_str, source_file_paths = self.build_file_tree(repo_dir)

        # Detect languages and tally
        detected_languages: Dict[str, int] = {}
        readme_preview: Optional[str] = None
        extracted_files: List[FileContent] = []

        # Sort files by priority
        def file_priority_score(file_path: Path) -> int:
            name_lower = file_path.name.lower()
            rel_path = str(file_path.relative_to(repo_dir)).replace("\\", "/").lower()
            
            if "readme" in name_lower:
                return 0  # Highest priority
            if name_lower in PRIORITY_FILENAMES:
                return 1
            if any(key in name_lower for key in ["main", "app", "server", "index", "router", "model", "config"]):
                return 2
            if "test" in rel_path or "spec" in rel_path:
                return 5  # Lower priority
            return 3

        sorted_files = sorted(source_file_paths, key=file_priority_score)

        chars_budget_remaining = max_content_chars
        total_source_files = len(source_file_paths)

        for file_path in sorted_files:
            rel_path = str(file_path.relative_to(repo_dir)).replace("\\", "/")
            ext = file_path.suffix.lower()
            lang = SUPPORTED_EXTENSIONS.get(ext, "Plain Text")

            # Update language counts
            if ext in SUPPORTED_EXTENSIONS:
                detected_languages[lang] = detected_languages.get(lang, 0) + 1

            # Extract content if budget allows
            if chars_budget_remaining <= 0:
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception:
                continue

            lines = content.splitlines()
            line_count = len(lines)

            # Capture README preview
            if "readme" in file_path.name.lower() and not readme_preview:
                # Store first 1000 chars of readme
                readme_preview = content[:1500]

            # Truncate very long files to save budget for diverse files
            max_lines_per_file = 100 if "readme" not in file_path.name.lower() else 150
            if len(lines) > max_lines_per_file:
                trimmed_content = "\n".join(lines[:max_lines_per_file]) + f"\n\n... [Truncated: {len(lines) - max_lines_per_file} more lines] ..."
            else:
                trimmed_content = content

            # Slice if budget is tight
            if len(trimmed_content) > chars_budget_remaining:
                trimmed_content = trimmed_content[:chars_budget_remaining] + "\n... [Truncated due to context limit] ..."

            chars_budget_remaining -= len(trimmed_content)

            extracted_files.append(FileContent(
                path=rel_path,
                language=lang,
                content=trimmed_content,
                line_count=line_count
            ))

        return RepoAnalysis(
            repo_name=repo_name,
            repo_owner=owner,
            clone_url=f"https://github.com/{owner}/{repo_name}",
            branch=branch,
            total_files=len(source_file_paths),
            source_files_count=total_source_files,
            detected_languages=detected_languages,
            file_tree_str=file_tree_str,
            extracted_files=extracted_files,
            readme_preview=readme_preview
        )
