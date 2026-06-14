<p align="center">
  <img src="../assets/logo.jpg" alt="AgentLens Logo" width="120" height="120" />
</p>

<h1 align="center">AgentLens</h1>

<p align="center">
  <strong>Lightweight AI Coding Agent Session Intelligence Analysis Engine</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-success.svg" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/Platform-Cross--Platform-informational.svg" alt="Cross Platform" />
  <img src="https://img.shields.io/badge/Tests-28%20Passed-brightgreen.svg" alt="Tests" />
  <img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="Version" />
</p>

---

## Introduction

AgentLens is a lightweight, zero-dependency CLI tool that intelligently analyzes your AI coding agent sessions. It automatically detects session data from Claude Code, Cursor, Trae, Windsurf, Copilot, Aider, and more — providing deep insights into your usage patterns, token consumption, costs, and optimization opportunities.

**Why AgentLens?** As AI coding agents become essential developer tools, understanding how you use them — and how much they cost — is critical. AgentLens gives you a clear, actionable view of your AI coding workflow.

## Features

- **Multi-Agent Support** — Auto-detect and parse sessions from 10+ AI coding agents
- **Cost Intelligence** — Track token usage and costs across models with smart projections
- **Usage Analytics** — Daily/weekly patterns, peak hours, session length distribution
- **Terminal Dashboard** — Beautiful colored TUI dashboard with progress bars
- **Multi-Format Export** — JSON, CSV, Markdown, SARIF for CI/CD integration
- **Optimization Tips** — Smart suggestions to reduce costs and improve efficiency
- **Zero Dependencies** — Pure Python 3.8+, single-file install, cross-platform
- **Privacy First** — 100% local analysis, no data leaves your machine

## Quick Start

### Install

```bash
pip install agentlens
```

Or from source:

```bash
git clone https://github.com/gitstq/AgentLens.git
cd AgentLens
pip install -e .
```

### Commands

```bash
# Detect installed AI coding agents
agentlens agents

# Show analysis dashboard
agentlens dashboard

# Scan and analyze all sessions
agentlens scan

# Cost analysis with projections
agentlens cost

# List recent sessions
agentlens sessions --limit 10

# Export reports
agentlens export --format markdown --output report.md
agentlens export --format csv --output analysis.csv
agentlens export --format sarif --output results.sarif

# Scan specific agent or directory
agentlens scan --agent claude-code
agentlens scan --path /path/to/sessions
```

## Supported Agents

| Agent | Support Level | Parser |
|-------|---------------|--------|
| Claude Code | Full | JSON/JSONL |
| Cursor | Full | JSON |
| Trae | Full | JSON/JSONL |
| Windsurf | Full | JSON |
| GitHub Copilot | Basic | JSON |
| Aider | Basic | JSONL |
| Continue | Basic | JSON |
| Tongyi Lingma | Basic | JSON |
| Codeium | Basic | JSON |
| Generic | Fallback | JSON/JSONL/Text |

## Architecture

```
AgentLens/
├── src/agentlens/
│   ├── models/       # Data models (Session, Message, CostRecord)
│   ├── parsers/      # Agent-specific session parsers
│   ├── analyzers/    # Session, cost, and usage analyzers
│   ├── exporters/    # Multi-format export (JSON/CSV/MD/SARIF)
│   ├── ui/           # Terminal UI (colors, tables, dashboard)
│   ├── utils/        # Utilities (cost estimation, path detection)
│   └── cli.py        # CLI entry point
├── tests/            # 28 unit tests, all passing
└── pyproject.toml    # Build configuration
```

## Roadmap

- [ ] Web UI dashboard
- [ ] Historical trend charts
- [ ] Session comparison and diff
- [ ] Plugin system for custom analyzers
- [ ] Real-time session monitoring
- [ ] Team/shared analytics
- [ ] VS Code extension

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License — see [LICENSE](../LICENSE) for details.

---

<p align="center">
  Built with Python by <a href="https://github.com/gitstq">AgentLens Team</a>
</p>
