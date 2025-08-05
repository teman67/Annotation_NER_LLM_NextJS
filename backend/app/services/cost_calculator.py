from typing import Dict, Optional
from app.config import settings


class CostCalculator:
    """Calculate costs for different LLM models based on token usage"""
    
    def __init__(self):
        self.pricing = {
            "gpt-4": {
                "input": settings.openai_gpt4_input_cost,
                "output": settings.openai_gpt4_output_cost
            },
            "gpt-4-turbo": {
                "input": settings.openai_gpt4_input_cost,
                "output": settings.openai_gpt4_output_cost
            },
            "gpt-3.5-turbo": {
                "input": settings.openai_gpt35_input_cost,
                "output": settings.openai_gpt35_output_cost
            },
            "claude-3": {
                "input": settings.claude_input_cost,
                "output": settings.claude_output_cost
            },
            "claude-3-sonnet": {
                "input": settings.claude_input_cost,
                "output": settings.claude_output_cost
            },
            "claude-3-haiku": {
                "input": settings.claude_input_cost * 0.5,  # Haiku is cheaper
                "output": settings.claude_output_cost * 0.5
            }
        }
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate total cost for a model call"""
        
        if model not in self.pricing:
            # Default to GPT-4 pricing for unknown models
            model = "gpt-4"
        
        pricing = self.pricing[model]
        
        # Costs are per 1K tokens
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)
    
    def estimate_cost(
        self,
        model: str,
        text_length: int,
        complexity_factor: float = 1.0
    ) -> Dict[str, float]:
        """Estimate cost based on text length and complexity"""
        
        # Rough estimation: 1 token ≈ 4 characters
        estimated_input_tokens = int(text_length / 4)
        
        # Output tokens depend on task complexity and number of annotations expected
        # Base estimate: 20% of input tokens for simple tasks, more for complex ones
        estimated_output_tokens = int(estimated_input_tokens * 0.2 * complexity_factor)
        
        total_cost = self.calculate_cost(model, estimated_input_tokens, estimated_output_tokens)
        
        return {
            "estimated_input_tokens": estimated_input_tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "estimated_total_cost": total_cost,
            "cost_breakdown": {
                "input_cost": (estimated_input_tokens / 1000) * self.pricing.get(model, self.pricing["gpt-4"])["input"],
                "output_cost": (estimated_output_tokens / 1000) * self.pricing.get(model, self.pricing["gpt-4"])["output"]
            }
        }
    
    def get_model_pricing(self, model: Optional[str] = None) -> Dict:
        """Get pricing information for models"""
        if model:
            return self.pricing.get(model, {})
        return self.pricing
    
    def compare_model_costs(
        self,
        text_length: int,
        complexity_factor: float = 1.0
    ) -> Dict[str, Dict]:
        """Compare costs across different models for the same task"""
        
        comparisons = {}
        
        for model in self.pricing.keys():
            cost_estimate = self.estimate_cost(model, text_length, complexity_factor)
            comparisons[model] = cost_estimate
        
        # Sort by cost
        sorted_models = sorted(
            comparisons.items(),
            key=lambda x: x[1]["estimated_total_cost"]
        )
        
        return {
            "models": dict(sorted_models),
            "cheapest": sorted_models[0][0],
            "most_expensive": sorted_models[-1][0],
            "cost_range": {
                "min": sorted_models[0][1]["estimated_total_cost"],
                "max": sorted_models[-1][1]["estimated_total_cost"]
            }
        }
