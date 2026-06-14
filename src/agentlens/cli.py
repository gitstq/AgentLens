#!/usr/bin/env python3
"""
AgentLens CLI - Main entry point.
Lightweight AI Coding Agent Session Intelligence Analysis Engine.

Usage:
    agentlens scan [--path PATH] [--agent AGENT] [--max-files N] [--format FMT]
    agentlens dashboard [--path PATH] [--agent AGENT]
    agentlens export [--path PATH] [--format FMT] [--output FILE]
    agentlens sessions [--path PATH] [--limit N]
    agentlens cost [--path PATH]
    agentlens agents
    agentlens version
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentlens.models import AnalysisResult, Session
from agentlens.parsers import (
    get_parser, detect_agent_type, PARSER_REGISTRY
)
from agentlens.utils import (
    find_agent_data_dirs, scan_session_files, expand_path
)
from agentlens.analyzers import SessionAnalyzer, CostAnalyzer, UsageAnalyzer
from agentlens.exporters import export_result, EXPORTER_REGISTRY
from agentlens.ui import (
    print_banner, render_dashboard, render_session_list,
    render_summary_line, bold, cyan, green, yellow, red, dim
)
from agentlens.utils import expand_path, format_cost, format_duration, format_number
from agentlens import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="agentlens",
        description="AgentLens - Lightweight AI Coding Agent Session Intelligence Analysis Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agentlens scan                          Scan default agent directories
  agentlens scan --path ~/.claude         Scan specific directory
  agentlens scan --agent claude-code      Scan Claude Code sessions
  agentlens dashboard                     Show analysis dashboard
  agentlens export --format markdown      Export as Markdown
  agentlens export --format csv -o report.csv
  agentlens sessions --limit 10           List recent sessions
  agentlens cost                           Show cost analysis
  agentlens agents                         List detected agents
"""
    )

    parser.add_argument("--version", action="version", version=f"AgentLens v{__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # scan command
    scan_p = subparsers.add_parser("scan", help="Scan and analyze agent sessions")
    scan_p.add_argument("--path", "-p", type=str, help="Path to scan (default: auto-detect)")
    scan_p.add_argument("--agent", "-a", type=str, help="Agent type to scan")
    scan_p.add_argument("--max-files", "-m", type=int, default=100, help="Max files to parse")
    scan_p.add_argument("--format", "-f", type=str, default="json", help="Output format")
    scan_p.add_argument("--output", "-o", type=str, help="Output file path")

    # dashboard command
    dash_p = subparsers.add_parser("dashboard", help="Show analysis dashboard")
    dash_p.add_argument("--path", "-p", type=str, help="Path to scan")
    dash_p.add_argument("--agent", "-a", type=str, help="Agent type")

    # export command
    export_p = subparsers.add_parser("export", help="Export analysis results")
    export_p.add_argument("--path", "-p", type=str, help="Path to scan")
    export_p.add_argument("--format", "-f", type=str, default="markdown", help="Export format")
    export_p.add_argument("--output", "-o", type=str, help="Output file path")
    export_p.add_argument("--agent", "-a", type=str, help="Agent type")

    # sessions command
    sess_p = subparsers.add_parser("sessions", help="List sessions")
    sess_p.add_argument("--path", "-p", type=str, help="Path to scan")
    sess_p.add_argument("--limit", "-l", type=int, default=20, help="Max sessions to show")
    sess_p.add_argument("--agent", "-a", type=str, help="Agent type")

    # cost command
    cost_p = subparsers.add_parser("cost", help="Show cost analysis")
    cost_p.add_argument("--path", "-p", type=str, help="Path to scan")
    cost_p.add_argument("--agent", "-a", type=str, help="Agent type")

    # agents command
    subparsers.add_parser("agents", help="List detected agent data directories")

    return parser


def scan_sessions(path: Optional[str] = None, agent_type: Optional[str] = None,
                  max_files: int = 100) -> List[Session]:
    """Scan and parse sessions from the specified path or auto-detected directories."""
    sessions = []

    if path:
        # Scan specific path
        target = expand_path(path)
        if not target.exists():
            print(red(f"Error: Path does not exist: {target}"))
            return []

        detected_type = agent_type or detect_agent_type(target)
        parser = get_parser(detected_type)
        print(dim(f"Scanning: {target} (parser: {detected_type})"))

        if target.is_file():
            session = parser.parse_file(target)
            if session:
                sessions.append(session)
        else:
            sessions = parser.parse_directory(target, max_files=max_files)
    else:
        # Auto-detect agent directories
        agent_dirs = find_agent_data_dirs()
        if not agent_dirs:
            print(yellow("No agent data directories found."))
            print(dim("Supported agents: Claude Code, Cursor, Windsurf, Trae, Copilot, Aider, Continue, Tongyi Lingma"))
            print(dim("Use --path to specify a directory manually."))
            return []

        for agent_name, dirs in agent_dirs.items():
            if agent_type and agent_name != agent_type:
                continue
            parser = get_parser(agent_name)
            for directory in dirs:
                print(dim(f"Scanning {agent_name}: {directory}"))
                found = parser.parse_directory(directory, max_files=max_files)
                sessions.extend(found)

    return sessions


def cmd_scan(args):
    """Execute scan command."""
    sessions = scan_sessions(args.path, args.agent, args.max_files)

    if not sessions:
        print(yellow("No sessions found."))
        return

    analyzer = SessionAnalyzer()
    result = analyzer.analyze(sessions)

    # Output
    if args.output:
        output_path = Path(args.output)
        export_result(result, args.format, output_path)
        print(green(f"Results exported to: {output_path}"))
    elif args.format in ("json",):
        print(result.to_json())
    else:
        export_result(result, args.format)


def cmd_dashboard(args):
    """Execute dashboard command."""
    print_banner()
    sessions = scan_sessions(args.path, args.agent)

    if not sessions:
        print(yellow("No sessions found. Run 'agentlens agents' to check detected directories."))
        return

    analyzer = SessionAnalyzer()
    result = analyzer.analyze(sessions)

    dashboard = render_dashboard(result)
    print(dashboard)

    # Summary
    print(render_summary_line(result))
    print()


def cmd_export(args):
    """Execute export command."""
    sessions = scan_sessions(args.path, args.agent)

    if not sessions:
        print(yellow("No sessions found."))
        return

    analyzer = SessionAnalyzer()
    result = analyzer.analyze(sessions)

    fmt = args.format or "markdown"
    content = export_result(result, fmt)

    if args.output:
        output_path = Path(args.output)
        export_result(result, fmt, output_path)
        print(green(f"Exported to: {output_path}"))
    else:
        print(content)


def cmd_sessions(args):
    """Execute sessions command."""
    sessions = scan_sessions(args.path, args.agent)

    if not sessions:
        print(yellow("No sessions found."))
        return

    # Sort by start time (newest first)
    sessions.sort(key=lambda s: s.start_time, reverse=True)

    print(bold(f"  Recent Sessions (showing {min(len(sessions), args.limit)} of {len(sessions)})"))
    print()
    print(render_session_list(sessions, args.limit))
    print()
    print(render_summary_line(SessionAnalyzer().analyze(sessions)))


def cmd_cost(args):
    """Execute cost command."""
    sessions = scan_sessions(args.path, args.agent)

    if not sessions:
        print(yellow("No sessions found."))
        return

    analyzer = SessionAnalyzer()
    cost_analyzer = CostAnalyzer()
    result = analyzer.analyze(sessions)

    print_banner()
    print(bold("  Cost Analysis"))
    print(dim("  " + "-" * 40))
    print()

    # Total cost
    print(f"  Total Cost:         {bold(green(format_cost(result.total_cost_usd)))}")
    print(f"  Total Tokens:       {bold(yellow(format_number(result.total_tokens)))}")
    print(f"  Avg Cost/Session:   {format_cost(result.total_cost_usd / max(result.total_sessions, 1))}")
    print()

    # Cost trend
    trend = cost_analyzer.analyze_cost_trend(sessions)
    if trend:
        print(bold("  Cost Trend (Daily)"))
        print()
        for item in trend[-7:]:
            bar_len = int(min(item["cost"] * 100, 30))
            bar = "█" * bar_len + "░" * (30 - bar_len)
            print(f"    {item['date']}  {green(bar)} {item['cost_formatted']}")
        print()

    # Model efficiency
    efficiency = cost_analyzer.analyze_model_efficiency(sessions)
    if efficiency:
        print(bold("  Model Efficiency"))
        print()
        for item in efficiency:
            print(f"    {item['model']:<25} {format_cost(item['total_cost']):>10}  "
                  f"({item['sessions']} sessions)")
        print()

    # Monthly projection
    projection = cost_analyzer.project_monthly_cost(sessions)
    print(bold("  Monthly Projection"))
    print()
    print(f"    Projected Monthly:  {bold(yellow(projection['projected_monthly_formatted']))}")
    print(f"    Daily Average:      {format_cost(projection['daily_average'])}")
    print(f"    Confidence:         {projection['confidence']}")
    print()

    # Tips
    if result.optimization_tips:
        print(bold("  Cost Optimization Tips"))
        print()
        for i, tip in enumerate(result.optimization_tips, 1):
            print(f"    {yellow(f'{i}.')} {tip}")
        print()


def cmd_agents(args):
    """Execute agents command."""
    print_banner()
    print(bold("  Detected Agent Data Directories"))
    print()

    agent_dirs = find_agent_data_dirs()

    if not agent_dirs:
        print(yellow("  No agent data directories found."))
        print()
        print(dim("  Supported agents:"))
        for name in PARSER_REGISTRY:
            if name != "generic":
                parser = PARSER_REGISTRY[name]
                print(f"    - {parser.agent_name} ({name})")
        print()
        print(dim("  Use --path to specify a directory manually."))
        return

    for agent_name, dirs in sorted(agent_dirs.items()):
        parser = get_parser(agent_name)
        total_files = 0
        for d in dirs:
            files = scan_session_files(d)
            total_files += len(files)

        status = green(f"{len(dirs)} dir(s), {total_files} file(s)")
        print(f"  {bold(agent_name):<20} {status}")
        for d in dirs:
            print(f"    {dim(str(d))}")
        print()

    print(dim(f"  Total: {sum(len(v) for v in agent_dirs.values())} directories detected"))
    print()


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print()
        print(yellow("Tip: Run 'agentlens agents' to detect installed AI coding agents."))
        return

    commands = {
        "scan": cmd_scan,
        "dashboard": cmd_dashboard,
        "export": cmd_export,
        "sessions": cmd_sessions,
        "cost": cmd_cost,
        "agents": cmd_agents,
    }

    handler = commands.get(args.command)
    if handler:
        try:
            handler(args)
        except KeyboardInterrupt:
            print()
            print(yellow("Interrupted."))
            sys.exit(1)
        except Exception as e:
            print(red(f"Error: {e}"))
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
