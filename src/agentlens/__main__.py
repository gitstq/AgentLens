#!/usr/bin/env python3
"""
AgentLens - Lightweight AI Coding Agent Session Intelligence Analysis Engine
轻量级AI编码代理会话智能分析引擎

Zero external dependencies | Pure Python 3.8+ | Cross-Platform

Usage:
    python -m agentlens scan              Scan default agent directories
    python -m agentlens dashboard         Show analysis dashboard
    python -m agentlens export -f md      Export as Markdown
    python -m agentlens sessions           List recent sessions
    python -m agentlens cost              Show cost analysis
    python -m agentlens agents            List detected agents
"""

from .cli import main

if __name__ == "__main__":
    main()
