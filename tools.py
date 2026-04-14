


"""
tools.py — Tool execution layer

Handles file creation, code writing, summarization, and chat.
All file writes are restricted to output/ directory.
"""

import re
from pathlib import Path


# ── MAIN EXECUTOR ─────────────────────────────────────────────────────────────

def execute_tool(intent: str, params: dict, output_dir: Path) -> dict:
    """Main tool dispatcher"""

    print(f"[TOOL] Executing: {intent}")
    print(f"[PARAMS] {params}")

    # ✅ Safety: ensure params is dict
    if not isinstance(params, dict):
        params = {}

    handlers = {
        "create_file": _handle_create_file,
        "write_code": _handle_write_code,
        "summarize": _handle_summarize,
        "general_chat": _handle_chat,
    }

    handler = handlers.get(intent, _handle_chat)

    try:
        return handler(params, output_dir)
    except Exception as e:
        print(f"[TOOL ERROR] {e}")
        return {
            "action": f"Failed to execute {intent}",
            "output": "",
            "error": f"{type(e).__name__}: {str(e)}",
        }


# ── HANDLERS ──────────────────────────────────────────────────────────────────

def _handle_create_file(params: dict, output_dir: Path) -> dict:
    filename = _safe_filename(params.get("filename") or "output.txt")
    content = params.get("content") or ""

    if not content.strip():
        return {
            "action": "Create file",
            "output": "",
            "error": "No content generated.",
        }

    file_path = _safe_write(output_dir, filename, content)

    return {
        "action": f"Created file: {file_path.name}",
        "output": content,
        "file_path": str(file_path),
        "size": file_path.stat().st_size,
    }


def _handle_write_code(params: dict, output_dir: Path) -> dict:
    filename = _safe_filename(params.get("filename") or "script.py")
    code = params.get("code") or params.get("content") or ""

    if not code.strip():
        return {
            "action": "Write code",
            "output": "",
            "error": "No code generated.",
        }

    file_path = _safe_write(output_dir, filename, code)
    language = params.get("language") or _detect_language(filename)

    return {
        "action": f"Code written to: {file_path.name}",
        "output": code,
        "file_path": str(file_path),
        "language": language,
        "size": file_path.stat().st_size,
    }


def _handle_summarize(params: dict, output_dir: Path) -> dict:
    summary = params.get("response") or params.get("content") or ""
    filename = params.get("filename")

    if not summary.strip():
        return {
            "action": "Summarize",
            "output": "Please provide text to summarize.",
        }

    # Optional save
    if filename:
        filename = _safe_filename(filename)
        file_path = _safe_write(output_dir, filename, summary)

        return {
            "action": f"Summary saved to: {file_path.name}",
            "output": summary,
            "file_path": str(file_path),
            "size": file_path.stat().st_size,
        }

    return {
        "action": "Text summarized",
        "output": summary,
    }


def _handle_chat(params: dict, output_dir: Path) -> dict:
    response = params.get("response") or "I didn't understand that. Please try again."

    return {
        "action": "Chat response",
        "output": response,
    }


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _safe_write(output_dir: Path, filename: str, content: str) -> Path:
    """Safe file write with overwrite protection"""

    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = Path(filename).name
    file_path = output_dir / safe_name

    # ✅ Prevent overwrite → auto rename
    counter = 1
    while file_path.exists():
        stem = file_path.stem
        suffix = file_path.suffix
        file_path = output_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    # ✅ Limit size (avoid huge writes)
    if len(content) > 100_000:
        content = content[:100_000] + "\n\n... (truncated)"

    file_path.write_text(content, encoding="utf-8")

    print(f"[FILE] Saved: {file_path}")

    return file_path


def _safe_filename(filename: str) -> str:
    """Sanitize filename"""

    name = Path(filename).name
    name = re.sub(r"[^\w.\-]", "_", name)

    return name or "output.txt"


def _detect_language(filename: str) -> str:
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".go": "go",
        ".rs": "rust",
        ".sh": "bash",
        ".md": "markdown",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".txt": "text",
        ".yaml": "yaml",
        ".yml": "yaml",
    }

    return ext_map.get(Path(filename).suffix.lower(), "text")