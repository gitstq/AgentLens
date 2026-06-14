"""
Cost calculator tests.
"""

import pytest

from src.services.cost_calculator import CostCalculator


def test_calculate_basic():
    """Test basic cost calculation."""
    cost = CostCalculator.calculate(1000, 500)
    assert cost == 0.025


def test_calculate_custom_pricing():
    """Test cost calculation with custom pricing."""
    cost = CostCalculator.calculate(2000, 1000, 0.005, 0.015)
    assert cost == 0.025


def test_calculate_by_model():
    """Test model-specific cost calculation."""
    result = CostCalculator.calculate_by_model("gpt-4o", 1000, 500)
    assert result["currency"] == "USD"
    assert result["total_cost"] > 0
    assert "input_cost" in result
    assert "output_cost" in result


def test_pricing_table():
    """Test pricing table retrieval."""
    table = CostCalculator.get_pricing_table()
    assert "gpt-4o" in table
    assert "claude-3-opus" in table
    assert "default" in table
