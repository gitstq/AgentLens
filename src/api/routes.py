"""
API routes for AgentLens.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db, SessionModel, CommandLog
from src.core.models import (
    SessionCreate, SessionUpdate, SessionResponse,
    CommandLogCreate, CommandLogResponse,
    AnalyticsSummary, CostEstimate
)
from src.services.analytics import AnalyticsService
from src.services.cost_calculator import CostCalculator

router = APIRouter()


# Session routes
@router.post("/sessions", response_model=SessionResponse)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """Create a new AI agent session."""
    db_session = SessionModel(
        session_id=str(uuid.uuid4())[:16],
        agent_type=session.agent_type,
        agent_version=session.agent_version,
        project_name=session.project_name,
        tags=session.tags,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions", response_model=List[SessionResponse])
def list_sessions(
    agent_type: Optional[str] = None,
    project_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all sessions with optional filtering."""
    query = db.query(SessionModel)
    if agent_type:
        query = query.filter(SessionModel.agent_type == agent_type)
    if project_name:
        query = query.filter(SessionModel.project_name.contains(project_name))
    return query.order_by(SessionModel.start_time.desc()).offset(skip).limit(limit).all()


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get a specific session by ID."""
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/sessions/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: str,
    update: SessionUpdate,
    db: Session = Depends(get_db)
):
    """Update session information."""
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    # Recalculate total tokens and cost
    if session.input_tokens or session.output_tokens:
        session.total_tokens = session.input_tokens + session.output_tokens
        session.estimated_cost = CostCalculator.calculate(
            session.input_tokens, session.output_tokens
        )
    
    db.commit()
    db.refresh(session)
    return session


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a session and its logs."""
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.query(CommandLog).filter(CommandLog.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    return {"message": "Session deleted successfully"}


# Command log routes
@router.post("/commands", response_model=CommandLogResponse)
def log_command(command: CommandLogCreate, db: Session = Depends(get_db)):
    """Log a command within a session."""
    session = db.query(SessionModel).filter(
        SessionModel.session_id == command.session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db_command = CommandLog(**command.model_dump())
    db.add(db_command)
    
    # Update session stats
    session.command_count += 1
    if command.tokens_used:
        session.total_tokens += command.tokens_used
    
    db.commit()
    db.refresh(db_command)
    return db_command


@router.get("/commands/{session_id}", response_model=List[CommandLogResponse])
def list_commands(
    session_id: str,
    skip: int = 0,
    limit: int = 500,
    db: Session = Depends(get_db)
):
    """List all commands for a session."""
    return db.query(CommandLog).filter(
        CommandLog.session_id == session_id
    ).order_by(CommandLog.timestamp).offset(skip).limit(limit).all()


# Analytics routes
@router.get("/analytics/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    """Get overall analytics summary."""
    service = AnalyticsService(db)
    return service.get_summary()


@router.get("/analytics/agent-types")
def get_agent_type_stats(db: Session = Depends(get_db)):
    """Get statistics grouped by agent type."""
    service = AnalyticsService(db)
    return service.get_agent_type_stats()


@router.get("/analytics/daily")
def get_daily_stats(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get daily statistics for the last N days."""
    service = AnalyticsService(db)
    return service.get_daily_stats(days)


@router.get("/analytics/cost-trends")
def get_cost_trends(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get cost trends over time."""
    service = AnalyticsService(db)
    return service.get_cost_trends(days)


# Cost calculator
@router.post("/cost/estimate")
def estimate_cost(estimate: CostEstimate):
    """Estimate cost based on token usage."""
    cost = CostCalculator.calculate(
        estimate.input_tokens,
        estimate.output_tokens,
        estimate.price_per_1k_input,
        estimate.price_per_1k_output,
    )
    return {
        "input_tokens": estimate.input_tokens,
        "output_tokens": estimate.output_tokens,
        "estimated_cost": cost,
        "currency": "USD",
    }


# Health check
@router.get("/health")
def health_check():
    """API health check."""
    return {"status": "healthy", "version": "1.0.0"}
