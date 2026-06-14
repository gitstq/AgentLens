"""
Terminal UI for AgentLens using pure Python (no external TUI dependencies).
Provides colored output, tables, and dashboard display.
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from ..models import AnalysisResult, Session
from ..utils import (
    format_cost, format_duration, format_number,
    format_timestamp, get_date_key
)


# --- ANSI Color Codes ---

class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"


def supports_color() -> bool:
    """Check if terminal supports color output."""
    if os.environ.get("NO_COLOR"):
        return False
    if not hasattr(sys.stdout, "isatty"):
        return True
    if os.environ.get("TERM") == "dumb":
        return False
    return sys.stdout.isatty()


USE_COLOR = supports_color()


def c(text: str, color: str) -> str:
    """Apply color to text if supported."""
    if USE_COLOR:
        return f"{color}{text}{Colors.RESET}"
    return text


def bold(text: str) -> str:
    return c(text, Colors.BOLD)

def red(text: str) -> str:
    return c(text, Colors.RED)

def green(text: str) -> str:
    return c(text, Colors.GREEN)

def yellow(text: str) -> str:
    return c(text, Colors.YELLOW)

def blue(text: str) -> str:
    return c(text, Colors.BLUE)

def magenta(text: str) -> str:
    return c(text, Colors.MAGENTA)

def cyan(text: str) -> str:
    return c(text, Colors.CYAN)

def dim(text: str) -> str:
    return c(text, Colors.DIM)


# --- Table Rendering ---

def render_table(headers: List[str], rows: List[List[str]], max_col_width: int = 40) -> str:
    """Render a formatted table."""
    if not rows:
        return ""

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], min(len(str(cell)), max_col_width))

    lines = []

    # Header
    header_parts = []
    for i, h in enumerate(headers):
        header_parts.append(f" {h:<{col_widths[i]}} ")
    lines.append(bold("|" + "|".join(header_parts) + "|"))

    # Separator
    sep_parts = []
    for w in col_widths:
        sep_parts.append("-" * (w + 2))
    lines.append(dim("+" + "+".join(sep_parts) + "+"))

    # Rows
    for row in rows:
        row_parts = []
        for i, cell in enumerate(row):
            cell_str = str(cell)
            if len(cell_str) > max_col_width:
                cell_str = cell_str[:max_col_width - 3] + "..."
            if i < len(col_widths):
                row_parts.append(f" {cell_str:<{col_widths[i]}} ")
        lines.append("|" + "|".join(row_parts) + "|")

    return "\n".join(lines)


# --- Progress Bar ---

def render_progress_bar(value: float, max_value: float, width: int = 30, label: str = "") -> str:
    """Render a progress bar."""
    if max_value == 0:
        ratio = 0
    else:
        ratio = min(value / max_value, 1.0)

    filled = int(width * ratio)
    empty = width - filled

    bar = green("█" * filled) + dim("░" * empty)
    pct = f"{ratio * 100:.1f}%"

    if label:
        return f"{label}: {bar} {pct}"
    return f"{bar} {pct}"


# --- Dashboard ---

def render_dashboard(result: AnalysisResult, title: str = "AgentLens Dashboard") -> str:
    """Render a full analysis dashboard."""
    lines = []

    # Title banner
    banner_width = 60
    lines.append("")
    lines.append(cyan("=" * banner_width))
    lines.append(bold(cyan(f"  {title}")))
    lines.append(cyan("=" * banner_width))
    lines.append("")

    # Overview section
    lines.append(bold("  Overview"))
    lines.append(dim("  " + "-" * 40))
    overview_data = [
        ("Total Sessions", str(result.total_sessions), blue),
        ("Total Tokens", format_number(result.total_tokens), yellow),
        ("Total Cost", format_cost(result.total_cost_usd), green if result.total_cost_usd < 10 else red),
        ("Total Duration", format_duration(result.total_duration_seconds), cyan),
        ("Total Messages", format_number(result.total_messages), magenta),
        ("Tool Calls", format_number(result.total_tool_calls), blue),
        ("Files Changed", str(result.total_files_changed), green),
    ]
    for label, value, color_fn in overview_data:
        lines.append(f"    {dim(label + ':'):<20} {color_fn(bold(value))}")
    lines.append("")

    # Agent Distribution
    if result.agent_distribution:
        lines.append(bold("  Agent Distribution"))
        lines.append(dim("  " + "-" * 40))
        max_sessions = max(result.agent_distribution.values())
        for agent, count in sorted(result.agent_distribution.items(), key=lambda x: -x[1]):
            bar = render_progress_bar(count, max_sessions, width=20)
            lines.append(f"    {agent:<20} {bar} ({count})")
        lines.append("")

    # Cost by Model
    if result.cost_by_model:
        lines.append(bold("  Cost by Model"))
        lines.append(dim("  " + "-" * 40))
        for model, cost in sorted(result.cost_by_model.items(), key=lambda x: -x[1]):
            lines.append(f"    {model:<25} {format_cost(cost):>10}")
        lines.append("")

    # Top Tools
    if result.top_tools:
        lines.append(bold("  Top Tools"))
        lines.append(dim("  " + "-" * 40))
        max_calls = result.top_tools[0]["calls"] if result.top_tools else 1
        for tool in result.top_tools[:10]:
            bar = render_progress_bar(tool["calls"], max_calls, width=15)
            lines.append(f"    {tool['name']:<25} {bar}")
        lines.append("")

    # Daily Usage (last 7 days)
    if result.daily_usage:
        lines.append(bold("  Daily Usage (Recent)"))
        lines.append(dim("  " + "-" * 40))
        recent_days = sorted(result.daily_usage.items(), reverse=True)[:7]
        max_tokens = max(d["tokens"] for _, d in recent_days) if recent_days else 1
        for date, data in reversed(recent_days):
            bar = render_progress_bar(data["tokens"], max_tokens, width=15)
            lines.append(f"    {date}  {bar}  {format_number(data['tokens'])} tokens")
        lines.append("")

    # Optimization Tips
    if result.optimization_tips:
        lines.append(bold("  Optimization Tips"))
        lines.append(dim("  " + "-" * 40))
        for i, tip in enumerate(result.optimization_tips, 1):
            lines.append(f"    {yellow(f'{i}.')} {tip}")
        lines.append("")

    lines.append(cyan("=" * banner_width))
    lines.append("")

    return "\n".join(lines)


def render_session_list(sessions: List[Session], limit: int = 20) -> str:
    """Render a list of sessions."""
    if not sessions:
        return dim("  No sessions found.")

    headers = ["ID", "Agent", "Messages", "Tokens", "Cost", "Duration", "Time"]
    rows = []
    for s in sessions[:limit]:
        rows.append([
            s.session_id[:10],
            s.agent_type.value,
            str(s.message_count),
            format_number(s.total_tokens),
            format_cost(s.total_cost_usd),
            format_duration(s.duration_seconds),
            format_timestamp(s.start_time)[:10] if s.start_time else "N/A",
        ])

    return render_table(headers, rows)


def render_summary_line(result: AnalysisResult) -> str:
    """Render a one-line summary."""
    parts = [
        f"{cyan(result.total_sessions)} sessions",
        f"{yellow(format_number(result.total_tokens))} tokens",
        f"{green(format_cost(result.total_cost_usd))} cost",
        f"{blue(format_duration(result.total_duration_seconds))} duration",
    ]
    return " | ".join(parts)


def print_banner():
    """Print AgentLens ASCII banner."""
    banner = f"""
{cyan('╔══════════════════════════════════════════════════════╗')}
{cyan('║')}                                                      {cyan('║')}
{bold(cyan('║'))}   {bold('AgentLens')} - AI Coding Agent Session Analyzer  {bold(cyan('║'))}
{cyan('║')}   {dim('Lightweight | Zero Dependencies | Cross-Platform')}   {cyan('║')}
{cyan('║')}                                                      {cyan('║')}
{cyan('╚══════════════════════════════════════════════════════╝')}
"""
    print(banner)
