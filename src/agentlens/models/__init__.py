"""
Data models for AgentLens session analysis.
"""

import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional, Any


class AgentType(Enum):
    """Supported AI coding agent types."""
    CLAUDE_CODE = "claude-code"
    CURSOR = "cursor"
    WINDSURF = "windsurf"
    COPILOT = "copilot"
    TRAE = "trae"
    TONGYI_LINGMA = "tongyi-lingma"
    CODEIUM = "codeium"
    CONTINUE = "continue"
    TABBY = "tabby"
    AIDER = "aider"
    UNKNOWN = "unknown"


class SessionStatus(Enum):
    """Session execution status."""
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class Message:
    """Single message in a session."""
    role: str  # user, assistant, system
    content: str
    timestamp: float = 0.0
    token_count: int = 0
    model: str = ""
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ToolUsage:
    """Tool usage record."""
    tool_name: str
    call_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FileChange:
    """File change record."""
    file_path: str
    action: str  # create, modify, delete
    lines_added: int = 0
    lines_removed: int = 0
    language: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CostRecord:
    """Token cost record."""
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Session:
    """A complete agent session."""
    session_id: str = ""
    agent_type: AgentType = AgentType.UNKNOWN
    start_time: float = 0.0
    end_time: float = 0.0
    status: SessionStatus = SessionStatus.UNKNOWN
    messages: List[Message] = field(default_factory=list)
    tool_usages: List[ToolUsage] = field(default_factory=list)
    file_changes: List[FileChange] = field(default_factory=list)
    cost_records: List[CostRecord] = field(default_factory=list)
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return 0.0

    @property
    def message_count(self) -> int:
        return len(self.messages)

    @property
    def tool_call_count(self) -> int:
        return sum(t.call_count for t in self.tool_usages)

    @property
    def files_changed_count(self) -> int:
        return len(self.file_changes)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["agent_type"] = self.agent_type.value
        data["status"] = self.status.value
        data["duration_seconds"] = self.duration_seconds
        data["message_count"] = self.message_count
        data["tool_call_count"] = self.tool_call_count
        data["files_changed_count"] = self.files_changed_count
        return data

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class AnalysisResult:
    """Complete analysis result for sessions."""
    total_sessions: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_duration_seconds: float = 0.0
    total_messages: int = 0
    total_tool_calls: int = 0
    total_files_changed: int = 0
    agent_distribution: Dict[str, int] = field(default_factory=dict)
    model_distribution: Dict[str, int] = field(default_factory=dict)
    daily_usage: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    top_tools: List[Dict[str, Any]] = field(default_factory=list)
    cost_by_model: Dict[str, float] = field(default_factory=dict)
    sessions: List[Session] = field(default_factory=list)
    optimization_tips: List[str] = field(default_factory=list)
    analyzed_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
