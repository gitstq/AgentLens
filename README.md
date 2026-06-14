<div align="center">

# 🔍 AgentLens

**AI Agent Session Analytics Platform**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)](https://github.com/gitstq/AgentLens/releases)

<p align="center">
  <img src="docs/logo.svg" alt="AgentLens Logo" width="120">
</p>

**Track, Analyze, and Optimize Your AI Agent Sessions**

[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

</div>

---

## 🎉 Project Introduction

AgentLens is a comprehensive analytics platform designed for AI coding agents and conversational AI tools. It helps developers track, analyze, and optimize their AI agent sessions with detailed insights into token usage, costs, and performance metrics.

Whether you're using Claude Code, Cursor, GitHub Copilot, or any other AI agent, AgentLens provides the visibility you need to understand and improve your AI-assisted development workflow.

## ✨ Core Features

- 📊 **Real-time Dashboard** - Beautiful web interface with live session statistics
- 💰 **Cost Tracking** - Automatic token counting and cost estimation
- 🤖 **Multi-Agent Support** - Works with Claude, Cursor, Codex, and more
- 📈 **Analytics & Reports** - Daily trends, agent comparisons, cost analysis
- 🖥️ **CLI Tool** - Command-line interface for quick session management
- 🔒 **Local-First** - Data stored locally, privacy guaranteed
- 🌐 **REST API** - Full-featured API for custom integrations
- 📱 **Responsive UI** - Works on desktop, tablet, and mobile

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend development)

### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/AgentLens.git
cd AgentLens

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies (optional, for development)
cd frontend
npm install
```

### Start the Server

```bash
# Start the API server
python -m src.main

# Or use the CLI
python -m src.cli.main serve
```

The web dashboard will be available at `http://localhost:8000`

### Using the CLI

```bash
# Start a new session
python -m src.cli.main start --agent claude --project my-project

# Log a command
python -m src.cli.main log <session-id> "git commit -m 'update'"

# End session with stats
python -m src.cli.main end <session-id> --input-tokens 1000 --output-tokens 500

# View analytics
python -m src.cli.main stats
```

## 📖 Detailed Usage Guide

### Session Tracking

1. **Start a Session**: Begin tracking when you start working with your AI agent
2. **Log Commands**: Record each interaction for detailed analysis
3. **End Session**: Finalize with token counts for cost calculation

### Web Dashboard

- **Dashboard**: Overview of all sessions, costs, and trends
- **Sessions**: Detailed list with filtering and search
- **Analytics**: Charts and reports for deeper insights
- **Settings**: Configure pricing and preferences

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/sessions` | GET | List all sessions |
| `/api/v1/sessions` | POST | Create new session |
| `/api/v1/sessions/{id}` | GET | Get session details |
| `/api/v1/sessions/{id}` | PATCH | Update session |
| `/api/v1/commands` | POST | Log a command |
| `/api/v1/analytics/summary` | GET | Get analytics summary |

## 💡 Design Philosophy & Roadmap

### Design Principles

- **Privacy First**: All data stays on your machine
- **Developer Friendly**: Simple CLI, powerful API
- **Extensible**: Easy to add new agent types and metrics
- **Lightweight**: Minimal resource usage

### Roadmap

- [ ] Export reports to PDF/CSV
- [ ] Team collaboration features
- [ ] Integration with popular IDEs
- [ ] Advanced cost optimization suggestions
- [ ] Multi-language support expansion

## 📦 Packaging & Deployment

### Docker Deployment

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "src.main"]
```

### Build Frontend

```bash
cd frontend
npm run build
```

### Run Tests

```bash
pytest tests/ -v
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ for the AI Developer Community**

[Report Bug](https://github.com/gitstq/AgentLens/issues) · [Request Feature](https://github.com/gitstq/AgentLens/issues)

</div>
