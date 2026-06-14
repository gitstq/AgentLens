"""
Cost calculation utilities for AI agent sessions.
"""

from typing import Dict


class CostCalculator:
    """Calculate API costs based on token usage."""
    
    # Default pricing per 1K tokens (USD)
    DEFAULT_PRICING = {
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "codex": {"input": 0.01, "output": 0.03},
        "cursor": {"input": 0.01, "output": 0.03},
        "default": {"input": 0.01, "output": 0.03},
    }
    
    @classmethod
    def calculate(
        cls,
        input_tokens: int,
        output_tokens: int,
        price_per_1k_input: float = 0.01,
        price_per_1k_output: float = 0.03,
    ) -> float:
        """Calculate estimated cost."""
        input_cost = (input_tokens / 1000) * price_per_1k_input
        output_cost = (output_tokens / 1000) * price_per_1k_output
        return round(input_cost + output_cost, 6)
    
    @classmethod
    def calculate_by_model(
        cls,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> Dict[str, float]:
        """Calculate cost using model-specific pricing."""
        pricing = cls.DEFAULT_PRICING.get(model, cls.DEFAULT_PRICING["default"])
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total = input_cost + output_cost
        
        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total, 6),
            "currency": "USD",
        }
    
    @classmethod
    def get_pricing_table(cls) -> Dict[str, Dict[str, float]]:
        """Get full pricing table."""
        return cls.DEFAULT_PRICING.copy()
