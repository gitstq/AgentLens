"""
Exporters for AgentLens analysis results.
Supports JSON, CSV, Markdown, and SARIF formats.
"""

import csv
import io
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..models import AnalysisResult, Session
from ..utils import (
    format_cost, format_duration, format_number,
    format_timestamp, get_date_key
)


class BaseExporter:
    """Base exporter class."""

    format_name: str = "unknown"
    file_extension: str = ".txt"

    def export(self, result: AnalysisResult, output_path: Optional[Path] = None) -> str:
        """Export analysis result. Returns content string."""
        raise NotImplementedError

    def write(self, result: AnalysisResult, output_path: Path) -> Path:
        """Write export to file."""
        content = self.export(result)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        return output_path


class JSONExporter(BaseExporter):
    """Export as JSON."""

    format_name = "json"
    file_extension = ".json"

    def export(self, result: AnalysisResult, output_path: Optional[Path] = None) -> str:
        return result.to_json(indent=2)


class CSVExporter(BaseExporter):
    """Export as CSV."""

    format_name = "csv"
    file_extension = ".csv"

    def export(self, result: AnalysisResult, output_path: Optional[Path] = None) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        # Summary header
        writer.writerow(["AgentLens Analysis Report"])
        writer.writerow(["Generated", datetime.now().isoformat()])
        writer.writerow([])

        # Overview
        writer.writerow(["=== Overview ==="])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Sessions", result.total_sessions])
        writer.writerow(["Total Tokens", result.total_tokens])
        writer.writerow(["Total Cost (USD)", f"{result.total_cost_usd:.6f}"])
        writer.writerow(["Total Duration (s)", f"{result.total_duration_seconds:.1f}"])
        writer.writerow(["Total Messages", result.total_messages])
        writer.writerow(["Total Tool Calls", result.total_tool_calls])
        writer.writerow(["Total Files Changed", result.total_files_changed])
        writer.writerow([])

        # Agent Distribution
        if result.agent_distribution:
            writer.writerow(["=== Agent Distribution ==="])
            writer.writerow(["Agent", "Sessions"])
            for agent, count in result.agent_distribution.items():
                writer.writerow([agent, count])
            writer.writerow([])

        # Model Distribution
        if result.model_distribution:
            writer.writerow(["=== Model Distribution ==="])
            writer.writerow(["Model", "Sessions"])
            for model, count in result.model_distribution.items():
                writer.writerow([model, count])
            writer.writerow([])

        # Cost by Model
        if result.cost_by_model:
            writer.writerow(["=== Cost by Model ==="])
            writer.writerow(["Model", "Cost (USD)"])
            for model, cost in sorted(result.cost_by_model.items(), key=lambda x: -x[1]):
                writer.writerow([model, f"{cost:.6f}"])
            writer.writerow([])

        # Daily Usage
        if result.daily_usage:
            writer.writerow(["=== Daily Usage ==="])
            writer.writerow(["Date", "Sessions", "Tokens", "Cost (USD)", "Messages", "Tool Calls"])
            for date, data in sorted(result.daily_usage.items()):
                writer.writerow([
                    date, data["sessions"], data["tokens"],
                    f"{data['cost']:.6f}", data["messages"], data["tool_calls"]
                ])
            writer.writerow([])

        # Top Tools
        if result.top_tools:
            writer.writerow(["=== Top Tools ==="])
            writer.writerow(["Tool", "Calls"])
            for tool in result.top_tools:
                writer.writerow([tool["name"], tool["calls"]])
            writer.writerow([])

        # Session Details
        if result.sessions:
            writer.writerow(["=== Session Details ==="])
            writer.writerow([
                "Session ID", "Agent", "Messages", "Tokens",
                "Cost (USD)", "Duration (s)", "Status"
            ])
            for s in result.sessions:
                writer.writerow([
                    s.session_id, s.agent_type.value, s.message_count,
                    s.total_tokens, f"{s.total_cost_usd:.6f}",
                    f"{s.duration_seconds:.1f}", s.status.value
                ])

        return output.getvalue()


class MarkdownExporter(BaseExporter):
    """Export as Markdown."""

    format_name = "markdown"
    file_extension = ".md"

    def export(self, result: AnalysisResult, output_path: Optional[Path] = None) -> str:
        lines = []

        # Header
        lines.append("# AgentLens Analysis Report")
        lines.append(f"\n> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Overview
        lines.append("## Overview\n")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Total Sessions | {result.total_sessions} |")
        lines.append(f"| Total Tokens | {format_number(result.total_tokens)} |")
        lines.append(f"| Total Cost | {format_cost(result.total_cost_usd)} |")
        lines.append(f"| Total Duration | {format_duration(result.total_duration_seconds)} |")
        lines.append(f"| Total Messages | {format_number(result.total_messages)} |")
        lines.append(f"| Total Tool Calls | {format_number(result.total_tool_calls)} |")
        lines.append(f"| Files Changed | {result.total_files_changed} |")
        lines.append("")

        # Agent Distribution
        if result.agent_distribution:
            lines.append("## Agent Distribution\n")
            lines.append("| Agent | Sessions |")
            lines.append("|-------|----------|")
            for agent, count in result.agent_distribution.items():
                lines.append(f"| {agent} | {count} |")
            lines.append("")

        # Model Distribution
        if result.model_distribution:
            lines.append("## Model Distribution\n")
            lines.append("| Model | Sessions |")
            lines.append("|-------|----------|")
            for model, count in result.model_distribution.items():
                lines.append(f"| {model} | {count} |")
            lines.append("")

        # Cost by Model
        if result.cost_by_model:
            lines.append("## Cost by Model\n")
            lines.append("| Model | Cost |")
            lines.append("|-------|------|")
            for model, cost in sorted(result.cost_by_model.items(), key=lambda x: -x[1]):
                lines.append(f"| {model} | {format_cost(cost)} |")
            lines.append("")

        # Daily Usage
        if result.daily_usage:
            lines.append("## Daily Usage\n")
            lines.append("| Date | Sessions | Tokens | Cost | Messages |")
            lines.append("|------|----------|--------|------|----------|")
            for date, data in sorted(result.daily_usage.items()):
                lines.append(
                    f"| {date} | {data['sessions']} | {format_number(data['tokens'])} "
                    f"| {format_cost(data['cost'])} | {data['messages']} |"
                )
            lines.append("")

        # Top Tools
        if result.top_tools:
            lines.append("## Top Tools\n")
            lines.append("| Tool | Calls |")
            lines.append("|------|-------|")
            for tool in result.top_tools[:15]:
                lines.append(f"| {tool['name']} | {tool['calls']} |")
            lines.append("")

        # Optimization Tips
        if result.optimization_tips:
            lines.append("## Optimization Tips\n")
            for tip in result.optimization_tips:
                lines.append(f"- {tip}")
            lines.append("")

        return "\n".join(lines)


class SARIFExporter(BaseExporter):
    """Export as SARIF (Static Analysis Results Interchange Format)."""

    format_name = "sarif"
    file_extension = ".sarif"

    def export(self, result: AnalysisResult, output_path: Optional[Path] = None) -> str:
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "AgentLens",
                        "version": "1.0.0",
                        "informationUri": "https://github.com/gitstq/AgentLens",
                        "rules": [
                            {
                                "id": "AL001",
                                "shortDescription": {"text": "High Cost Session"},
                                "fullDescription": {"text": "Session with unusually high cost detected"},
                                "defaultConfiguration": {"level": "warning"}
                            },
                            {
                                "id": "AL002",
                                "shortDescription": {"text": "Long Session"},
                                "fullDescription": {"text": "Session with excessive message count"},
                                "defaultConfiguration": {"level": "note"}
                            },
                            {
                                "id": "AL003",
                                "shortDescription": {"text": "Cost Optimization Opportunity"},
                                "fullDescription": {"text": "Potential cost savings identified"},
                                "defaultConfiguration": {"level": "note"}
                            }
                        ]
                    }
                },
                "results": []
            }]
        }

        results = sarif["runs"][0]["results"]

        # Flag high-cost sessions
        if result.sessions:
            avg_cost = result.total_cost_usd / max(result.total_sessions, 1)
            for session in result.sessions:
                if session.total_cost_usd > avg_cost * 2:
                    results.append({
                        "ruleId": "AL001",
                        "level": "warning",
                        "message": {
                            "text": f"High cost session: {session.session_id} "
                                    f"(${session.total_cost_usd:.4f}, "
                                    f"{session.message_count} messages)"
                        },
                        "properties": {
                            "agent": session.agent_type.value,
                            "cost": session.total_cost_usd,
                            "messages": session.message_count,
                        }
                    })

                if session.message_count > 50:
                    results.append({
                        "ruleId": "AL002",
                        "level": "note",
                        "message": {
                            "text": f"Long session: {session.session_id} "
                                    f"({session.message_count} messages)"
                        }
                    })

        # Add optimization tips as results
        for tip in result.optimization_tips:
            results.append({
                "ruleId": "AL003",
                "level": "note",
                "message": {"text": tip}
            })

        return json.dumps(sarif, indent=2, ensure_ascii=False)


# Exporter registry
EXPORTER_REGISTRY: Dict[str, BaseExporter] = {
    "json": JSONExporter(),
    "csv": CSVExporter(),
    "markdown": MarkdownExporter(),
    "md": MarkdownExporter(),
    "sarif": SARIFExporter(),
}


def get_exporter(format_name: str) -> BaseExporter:
    """Get exporter by format name."""
    return EXPORTER_REGISTRY.get(format_name.lower(), JSONExporter())


def export_result(result: AnalysisResult, format_name: str, output_path: Optional[Path] = None) -> str:
    """Export analysis result in specified format."""
    exporter = get_exporter(format_name)
    content = exporter.export(result)

    if output_path:
        exporter.write(result, output_path)

    return content
