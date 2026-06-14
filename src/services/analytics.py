"""
Analytics service for generating insights from session data.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.database import SessionModel, CommandLog


class AnalyticsService:
    """Service for computing analytics."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_summary(self) -> Dict[str, Any]:
        """Get overall analytics summary."""
        total_sessions = self.db.query(SessionModel).count()
        
        if total_sessions == 0:
            return {
                "total_sessions": 0,
                "total_duration_seconds": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "total_commands": 0,
                "total_errors": 0,
                "avg_session_duration": 0.0,
                "avg_tokens_per_session": 0.0,
                "top_agents": [],
                "daily_stats": [],
            }
        
        # Aggregate stats
        stats = self.db.query(
            func.sum(SessionModel.duration_seconds).label("total_duration"),
            func.sum(SessionModel.total_tokens).label("total_tokens"),
            func.sum(SessionModel.estimated_cost).label("total_cost"),
            func.sum(SessionModel.command_count).label("total_commands"),
            func.sum(SessionModel.error_count).label("total_errors"),
            func.avg(SessionModel.duration_seconds).label("avg_duration"),
            func.avg(SessionModel.total_tokens).label("avg_tokens"),
        ).first()
        
        # Top agents by session count
        top_agents = self.db.query(
            SessionModel.agent_type,
            func.count(SessionModel.id).label("count"),
            func.sum(SessionModel.total_tokens).label("tokens"),
        ).group_by(SessionModel.agent_type).order_by(func.count(SessionModel.id).desc()).limit(10).all()
        
        # Daily stats for last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily = self.db.query(
            func.date(SessionModel.start_time).label("date"),
            func.count(SessionModel.id).label("sessions"),
            func.sum(SessionModel.total_tokens).label("tokens"),
            func.sum(SessionModel.estimated_cost).label("cost"),
        ).filter(SessionModel.start_time >= thirty_days_ago).group_by(
            func.date(SessionModel.start_time)
        ).order_by(func.date(SessionModel.start_time)).all()
        
        return {
            "total_sessions": total_sessions,
            "total_duration_seconds": stats.total_duration or 0,
            "total_tokens": stats.total_tokens or 0,
            "total_cost": round(stats.total_cost or 0, 4),
            "total_commands": stats.total_commands or 0,
            "total_errors": stats.total_errors or 0,
            "avg_session_duration": round(stats.avg_duration or 0, 2),
            "avg_tokens_per_session": round(stats.avg_tokens or 0, 2),
            "top_agents": [
                {"agent": a.agent_type, "sessions": a.count, "tokens": a.tokens or 0}
                for a in top_agents
            ],
            "daily_stats": [
                {"date": str(d.date), "sessions": d.sessions, "tokens": d.tokens or 0, "cost": round(d.cost or 0, 4)}
                for d in daily
            ],
        }
    
    def get_agent_type_stats(self) -> List[Dict[str, Any]]:
        """Get statistics grouped by agent type."""
        results = self.db.query(
            SessionModel.agent_type,
            func.count(SessionModel.id).label("sessions"),
            func.sum(SessionModel.duration_seconds).label("duration"),
            func.sum(SessionModel.total_tokens).label("tokens"),
            func.sum(SessionModel.estimated_cost).label("cost"),
            func.avg(SessionModel.command_count).label("avg_commands"),
        ).group_by(SessionModel.agent_type).all()
        
        return [
            {
                "agent_type": r.agent_type,
                "sessions": r.sessions,
                "total_duration": r.duration or 0,
                "total_tokens": r.tokens or 0,
                "total_cost": round(r.cost or 0, 4),
                "avg_commands": round(r.avg_commands or 0, 2),
            }
            for r in results
        ]
    
    def get_daily_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily statistics."""
        since = datetime.utcnow() - timedelta(days=days)
        results = self.db.query(
            func.date(SessionModel.start_time).label("date"),
            func.count(SessionModel.id).label("sessions"),
            func.sum(SessionModel.duration_seconds).label("duration"),
            func.sum(SessionModel.total_tokens).label("tokens"),
            func.sum(SessionModel.estimated_cost).label("cost"),
            func.sum(SessionModel.command_count).label("commands"),
        ).filter(SessionModel.start_time >= since).group_by(
            func.date(SessionModel.start_time)
        ).order_by(func.date(SessionModel.start_time)).all()
        
        return [
            {
                "date": str(r.date),
                "sessions": r.sessions,
                "duration": r.duration or 0,
                "tokens": r.tokens or 0,
                "cost": round(r.cost or 0, 4),
                "commands": r.commands or 0,
            }
            for r in results
        ]
    
    def get_cost_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get cost trends over time."""
        since = datetime.utcnow() - timedelta(days=days)
        results = self.db.query(
            func.date(SessionModel.start_time).label("date"),
            func.sum(SessionModel.estimated_cost).label("cost"),
            func.sum(SessionModel.input_tokens).label("input_tokens"),
            func.sum(SessionModel.output_tokens).label("output_tokens"),
        ).filter(SessionModel.start_time >= since).group_by(
            func.date(SessionModel.start_time)
        ).order_by(func.date(SessionModel.start_time)).all()
        
        return [
            {
                "date": str(r.date),
                "cost": round(r.cost or 0, 4),
                "input_tokens": r.input_tokens or 0,
                "output_tokens": r.output_tokens or 0,
            }
            for r in results
        ]
