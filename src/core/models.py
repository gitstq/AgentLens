"""
Pydantic models for API requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """Create a new session."""
    agent_type: str = Field(..., description="AI agent type: claude, cursor, codex, etc.")
    agent_version: Optional[str] = None
    project_name: Optional[str] = None
    tags: Optional[str] = None


class SessionUpdate(BaseModel):
    """Update session information."""
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    command_count: Optional[int] = None
    file_changes: Optional[int] = None
    error_count: Optional[int] = None
    session_data: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Session response model."""
    id: int
    session_id: str
    agent_type: str
    agent_version: Optional[str]
    project_name: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    command_count: int
    file_changes: int
    error_count: int
    tags: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommandLogCreate(BaseModel):
    """Create a command log entry."""
    session_id: str
    command: str
    response: Optional[str] = None
    duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    command_type: Optional[str] = None


class CommandLogResponse(BaseModel):
    """Command log response."""
    id: int
    session_id: str
    command: str
    response: Optional[str]
    timestamp: datetime
    duration_ms: int
    tokens_used: int
    command_type: Optional[str]
    
    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    """Analytics summary response."""
    total_sessions: int
    total_duration_seconds: int
    total_tokens: int
    total_cost: float
    total_commands: int
    total_errors: int
    avg_session_duration: float
    avg_tokens_per_session: float
    top_agents: List[Dict[str, Any]]
    daily_stats: List[Dict[str, Any]]


class CostEstimate(BaseModel):
    """Cost estimation request/response."""
    input_tokens: int
    output_tokens: int
    price_per_1k_input: float = 0.01
    price_per_1k_output: float = 0.03
    estimated_cost: Optional[float] = None
