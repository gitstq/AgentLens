"""
Session parsers for various AI coding agents.
Each parser extracts structured session data from agent-specific formats.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..models import (
    Session, Message, ToolUsage, FileChange, CostRecord,
    AgentType, SessionStatus
)
from ..utils import (
    count_tokens_approx, estimate_cost, generate_session_id,
    safe_load_json, safe_load_jsonl, scan_session_files,
    get_date_key, format_timestamp
)


class BaseParser:
    """Base class for session parsers."""

    agent_type: AgentType = AgentType.UNKNOWN
    agent_name: str = "Unknown"

    def parse_directory(self, directory: Path, max_files: int = 100) -> List[Session]:
        """Parse all session files in a directory."""
        sessions = []
        files = scan_session_files(directory)

        for filepath in files[:max_files]:
            try:
                session = self.parse_file(filepath)
                if session and session.message_count > 0:
                    sessions.append(session)
            except Exception:
                continue

        return sessions

    def parse_file(self, filepath: Path) -> Optional[Session]:
        """Parse a single session file. Override in subclasses."""
        raise NotImplementedError

    def _extract_messages(self, data: Any) -> List[Message]:
        """Extract messages from parsed data."""
        return []

    def _extract_tool_usage(self, data: Any) -> List[ToolUsage]:
        """Extract tool usage from parsed data."""
        return []

    def _extract_file_changes(self, data: Any) -> List[FileChange]:
        """Extract file changes from parsed data."""
        return []

    def _extract_cost(self, data: Any) -> List[CostRecord]:
        """Extract cost records from parsed data."""
        return []


class ClaudeCodeParser(BaseParser):
    """Parser for Claude Code sessions."""

    agent_type = AgentType.CLAUDE_CODE
    agent_name = "Claude Code"

    def parse_file(self, filepath: Path) -> Optional[Session]:
        """Parse Claude Code JSONL session file."""
        ext = filepath.suffix.lower()

        if ext == ".jsonl":
            records = safe_load_jsonl(filepath)
        elif ext == ".json":
            data = safe_load_json(filepath)
            records = [data] if data else []
        else:
            # Try JSONL for unknown extensions
            records = safe_load_jsonl(filepath)

        if not records:
            return None

        session = Session(
            session_id=generate_session_id(filepath.name),
            agent_type=self.agent_type,
            metadata={"source_file": str(filepath)}
        )

        messages = []
        tool_usages = {}
        file_changes = []
        cost_records = {}
        total_input = 0
        total_output = 0
        model = ""

        for record in records:
            # Extract messages
            if "role" in record and "content" in record:
                content = record["content"]
                if isinstance(content, list):
                    text_parts = [p.get("text", "") for p in content if isinstance(p, dict)]
                    content = "\n".join(text_parts)
                msg = Message(
                    role=record.get("role", "unknown"),
                    content=str(content),
                    timestamp=record.get("timestamp", 0),
                    token_count=count_tokens_approx(str(content)),
                    model=record.get("model", "")
                )
                messages.append(msg)
                if record.get("model"):
                    model = record["model"]

            # Extract tool calls
            if "tool_calls" in record or "tool_use" in record:
                tool_calls = record.get("tool_calls", record.get("tool_use", []))
                if isinstance(tool_calls, list):
                    for tc in tool_calls:
                        if isinstance(tc, dict):
                            name = tc.get("name", tc.get("tool", "unknown"))
                        else:
                            name = str(tc)
                        if name not in tool_usages:
                            tool_usages[name] = ToolUsage(tool_name=name)
                        tool_usages[name].call_count += 1

            # Extract token usage
            if "usage" in record:
                usage = record["usage"]
                if isinstance(usage, dict):
                    inp = usage.get("input_tokens", usage.get("prompt_tokens", 0))
                    out = usage.get("output_tokens", usage.get("completion_tokens", 0))
                    total_input += inp
                    total_output += out

            # Extract file changes from tool results
            if "tool_results" in record:
                for result in record.get("tool_results", []):
                    if isinstance(result, dict):
                        for change in self._parse_file_change(result):
                            file_changes.append(change)

        session.messages = messages
        session.tool_usages = list(tool_usages.values())
        session.file_changes = file_changes
        session.total_tokens = total_input + total_output

        if total_input or total_output:
            cost = estimate_cost(model or "claude-3.5-sonnet", total_input, total_output)
            session.cost_records = [CostRecord(
                model=model or "claude-3.5-sonnet",
                input_tokens=total_input,
                output_tokens=total_output,
                total_tokens=total_input + total_output,
                estimated_cost_usd=cost
            )]
            session.total_cost_usd = cost

        if messages:
            session.start_time = messages[0].timestamp
            session.end_time = messages[-1].timestamp

        return session

    def _parse_file_change(self, result: Dict) -> List[FileChange]:
        """Parse file changes from tool result."""
        changes = []
        content = result.get("content", "")
        if isinstance(content, str):
            # Look for file write/edit patterns
            for pattern in [r'(\S+\.\w+).*?(\d+) lines', r'Wrote (\S+)', r'Edited (\S+)']:
                matches = re.findall(pattern, content)
                for match in matches:
                    path = match[0] if isinstance(match, tuple) else match
                    changes.append(FileChange(file_path=str(path), action="modify"))
        return changes


class CursorParser(BaseParser):
    """Parser for Cursor IDE sessions."""

    agent_type = AgentType.CURSOR
    agent_name = "Cursor"

    def parse_file(self, filepath: Path) -> Optional[Session]:
        """Parse Cursor session file."""
        data = safe_load_json(filepath)
        if not data:
            records = safe_load_jsonl(filepath)
            if not records:
                return None
            data = records[0] if records else None
            if not data:
                return None

        session = Session(
            session_id=generate_session_id(filepath.name),
            agent_type=self.agent_type,
            metadata={"source_file": str(filepath)}
        )

        messages = []
        tool_usages = {}
        total_input = 0
        total_output = 0
        model = ""

        # Handle array of messages
        msg_list = data.get("messages", data.get("chat", []))
        if isinstance(msg_list, list):
            for msg_data in msg_list:
                if isinstance(msg_data, dict):
                    role = msg_data.get("role", "unknown")
                    content = msg_data.get("content", msg_data.get("text", ""))
                    if isinstance(content, list):
                        text_parts = [p.get("text", "") for p in content if isinstance(p, dict)]
                        content = "\n".join(text_parts)

                    msg = Message(
                        role=role,
                        content=str(content),
                        timestamp=msg_data.get("timestamp", msg_data.get("createdAt", 0)),
                        token_count=count_tokens_approx(str(content)),
                        model=msg_data.get("model", "")
                    )
                    messages.append(msg)

                    if msg_data.get("model"):
                        model = msg_data["model"]

                    # Tool usage
                    if "toolCalls" in msg_data or "tool_calls" in msg_data:
                        for tc in msg_data.get("toolCalls", msg_data.get("tool_calls", [])):
                            name = tc.get("name", tc.get("function", {}).get("name", "unknown"))
                            if name not in tool_usages:
                                tool_usages[name] = ToolUsage(tool_name=name)
                            tool_usages[name].call_count += 1

                    # Token usage
                    usage = msg_data.get("usage", {})
                    if isinstance(usage, dict):
                        total_input += usage.get("promptTokens", usage.get("input_tokens", 0))
                        total_output += usage.get("completionTokens", usage.get("output_tokens", 0))

        session.messages = messages
        session.tool_usages = list(tool_usages.values())
        session.total_tokens = total_input + total_output

        if total_input or total_output:
            cost = estimate_cost(model or "gpt-4o", total_input, total_output)
            session.cost_records = [CostRecord(
                model=model or "gpt-4o",
                input_tokens=total_input,
                output_tokens=total_output,
                total_tokens=total_input + total_output,
                estimated_cost_usd=cost
            )]
            session.total_cost_usd = cost

        if messages:
            session.start_time = messages[0].timestamp
            session.end_time = messages[-1].timestamp

        return session


class TraeParser(BaseParser):
    """Parser for Trae IDE sessions."""

    agent_type = AgentType.TRAE
    agent_name = "Trae"

    def parse_file(self, filepath: Path) -> Optional[Session]:
        """Parse Trae session file."""
        data = safe_load_json(filepath)
        if not data:
            records = safe_load_jsonl(filepath)
            if records:
                data = {"messages": records}
            else:
                return None

        session = Session(
            session_id=generate_session_id(filepath.name),
            agent_type=self.agent_type,
            metadata={"source_file": str(filepath)}
        )

        messages = []
        tool_usages = {}
        file_changes = []
        total_input = 0
        total_output = 0
        model = ""

        # Trae format: conversations array or messages array
        conv_list = data.get("conversations", data.get("messages", data.get("chatHistory", [])))
        if isinstance(conv_list, list):
            for item in conv_list:
                if isinstance(item, dict):
                    role = item.get("role", item.get("type", "unknown"))
                    if role in ("human", "user"):
                        role = "user"
                    elif role in ("ai", "assistant", "bot"):
                        role = "assistant"

                    content = item.get("content", item.get("text", item.get("message", "")))
                    if isinstance(content, list):
                        text_parts = [p.get("text", "") for p in content if isinstance(p, dict)]
                        content = "\n".join(text_parts)

                    msg = Message(
                        role=role,
                        content=str(content),
                        timestamp=item.get("timestamp", item.get("createdAt", 0)),
                        token_count=count_tokens_approx(str(content)),
                        model=item.get("model", "")
                    )
                    messages.append(msg)

                    if item.get("model"):
                        model = item["model"]

                    # File changes
                    if "fileChanges" in item:
                        for fc in item["fileChanges"]:
                            file_changes.append(FileChange(
                                file_path=fc.get("path", fc.get("file", "")),
                                action=fc.get("action", "modify"),
                                lines_added=fc.get("added", 0),
                                lines_removed=fc.get("removed", 0)
                            ))

                    # Tool calls
                    if "toolCalls" in item:
                        for tc in item["toolCalls"]:
                            name = tc.get("name", "unknown")
                            if name not in tool_usages:
                                tool_usages[name] = ToolUsage(tool_name=name)
                            tool_usages[name].call_count += 1

        session.messages = messages
        session.tool_usages = list(tool_usages.values())
        session.file_changes = file_changes
        session.total_tokens = total_input + total_output

        if total_input or total_output:
            cost = estimate_cost(model or "claude-3.5-sonnet", total_input, total_output)
            session.cost_records = [CostRecord(
                model=model or "claude-3.5-sonnet",
                input_tokens=total_input,
                output_tokens=total_output,
                total_tokens=total_input + total_output,
                estimated_cost_usd=cost
            )]
            session.total_cost_usd = cost

        if messages:
            session.start_time = messages[0].timestamp
            session.end_time = messages[-1].timestamp

        return session


class GenericParser(BaseParser):
    """Generic parser for unknown/unsupported agent formats."""

    agent_type = AgentType.UNKNOWN
    agent_name = "Generic"

    def parse_file(self, filepath: Path) -> Optional[Session]:
        """Attempt to parse any JSON/JSONL file as a session."""
        ext = filepath.suffix.lower()

        if ext == ".json":
            data = safe_load_json(filepath)
            if not data:
                return None
            return self._parse_generic_data(data, filepath)
        elif ext == ".jsonl":
            records = safe_load_jsonl(filepath)
            if records:
                return self._parse_generic_data({"messages": records}, filepath)
        else:
            # Try as text log
            return self._parse_text_file(filepath)

        return None

    def _parse_generic_data(self, data: Dict, filepath: Path) -> Optional[Session]:
        """Parse generic JSON data structure."""
        session = Session(
            session_id=generate_session_id(filepath.name),
            agent_type=self.agent_type,
            metadata={"source_file": str(filepath)}
        )

        messages = []
        # Try common field names for message lists
        for key in ["messages", "chat", "conversation", "history", "turns"]:
            msg_list = data.get(key, [])
            if isinstance(msg_list, list):
                for item in msg_list:
                    if isinstance(item, dict):
                        role = item.get("role", item.get("type", "user"))
                        content = item.get("content", item.get("text", ""))
                        if isinstance(content, list):
                            text_parts = [p.get("text", "") for p in content if isinstance(p, dict)]
                            content = "\n".join(text_parts)
                        if content:
                            messages.append(Message(
                                role=role,
                                content=str(content),
                                timestamp=item.get("timestamp", 0),
                                token_count=count_tokens_approx(str(content)),
                                model=item.get("model", "")
                            ))
                if messages:
                    break

        if not messages:
            return None

        session.messages = messages
        session.total_tokens = sum(m.token_count for m in messages)
        if messages:
            session.start_time = messages[0].timestamp
            session.end_time = messages[-1].timestamp

        return session

    def _parse_text_file(self, filepath: Path) -> Optional[Session]:
        """Parse text/log file as a simple session."""
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except (IOError, UnicodeDecodeError):
            return None

        if not content.strip():
            return None

        lines = [l.strip() for l in content.splitlines() if l.strip()]
        if not lines:
            return None

        messages = []
        for line in lines[:500]:  # Limit to 500 lines
            messages.append(Message(
                role="user" if "?" in line else "assistant",
                content=line,
                token_count=count_tokens_approx(line)
            ))

        session = Session(
            session_id=generate_session_id(filepath.name),
            agent_type=self.agent_type,
            messages=messages,
            total_tokens=sum(m.token_count for m in messages),
            metadata={"source_file": str(filepath)}
        )

        stat = filepath.stat()
        session.start_time = stat.st_ctime
        session.end_time = stat.st_mtime

        return session


# Parser registry
PARSER_REGISTRY: Dict[str, BaseParser] = {
    "claude-code": ClaudeCodeParser(),
    "cursor": CursorParser(),
    "trae": TraeParser(),
    "generic": GenericParser(),
}


def get_parser(agent_type: str) -> BaseParser:
    """Get parser for agent type."""
    return PARSER_REGISTRY.get(agent_type, GenericParser())


def detect_agent_type(filepath: Path) -> str:
    """Detect agent type from file path and content."""
    path_str = str(filepath).lower()

    if ".claude" in path_str:
        return "claude-code"
    elif ".cursor" in path_str:
        return "cursor"
    elif ".trae" in path_str:
        return "trae"
    elif ".windsurf" in path_str:
        return "windsurf"
    elif ".aider" in path_str:
        return "aider"
    elif ".continue" in path_str:
        return "continue"
    elif ".copilot" in path_str:
        return "copilot"
    elif ".lingma" in path_str:
        return "tongyi-lingma"
    elif ".codeium" in path_str:
        return "codeium"
    else:
        return "generic"
