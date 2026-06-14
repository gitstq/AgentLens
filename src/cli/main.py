"""
AgentLens CLI - Command line interface for session tracking.
"""

import json
import sys
from datetime import datetime

import click
import requests

from src.core.config import settings

API_BASE = f"http://{settings.HOST}:{settings.PORT}/api/v1"


@click.group()
@click.version_option(version=settings.VERSION, prog_name="agentlens")
def cli():
    """AgentLens - AI Agent Session Analytics CLI"""
    pass


@cli.command()
@click.option("--agent", "-a", required=True, help="Agent type (claude, cursor, codex, etc.)")
@click.option("--version", "-v", help="Agent version")
@click.option("--project", "-p", help="Project name")
@click.option("--tags", "-t", help="Comma-separated tags")
def start(agent: str, version: str = None, project: str = None, tags: str = None):
    """Start a new session."""
    payload = {
        "agent_type": agent,
        "agent_version": version,
        "project_name": project,
        "tags": tags,
    }
    try:
        resp = requests.post(f"{API_BASE}/sessions", json={k: v for k, v in payload.items() if v})
        resp.raise_for_status()
        data = resp.json()
        click.echo(f"✅ Session started: {data['session_id']}")
        click.echo(f"   Agent: {data['agent_type']}")
        click.echo(f"   Time: {data['start_time']}")
    except requests.exceptions.ConnectionError:
        click.echo("❌ Error: Cannot connect to AgentLens server. Is it running?", err=True)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("session_id")
@click.option("--input-tokens", "-i", type=int, help="Input tokens used")
@click.option("--output-tokens", "-o", type=int, help="Output tokens used")
@click.option("--commands", "-c", type=int, help="Total commands executed")
@click.option("--errors", "-e", type=int, help="Error count")
def end(session_id: str, input_tokens: int = None, output_tokens: int = None,
        commands: int = None, errors: int = None):
    """End a session and update stats."""
    payload = {
        "end_time": datetime.utcnow().isoformat(),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "command_count": commands,
        "error_count": errors,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    
    try:
        resp = requests.patch(f"{API_BASE}/sessions/{session_id}", json=payload)
        resp.raise_for_status()
        data = resp.json()
        click.echo(f"✅ Session ended: {session_id}")
        click.echo(f"   Duration: {data['duration_seconds']}s")
        click.echo(f"   Tokens: {data['total_tokens']}")
        click.echo(f"   Cost: ${data['estimated_cost']:.4f}")
    except requests.exceptions.ConnectionError:
        click.echo("❌ Error: Cannot connect to AgentLens server.", err=True)
        sys.exit(1)


@cli.command()
@click.argument("session_id")
@click.argument("command")
@click.option("--response", "-r", help="Command response")
@click.option("--tokens", type=int, help="Tokens used")
@click.option("--type", "cmd_type", help="Command type")
def log(session_id: str, command: str, response: str = None, tokens: int = None, cmd_type: str = None):
    """Log a command to a session."""
    payload = {
        "session_id": session_id,
        "command": command,
        "response": response,
        "tokens_used": tokens,
        "command_type": cmd_type,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    
    try:
        resp = requests.post(f"{API_BASE}/commands", json=payload)
        resp.raise_for_status()
        click.echo(f"✅ Command logged to session {session_id}")
    except requests.exceptions.ConnectionError:
        click.echo("❌ Error: Cannot connect to AgentLens server.", err=True)
        sys.exit(1)


@cli.command()
@click.option("--agent", "-a", help="Filter by agent type")
@click.option("--project", "-p", help="Filter by project name")
@click.option("--limit", "-l", default=20, help="Limit results")
def list(agent: str = None, project: str = None, limit: int = 20):
    """List sessions."""
    params = {}
    if agent:
        params["agent_type"] = agent
    if project:
        params["project_name"] = project
    params["limit"] = limit
    
    try:
        resp = requests.get(f"{API_BASE}/sessions", params=params)
        resp.raise_for_status()
        sessions = resp.json()
        
        if not sessions:
            click.echo("No sessions found.")
            return
        
        click.echo(f"{'ID':<18} {'Agent':<12} {'Project':<20} {'Tokens':<10} {'Cost':<10} {'Started'}")
        click.echo("-" * 90)
        for s in sessions:
            click.echo(
                f"{s['session_id']:<18} {s['agent_type']:<12} "
                f"{(s['project_name'] or '-')[:18]:<20} {s['total_tokens']:<10} "
                f"${s['estimated_cost']:<9.4f} {s['start_time'][:10]}"
            )
    except requests.exceptions.ConnectionError:
        click.echo("❌ Error: Cannot connect to AgentLens server.", err=True)
        sys.exit(1)


@cli.command()
def stats():
    """Show analytics summary."""
    try:
        resp = requests.get(f"{API_BASE}/analytics/summary")
        resp.raise_for_status()
        data = resp.json()
        
        click.echo("📊 AgentLens Analytics Summary")
        click.echo("=" * 40)
        click.echo(f"Total Sessions:    {data['total_sessions']}")
        click.echo(f"Total Duration:    {data['total_duration_seconds'] // 3600}h {(data['total_duration_seconds'] % 3600) // 60}m")
        click.echo(f"Total Tokens:      {data['total_tokens']:,}")
        click.echo(f"Total Cost:        ${data['total_cost']:.4f}")
        click.echo(f"Total Commands:    {data['total_commands']}")
        click.echo(f"Total Errors:      {data['total_errors']}")
        click.echo(f"Avg Duration:      {data['avg_session_duration']:.0f}s")
        click.echo(f"Avg Tokens/Session: {data['avg_tokens_per_session']:.0f}")
        
        if data['top_agents']:
            click.echo("\n🏆 Top Agents:")
            for agent in data['top_agents'][:5]:
                click.echo(f"   {agent['agent']}: {agent['sessions']} sessions, {agent['tokens']} tokens")
    except requests.exceptions.ConnectionError:
        click.echo("❌ Error: Cannot connect to AgentLens server.", err=True)
        sys.exit(1)


@cli.command()
@click.argument("session_id")
def delete(session_id: str):
    """Delete a session."""
    try:
        resp = requests.delete(f"{API_BASE}/sessions/{session_id}")
        resp.raise_for_status()
        click.echo(f"✅ Session {session_id} deleted.")
    except requests.exceptions.ConnectionError:
        click.echo("❌ Error: Cannot connect to AgentLens server.", err=True)
        sys.exit(1)


@cli.command()
def serve():
    """Start the AgentLens web server."""
    import uvicorn
    click.echo(f"🚀 Starting AgentLens server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)


if __name__ == "__main__":
    cli()
