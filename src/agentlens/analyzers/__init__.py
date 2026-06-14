"""
Session analyzers for AgentLens.
Provides intelligent analysis of parsed session data.
"""

import time
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from ..models import (
    Session, AnalysisResult, AgentType, SessionStatus,
    Message, ToolUsage, CostRecord
)
from ..utils import (
    format_cost, format_duration, format_number,
    get_date_key, format_timestamp, count_tokens_approx
)


class SessionAnalyzer:
    """Core session analyzer."""

    def analyze(self, sessions: List[Session]) -> AnalysisResult:
        """Perform comprehensive analysis on sessions."""
        result = AnalysisResult(sessions=sessions)
        result.total_sessions = len(sessions)

        if not sessions:
            result.optimization_tips = [
                "No sessions found. Point AgentLens to your agent data directory.",
            ]
            return result

        # Aggregate statistics
        total_tokens = 0
        total_cost = 0.0
        total_duration = 0.0
        total_messages = 0
        total_tool_calls = 0
        total_files_changed = 0
        agent_counter = Counter()
        model_counter = Counter()
        cost_by_model = defaultdict(float)
        daily_usage = defaultdict(lambda: {
            "sessions": 0, "tokens": 0, "cost": 0.0,
            "messages": 0, "tool_calls": 0, "duration": 0.0
        })
        tool_counter = Counter()

        for session in sessions:
            total_tokens += session.total_tokens
            total_cost += session.total_cost_usd
            total_duration += session.duration_seconds
            total_messages += session.message_count
            total_tool_calls += session.tool_call_count
            total_files_changed += session.files_changed_count

            # Agent distribution
            agent_name = session.agent_type.value
            agent_counter[agent_name] += 1

            # Model distribution
            for cost_rec in session.cost_records:
                model_counter[cost_rec.model] += 1
                cost_by_model[cost_rec.model] += cost_rec.estimated_cost_usd

            # Also count models from messages
            for msg in session.messages:
                if msg.model:
                    model_counter[msg.model] += 1

            # Daily usage
            date_key = get_date_key(session.start_time) if session.start_time else "unknown"
            daily_usage[date_key]["sessions"] += 1
            daily_usage[date_key]["tokens"] += session.total_tokens
            daily_usage[date_key]["cost"] += session.total_cost_usd
            daily_usage[date_key]["messages"] += session.message_count
            daily_usage[date_key]["tool_calls"] += session.tool_call_count
            daily_usage[date_key]["duration"] += session.duration_seconds

            # Tool usage
            for tool in session.tool_usages:
                tool_counter[tool.tool_name] += tool.call_count

        result.total_tokens = total_tokens
        result.total_cost_usd = total_cost
        result.total_duration_seconds = total_duration
        result.total_messages = total_messages
        result.total_tool_calls = total_tool_calls
        result.total_files_changed = total_files_changed
        result.agent_distribution = dict(agent_counter.most_common())
        result.model_distribution = dict(model_counter.most_common())
        result.daily_usage = dict(daily_usage)
        result.cost_by_model = dict(cost_by_model)

        # Top tools
        result.top_tools = [
            {"name": name, "calls": count}
            for name, count in tool_counter.most_common(20)
        ]

        # Generate optimization tips
        result.optimization_tips = self._generate_tips(
            sessions, total_tokens, total_cost, total_duration,
            tool_counter, model_counter, daily_usage
        )

        return result

    def _generate_tips(
        self,
        sessions: List[Session],
        total_tokens: int,
        total_cost: float,
        total_duration: float,
        tool_counter: Counter,
        model_counter: Counter,
        daily_usage: Dict,
    ) -> List[str]:
        """Generate cost and usage optimization tips."""
        tips = []

        # Cost optimization
        if total_cost > 10:
            tips.append(
                f"High spend alert: ${total_cost:.2f} total. Consider using cheaper models "
                f"for routine tasks (e.g., Claude Haiku or GPT-4o-mini)."
            )

        # Model mixing suggestion
        if len(model_counter) == 1:
            tips.append(
                "You're using only one model. Consider mixing models: "
                "use cheaper models for simple tasks and premium models for complex ones."
            )

        # Session length optimization
        avg_msgs = sum(s.message_count for s in sessions) / max(len(sessions), 1)
        if avg_msgs > 50:
            tips.append(
                f"Average {avg_msgs:.0f} messages per session. Consider breaking large tasks "
                f"into smaller, focused sessions to reduce context overhead."
            )

        # Tool usage patterns
        if tool_counter:
            top_tool = tool_counter.most_common(1)[0]
            if top_tool[1] > 100:
                tips.append(
                    f"Tool '{top_tool[0]}' called {top_tool[1]} times. "
                    f"Consider batching similar operations to reduce redundant calls."
                )

        # Daily patterns
        if len(daily_usage) > 7:
            tips.append(
                "Active usage detected over 7+ days. Consider setting weekly budget limits "
                "to track and control AI coding costs."
            )

        # Token efficiency
        if total_tokens > 0 and total_cost > 0:
            cost_per_1k_tokens = (total_cost / total_tokens) * 1000
            if cost_per_1k_tokens > 0.01:
                tips.append(
                    f"Cost per 1K tokens: ${cost_per_1k_tokens:.4f}. "
                    f"Switching to a more cost-effective model could save up to 60%."
                )

        if not tips:
            tips.append("Usage looks efficient! Keep up the good work.")

        return tips


class CostAnalyzer:
    """Detailed cost analysis."""

    def analyze_cost_trend(self, sessions: List[Session]) -> List[Dict[str, Any]]:
        """Analyze cost trends over time."""
        daily_costs = defaultdict(float)
        for session in sessions:
            date_key = get_date_key(session.start_time)
            daily_costs[date_key] += session.total_cost_usd

        trend = []
        for date in sorted(daily_costs.keys()):
            trend.append({
                "date": date,
                "cost": daily_costs[date],
                "cost_formatted": format_cost(daily_costs[date])
            })

        return trend

    def analyze_model_efficiency(self, sessions: List[Session]) -> List[Dict[str, Any]]:
        """Analyze cost efficiency by model."""
        model_stats = defaultdict(lambda: {
            "sessions": 0, "tokens": 0, "cost": 0.0, "messages": 0
        })

        for session in sessions:
            for cost_rec in session.cost_records:
                model = cost_rec.model
                model_stats[model]["sessions"] += 1
                model_stats[model]["tokens"] += cost_rec.total_tokens
                model_stats[model]["cost"] += cost_rec.estimated_cost_usd
                model_stats[model]["messages"] += session.message_count

        results = []
        for model, stats in sorted(model_stats.items(), key=lambda x: -x[1]["cost"]):
            cost_per_msg = stats["cost"] / max(stats["messages"], 1)
            cost_per_token = stats["cost"] / max(stats["tokens"], 1) * 1_000_000
            results.append({
                "model": model,
                "sessions": stats["sessions"],
                "total_tokens": stats["tokens"],
                "total_cost": stats["cost"],
                "cost_formatted": format_cost(stats["cost"]),
                "cost_per_message": cost_per_msg,
                "cost_per_1m_tokens": cost_per_token,
            })

        return results

    def project_monthly_cost(self, sessions: List[Session]) -> Dict[str, Any]:
        """Project monthly cost based on current usage pattern."""
        if not sessions:
            return {"projected_monthly": 0, "confidence": "low"}

        total_cost = sum(s.total_cost_usd for s in sessions)
        date_keys = set()
        for s in sessions:
            if s.start_time:
                date_keys.add(get_date_key(s.start_time))

        unique_days = max(len(date_keys), 1)
        daily_avg = total_cost / unique_days
        projected_monthly = daily_avg * 30

        confidence = "high" if unique_days >= 14 else ("medium" if unique_days >= 7 else "low")

        return {
            "total_cost": total_cost,
            "unique_days": unique_days,
            "daily_average": daily_avg,
            "projected_monthly": projected_monthly,
            "projected_monthly_formatted": format_cost(projected_monthly),
            "confidence": confidence,
        }


class UsageAnalyzer:
    """Usage pattern analysis."""

    def analyze_peak_hours(self, sessions: List[Session]) -> List[Dict[str, Any]]:
        """Analyze usage by hour of day."""
        hour_counter = Counter()
        for session in sessions:
            if session.start_time:
                try:
                    hour = datetime.fromtimestamp(session.start_time).hour
                    hour_counter[hour] += 1
                except (OSError, ValueError):
                    continue

        return [
            {"hour": h, "sessions": c, "label": f"{h:02d}:00-{h:02d}:59"}
            for h, c in sorted(hour_counter.items())
        ]

    def analyze_agent_preferences(self, sessions: List[Session]) -> List[Dict[str, Any]]:
        """Analyze agent usage preferences."""
        agent_stats = defaultdict(lambda: {
            "sessions": 0, "tokens": 0, "cost": 0.0, "messages": 0
        })

        for session in sessions:
            agent = session.agent_type.value
            agent_stats[agent]["sessions"] += 1
            agent_stats[agent]["tokens"] += session.total_tokens
            agent_stats[agent]["cost"] += session.total_cost_usd
            agent_stats[agent]["messages"] += session.message_count

        return [
            {"agent": agent, **stats}
            for agent, stats in sorted(agent_stats.items(), key=lambda x: -x[1]["sessions"])
        ]

    def analyze_session_lengths(self, sessions: List[Session]) -> Dict[str, Any]:
        """Analyze session length distribution."""
        if not sessions:
            return {}

        lengths = [s.message_count for s in sessions]
        durations = [s.duration_seconds for s in sessions if s.duration_seconds > 0]

        stats = {
            "message_count": {
                "min": min(lengths),
                "max": max(lengths),
                "avg": sum(lengths) / len(lengths),
                "median": sorted(lengths)[len(lengths) // 2],
            }
        }

        if durations:
            stats["duration_seconds"] = {
                "min": min(durations),
                "max": max(durations),
                "avg": sum(durations) / len(durations),
                "median": sorted(durations)[len(durations) // 2],
                "avg_formatted": format_duration(sum(durations) / len(durations)),
            }

        return stats
