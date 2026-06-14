"""
Utility functions for AgentLens.
"""

import json
import os
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


# --- Path Utilities ---

def expand_path(path: str) -> Path:
    """Expand user home and resolve path."""
    return Path(path).expanduser().resolve()


def find_agent_data_dirs() -> Dict[str, List[Path]]:
    """
    Find AI coding agent data directories on the system.
    Returns a dict mapping agent type to list of data directory paths.
    """
    home = Path.home()
    found = {}

    # Claude Code
    claude_paths = [
        home / ".claude" / "projects",
        home / ".claude" / "sessions",
    ]
    found["claude-code"] = [p for p in claude_paths if p.exists()]

    # Cursor
    cursor_paths = [
        home / ".cursor" / "sessions",
        home / ".cursor" / "history",
        Path(os.environ.get("APPDATA", "")) / "Cursor" / "User" / "globalStorage",
    ]
    found["cursor"] = [p for p in cursor_paths if p.exists()]

    # Windsurf
    windsurf_paths = [
        home / ".windsurf" / "sessions",
        home / ".codeium" / "windsurf" / "sessions",
    ]
    found["windsurf"] = [p for p in windsurf_paths if p.exists()]

    # Trae
    trae_paths = [
        home / ".trae" / "sessions",
        home / ".trae" / "data",
        home / ".config" / "Trae" / "sessions",
    ]
    found["trae"] = [p for p in trae_paths if p.exists()]

    # Copilot
    copilot_paths = [
        home / ".github" / "copilot",
        home / ".copilot",
    ]
    found["copilot"] = [p for p in copilot_paths if p.exists()]

    # Aider
    aider_paths = [
        home / ".aider" / "chat.history",
        home / ".aider" / "sessions",
    ]
    found["aider"] = [p for p in aider_paths if p.exists()]

    # Continue
    continue_paths = [
        home / ".continue" / "sessions",
    ]
    found["continue"] = [p for p in continue_paths if p.exists()]

    # Tongyi Lingma (通义灵码)
    lingma_paths = [
        home / ".lingma" / "sessions",
        home / ".config" / "lingma" / "data",
    ]
    found["tongyi-lingma"] = [p for p in lingma_paths if p.exists()]

    # Codeium
    codeium_paths = [
        home / ".codeium" / "sessions",
    ]
    found["codeium"] = [p for p in codeium_paths if p.exists()]

    return {k: v for k, v in found.items() if v}


def scan_session_files(directory: Path, extensions: List[str] = None) -> List[Path]:
    """Scan directory for session files."""
    if not directory.exists():
        return []

    if extensions is None:
        extensions = [".json", ".jsonl", ".log", ".txt", ".md"]

    files = []
    try:
        for ext in extensions:
            files.extend(directory.rglob(f"*{ext}"))
    except PermissionError:
        pass

    return sorted(set(files), key=lambda f: f.stat().st_mtime, reverse=True)


# --- String Utilities ---

def generate_session_id(content: str) -> str:
    """Generate a short hash ID from content."""
    return hashlib.md5(content.encode()).hexdigest()[:12]


def truncate_str(s: str, max_len: int = 100, suffix: str = "...") -> str:
    """Truncate string to max length."""
    if len(s) <= max_len:
        return s
    return s[:max_len - len(suffix)] + suffix


def count_tokens_approx(text: str) -> int:
    """
    Approximate token count for text.
    Uses a simple heuristic: ~4 chars per token for English, ~2 chars for CJK.
    """
    if not text:
        return 0

    # Count CJK characters
    cjk_count = len(re.findall(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', text))
    other_count = len(text) - cjk_count

    # Rough estimation
    tokens = int(cjk_count / 1.5) + int(other_count / 4)
    return max(tokens, 1)


# --- Cost Estimation ---

MODEL_PRICING = {
    # Claude models
    "claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
    "claude-3-opus": {"input": 15.0, "output": 75.0},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    "claude-4-sonnet": {"input": 3.0, "output": 15.0},
    "claude-4-opus": {"input": 15.0, "output": 75.0},
    # GPT models
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "o1": {"input": 15.0, "output": 60.0},
    "o3-mini": {"input": 1.1, "output": 4.4},
    # DeepSeek models
    "deepseek-v3": {"input": 0.27, "output": 1.1},
    "deepseek-r1": {"input": 0.55, "output": 2.19},
    # Qwen models
    "qwen-max": {"input": 1.6, "output": 4.8},
    "qwen-plus": {"input": 0.8, "output": 2.0},
    # Default
    "default": {"input": 3.0, "output": 15.0},
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost in USD for token usage."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
    cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
    return round(cost, 6)


def format_cost(cost_usd: float) -> str:
    """Format cost for display."""
    if cost_usd < 0.01:
        return f"${cost_usd * 1000:.2f}K"
    elif cost_usd < 1.0:
        return f"${cost_usd:.4f}"
    elif cost_usd < 100:
        return f"${cost_usd:.2f}"
    else:
        return f"${cost_usd:,.2f}"


# --- Time Utilities ---

def format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_timestamp(ts: float) -> str:
    """Format Unix timestamp to readable string."""
    if not ts:
        return "N/A"
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except (OSError, ValueError):
        return "Invalid"


def get_date_key(ts: float) -> str:
    """Get date string from timestamp."""
    if not ts:
        return "unknown"
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    except (OSError, ValueError):
        return "unknown"


# --- Number Formatting ---

def format_number(n: int) -> str:
    """Format large numbers with K/M suffixes."""
    if n < 1000:
        return str(n)
    elif n < 1_000_000:
        return f"{n / 1000:.1f}K"
    else:
        return f"{n / 1_000_000:.1f}M"


# --- JSON Utilities ---

def safe_load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Safely load JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError, IOError):
        return None


def safe_load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Safely load JSONL file."""
    records = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except (UnicodeDecodeError, IOError):
        pass
    return records
