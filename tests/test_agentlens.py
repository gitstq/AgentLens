"""Tests for AgentLens core modules."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentlens.models import (
    Session, Message, ToolUsage, FileChange, CostRecord,
    AgentType, SessionStatus, AnalysisResult
)
from agentlens.utils import (
    count_tokens_approx, estimate_cost, format_cost,
    format_duration, format_number, format_timestamp,
    generate_session_id, get_date_key, safe_load_json, safe_load_jsonl
)
from agentlens.parsers import (
    ClaudeCodeParser, CursorParser, TraeParser, GenericParser,
    get_parser, detect_agent_type
)
from agentlens.analyzers import SessionAnalyzer, CostAnalyzer, UsageAnalyzer
from agentlens.exporters import (
    JSONExporter, CSVExporter, MarkdownExporter, SARIFExporter,
    get_exporter, export_result
)


class TestUtils:
    """Test utility functions."""

    def test_count_tokens_english(self):
        result = count_tokens_approx("Hello, this is a test message.")
        assert result > 0
        assert result < 20

    def test_count_tokens_chinese(self):
        result = count_tokens_approx("这是一个中文测试消息")
        assert result > 0

    def test_count_tokens_empty(self):
        assert count_tokens_approx("") == 0

    def test_estimate_cost(self):
        cost = estimate_cost("claude-3.5-sonnet", 1000, 500)
        assert cost > 0
        assert cost < 0.1

    def test_format_cost(self):
        assert "K" in format_cost(0.001)
        assert "$" in format_cost(1.0)
        assert "$" in format_cost(100.0)

    def test_format_duration(self):
        assert "s" in format_duration(30)
        assert "m" in format_duration(120)
        assert "h" in format_duration(7200)

    def test_format_number(self):
        assert format_number(500) == "500"
        assert "K" in format_number(5000)
        assert "M" in format_number(5000000)

    def test_generate_session_id(self):
        id1 = generate_session_id("test content")
        id2 = generate_session_id("test content")
        id3 = generate_session_id("different content")
        assert len(id1) == 12
        assert id1 == id2
        assert id1 != id3

    def test_safe_load_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "value"}, f)
            f.flush()
            result = safe_load_json(Path(f.name))
            assert result == {"key": "value"}
            os.unlink(f.name)

    def test_safe_load_json_invalid(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            f.flush()
            result = safe_load_json(Path(f.name))
            assert result is None
            os.unlink(f.name)

    def test_safe_load_jsonl(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write('{"a": 1}\n{"b": 2}\ninvalid\n')
            f.flush()
            result = safe_load_jsonl(Path(f.name))
            assert len(result) == 2
            os.unlink(f.name)


class TestModels:
    """Test data models."""

    def test_session_creation(self):
        session = Session(
            session_id="test123",
            agent_type=AgentType.CLAUDE_CODE,
            messages=[
                Message(role="user", content="Hello", token_count=5),
                Message(role="assistant", content="Hi there!", token_count=8),
            ]
        )
        assert session.message_count == 2
        assert session.session_id == "test123"

    def test_session_to_dict(self):
        session = Session(
            session_id="abc",
            agent_type=AgentType.CLAUDE_CODE,
            start_time=1000.0,
            end_time=2000.0,
        )
        d = session.to_dict()
        assert d["session_id"] == "abc"
        assert d["agent_type"] == "claude-code"
        assert d["duration_seconds"] == 1000.0

    def test_session_to_json(self):
        session = Session(session_id="test")
        json_str = session.to_json()
        parsed = json.loads(json_str)
        assert parsed["session_id"] == "test"

    def test_analysis_result(self):
        result = AnalysisResult(
            total_sessions=5,
            total_tokens=10000,
            total_cost_usd=0.5,
        )
        d = result.to_dict()
        assert d["total_sessions"] == 5
        assert d["total_tokens"] == 10000


class TestParsers:
    """Test session parsers."""

    def _create_jsonl_file(self, records):
        """Helper to create a temp JSONL file."""
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
        for r in records:
            f.write(json.dumps(r) + "\n")
        f.close()
        return Path(f.name)

    def _create_json_file(self, data):
        """Helper to create a temp JSON file."""
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(data, f)
        f.close()
        return Path(f.name)

    def test_claude_code_parser_jsonl(self):
        records = [
            {"role": "user", "content": "Hello", "timestamp": 1000, "model": "claude-3.5-sonnet"},
            {"role": "assistant", "content": "Hi!", "timestamp": 1001, "model": "claude-3.5-sonnet",
             "usage": {"input_tokens": 100, "output_tokens": 50}},
        ]
        path = self._create_jsonl_file(records)
        try:
            parser = ClaudeCodeParser()
            session = parser.parse_file(path)
            assert session is not None
            assert session.message_count == 2
            assert session.agent_type == AgentType.CLAUDE_CODE
        finally:
            os.unlink(path)

    def test_cursor_parser(self):
        data = {
            "messages": [
                {"role": "user", "content": "Fix bug", "model": "gpt-4o"},
                {"role": "assistant", "content": "Fixed!", "model": "gpt-4o"},
            ]
        }
        path = self._create_json_file(data)
        try:
            parser = CursorParser()
            session = parser.parse_file(path)
            assert session is not None
            assert session.message_count == 2
        finally:
            os.unlink(path)

    def test_generic_parser_json(self):
        data = {
            "messages": [
                {"role": "user", "content": "Test message"},
                {"role": "assistant", "content": "Test response"},
            ]
        }
        path = self._create_json_file(data)
        try:
            parser = GenericParser()
            session = parser.parse_file(path)
            assert session is not None
            assert session.message_count == 2
        finally:
            os.unlink(path)

    def test_detect_agent_type(self):
        assert detect_agent_type(Path("/home/.claude/sessions/test.json")) == "claude-code"
        assert detect_agent_type(Path("/home/.cursor/sessions/test.json")) == "cursor"
        assert detect_agent_type(Path("/home/.trae/data/test.json")) == "trae"
        assert detect_agent_type(Path("/tmp/test.json")) == "generic"

    def test_get_parser(self):
        assert isinstance(get_parser("claude-code"), ClaudeCodeParser)
        assert isinstance(get_parser("cursor"), CursorParser)
        assert isinstance(get_parser("unknown"), GenericParser)


class TestAnalyzers:
    """Test analyzers."""

    def _create_test_sessions(self):
        return [
            Session(
                session_id="s1",
                agent_type=AgentType.CLAUDE_CODE,
                start_time=1000.0,
                end_time=2000.0,
                messages=[Message(role="user", content="Hello", token_count=10)],
                total_tokens=100,
                total_cost_usd=0.01,
                cost_records=[CostRecord(model="claude-3.5-sonnet", total_tokens=100, estimated_cost_usd=0.01)],
            ),
            Session(
                session_id="s2",
                agent_type=AgentType.CURSOR,
                start_time=3000.0,
                end_time=5000.0,
                messages=[Message(role="user", content="World", token_count=10)],
                total_tokens=200,
                total_cost_usd=0.02,
                cost_records=[CostRecord(model="gpt-4o", total_tokens=200, estimated_cost_usd=0.02)],
            ),
        ]

    def test_session_analyzer(self):
        sessions = self._create_test_sessions()
        analyzer = SessionAnalyzer()
        result = analyzer.analyze(sessions)
        assert result.total_sessions == 2
        assert result.total_tokens == 300
        assert result.total_cost_usd == 0.03
        assert "claude-code" in result.agent_distribution
        assert "cursor" in result.agent_distribution
        assert len(result.optimization_tips) > 0

    def test_session_analyzer_empty(self):
        analyzer = SessionAnalyzer()
        result = analyzer.analyze([])
        assert result.total_sessions == 0
        assert len(result.optimization_tips) > 0

    def test_cost_analyzer(self):
        sessions = self._create_test_sessions()
        ca = CostAnalyzer()
        trend = ca.analyze_cost_trend(sessions)
        assert len(trend) > 0

        efficiency = ca.analyze_model_efficiency(sessions)
        assert len(efficiency) > 0

        projection = ca.project_monthly_cost(sessions)
        assert "projected_monthly" in projection


class TestExporters:
    """Test exporters."""

    def _create_test_result(self):
        return AnalysisResult(
            total_sessions=2,
            total_tokens=300,
            total_cost_usd=0.03,
            total_duration_seconds=3000.0,
            total_messages=2,
            agent_distribution={"claude-code": 1, "cursor": 1},
            model_distribution={"claude-3.5-sonnet": 1, "gpt-4o": 1},
            cost_by_model={"claude-3.5-sonnet": 0.01, "gpt-4o": 0.02},
            optimization_tips=["Tip 1", "Tip 2"],
        )

    def test_json_exporter(self):
        result = self._create_test_result()
        exporter = JSONExporter()
        content = exporter.export(result)
        parsed = json.loads(content)
        assert parsed["total_sessions"] == 2

    def test_csv_exporter(self):
        result = self._create_test_result()
        exporter = CSVExporter()
        content = exporter.export(result)
        assert "Total Sessions" in content
        assert "claude-code" in content

    def test_markdown_exporter(self):
        result = self._create_test_result()
        exporter = MarkdownExporter()
        content = exporter.export(result)
        assert "# AgentLens" in content
        assert "## Overview" in content

    def test_sarif_exporter(self):
        result = self._create_test_result()
        exporter = SARIFExporter()
        content = exporter.export(result)
        parsed = json.loads(content)
        assert parsed["version"] == "2.1.0"
        assert "AgentLens" in parsed["runs"][0]["tool"]["driver"]["name"]

    def test_get_exporter(self):
        assert isinstance(get_exporter("json"), JSONExporter)
        assert isinstance(get_exporter("markdown"), MarkdownExporter)
        assert isinstance(get_exporter("md"), MarkdownExporter)
        assert isinstance(get_exporter("csv"), CSVExporter)
        assert isinstance(get_exporter("sarif"), SARIFExporter)


def run_tests():
    """Run all tests."""
    test_classes = [TestUtils, TestModels, TestParsers, TestAnalyzers, TestExporters]
    total = 0
    passed = 0
    failed = 0

    for cls in test_classes:
        instance = cls()
        methods = [m for m in dir(instance) if m.startswith("test_")]
        for method_name in methods:
            total += 1
            try:
                getattr(instance, method_name)()
                passed += 1
                print(f"  PASS: {cls.__name__}.{method_name}")
            except Exception as e:
                failed += 1
                print(f"  FAIL: {cls.__name__}.{method_name} - {e}")

    print()
    print(f"Results: {passed}/{total} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
