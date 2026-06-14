# Contributing to AgentLens

Thank you for your interest in contributing to AgentLens!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/gitstq/AgentLens.git
cd AgentLens

# Install in development mode
pip install -e .

# Run tests
python tests/test_agentlens.py
```

## Project Structure

- `src/agentlens/models/` — Data models
- `src/agentlens/parsers/` — Agent session parsers
- `src/agentlens/analyzers/` — Analysis engines
- `src/agentlens/exporters/` — Export formats
- `src/agentlens/ui/` — Terminal UI
- `src/agentlens/utils/` — Utilities
- `tests/` — Unit tests

## Adding a New Agent Parser

1. Create a new parser class in `src/agentlens/parsers/` extending `BaseParser`
2. Implement the `parse_file()` method
3. Register the parser in `PARSER_REGISTRY`
4. Add detection logic in `detect_agent_type()`
5. Add tests in `tests/test_agentlens.py`

## Commit Convention

We follow the Angular commit convention:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

## Code Style

- Python 3.8+ compatible
- Type hints encouraged
- Docstrings for all public functions
- Zero external dependencies (stdlib only)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
