from typing import Dict, Optional, List, Any
from datetime import datetime
from app.config import settings


class CostCalculator:
    """Calculate costs for different LLM models based on token usage"""
    
    def __init__(self):
        self.pricing = {
            # OpenAI Models
            "gpt-4o": {
                "input": 0.0050,  # $5.00 per 1M tokens
                "output": 0.0150,  # $15.00 per 1M tokens
            },
            "gpt-4o-mini": {
                "input": 0.00015,  # $0.15 per 1M tokens
                "output": 0.0006,   # $0.60 per 1M tokens
            },
            "gpt-4": {
                "input": 0.030,    # $30.00 per 1M tokens
                "output": 0.060,   # $60.00 per 1M tokens
            },
            "gpt-4-turbo": {
                "input": 0.010,    # $10.00 per 1M tokens
                "output": 0.030,   # $30.00 per 1M tokens
            },
            "gpt-3.5-turbo": {
                "input": 0.0005,   # $0.50 per 1M tokens
                "output": 0.0015,  # $1.50 per 1M tokens
            },
            
            # Anthropic Claude Models
            "claude-3-5-sonnet-20241022": {
                "input": 0.003,    # $3.00 per 1M tokens
                "output": 0.015,   # $15.00 per 1M tokens
            },
            "claude-3-5-haiku-20241022": {
                "input": 0.00025,  # $0.25 per 1M tokens
                "output": 0.00125, # $1.25 per 1M tokens
            },
            "claude-3-opus-20240229": {
                "input": 0.015,    # $15.00 per 1M tokens
                "output": 0.075,   # $75.00 per 1M tokens
            },
            "claude-3-sonnet-20240229": {
                "input": 0.003,    # $3.00 per 1M tokens
                "output": 0.015,   # $15.00 per 1M tokens
            },
            "claude-3-haiku-20240307": {
                "input": 0.00025,  # $0.25 per 1M tokens
                "output": 0.00125, # $1.25 per 1M tokens
            }
        }
        
        # Model aliases for easier matching
        self.model_aliases = {
            "gpt-4o-mini": ["gpt-4o-mini"],
            "gpt-4o": ["gpt-4o"],
            "gpt-4": ["gpt-4", "gpt-4-0613"],
            "gpt-4-turbo": ["gpt-4-turbo", "gpt-4-1106-preview", "gpt-4-0125-preview"],
            "gpt-3.5-turbo": ["gpt-3.5-turbo", "gpt-3.5-turbo-0125"],
            "claude-3-5-sonnet-20241022": ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022"],
            "claude-3-5-haiku-20241022": ["claude-3-5-haiku-20241022"],
        }
    
    def get_model_key(self, model: str) -> str:
        """Get the standardized model key for pricing lookup"""
        model = model.lower()
        
        # Direct match
        if model in self.pricing:
            return model
        
        # Check aliases
        for standard_key, aliases in self.model_aliases.items():
            if model in [alias.lower() for alias in aliases]:
                return standard_key
        
        # Default fallback
        if model.startswith("gpt-4o-mini"):
            return "gpt-4o-mini"
        elif model.startswith("gpt-4o"):
            return "gpt-4o"
        elif model.startswith("gpt-4"):
            return "gpt-4"
        elif model.startswith("gpt-3.5"):
            return "gpt-3.5-turbo"
        elif "claude" in model and "haiku" in model:
            return "claude-3-5-haiku-20241022"
        elif "claude" in model and "sonnet" in model:
            return "claude-3-5-sonnet-20241022"
        else:
            return "gpt-4o-mini"  # Safe default
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> Dict[str, Any]:
        """Calculate total cost for a model call"""
        
        model_key = self.get_model_key(model)
        pricing = self.pricing[model_key]
        
        # Costs are per 1M tokens, convert to per-token costs
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        return {
            "model": model,
            "model_key": model_key,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "cost_per_1k_tokens": {
                "input": pricing["input"] / 1000,
                "output": pricing["output"] / 1000
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def estimate_cost(
        self,
        model: str,
        text_length: int,
        tag_count: int = 5,
        complexity_factor: float = 1.0
    ) -> Dict[str, Any]:
        """Estimate cost based on text length and complexity"""
        
        # Rough estimation: 1 token ≈ 4 characters for English text
        estimated_input_tokens = int(text_length / 4)
        
        # Add tokens for system prompt and tag definitions
        system_prompt_tokens = 200 + (tag_count * 50)  # Base + per tag
        estimated_input_tokens += system_prompt_tokens
        
        # Output tokens depend on task complexity and number of annotations expected
        # Base estimate: entities are usually 1-5% of input tokens
        base_output_ratio = 0.03  # 3% of input tokens
        estimated_output_tokens = int(estimated_input_tokens * base_output_ratio * complexity_factor)
        
        # Minimum output tokens for valid JSON response
        estimated_output_tokens = max(estimated_output_tokens, 50)
        
        cost_breakdown = self.calculate_cost(model, estimated_input_tokens, estimated_output_tokens)
        
        return {
            "text_length": text_length,
            "tag_count": tag_count,
            "complexity_factor": complexity_factor,
            "estimated_input_tokens": estimated_input_tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "estimated_total_tokens": estimated_input_tokens + estimated_output_tokens,
            "estimated_cost": cost_breakdown["total_cost"],
            "cost_breakdown": cost_breakdown,
            "cost_per_character": round(cost_breakdown["total_cost"] / text_length, 8) if text_length > 0 else 0
        }
    
    def estimate_chunked_cost(
        self,
        model: str,
        text_length: int,
        chunk_size: int = 1000,
        overlap: int = 50,
        tag_count: int = 5,
        complexity_factor: float = 1.0
    ) -> Dict[str, Any]:
        """Estimate cost for chunked processing"""
        
        # Calculate number of chunks
        if text_length <= chunk_size:
            num_chunks = 1
            total_chunk_chars = text_length
        else:
            num_chunks = 1
            remaining_text = text_length - chunk_size
            
            while remaining_text > 0:
                num_chunks += 1
                remaining_text -= (chunk_size - overlap)
            
            # Account for overlap in total characters processed
            total_chunk_chars = text_length + (overlap * (num_chunks - 1))
        
        # Estimate cost per chunk
        chunk_cost = self.estimate_cost(model, chunk_size, tag_count, complexity_factor)
        
        # Calculate total cost
        total_input_tokens = chunk_cost["estimated_input_tokens"] * num_chunks
        total_output_tokens = chunk_cost["estimated_output_tokens"] * num_chunks
        total_cost_breakdown = self.calculate_cost(model, total_input_tokens, total_output_tokens)
        
        return {
            "text_length": text_length,
            "chunk_size": chunk_size,
            "overlap": overlap,
            "num_chunks": num_chunks,
            "total_chunk_chars": total_chunk_chars,
            "overlap_overhead": total_chunk_chars - text_length,
            "cost_per_chunk": chunk_cost["estimated_cost"],
            "total_estimated_cost": total_cost_breakdown["total_cost"],
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "efficiency_ratio": text_length / total_chunk_chars if total_chunk_chars > 0 else 1.0
        }
    
    def get_model_pricing(self, model: Optional[str] = None) -> Dict:
        """Get pricing information for models"""
        if model:
            model_key = self.get_model_key(model)
            return {
                "model": model,
                "model_key": model_key,
                "pricing": self.pricing.get(model_key, {}),
                "cost_per_1k_tokens": {
                    "input": self.pricing.get(model_key, {}).get("input", 0) / 1000,
                    "output": self.pricing.get(model_key, {}).get("output", 0) / 1000
                }
            }
        return self.pricing
    
    def compare_model_costs(
        self,
        text_length: int,
        models: Optional[List[str]] = None,
        tag_count: int = 5,
        complexity_factor: float = 1.0
    ) -> Dict[str, Any]:
        """Compare costs across different models for the same task"""
        
        if models is None:
            models = ["gpt-4o-mini", "gpt-4o", "gpt-4", "claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"]
        
        comparisons = {}
        
        for model in models:
            try:
                cost_estimate = self.estimate_cost(model, text_length, tag_count, complexity_factor)
                comparisons[model] = cost_estimate
            except Exception as e:
                comparisons[model] = {"error": str(e)}
        
        # Find cheapest and most expensive
        valid_models = {k: v for k, v in comparisons.items() if "error" not in v}
        
        if valid_models:
            cheapest = min(valid_models.items(), key=lambda x: x[1]["estimated_cost"])
            most_expensive = max(valid_models.items(), key=lambda x: x[1]["estimated_cost"])
            
            return {
                "comparisons": comparisons,
                "cheapest": {
                    "model": cheapest[0],
                    "cost": cheapest[1]["estimated_cost"]
                },
                "most_expensive": {
                    "model": most_expensive[0],
                    "cost": most_expensive[1]["estimated_cost"]
                },
                "cost_range": {
                    "min": cheapest[1]["estimated_cost"],
                    "max": most_expensive[1]["estimated_cost"],
                    "ratio": most_expensive[1]["estimated_cost"] / cheapest[1]["estimated_cost"] if cheapest[1]["estimated_cost"] > 0 else 0
                }
            }
        
        return {"comparisons": comparisons}
    
    def track_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track usage statistics (for future database storage)"""
        
        cost_data = self.calculate_cost(model, input_tokens, output_tokens)
        
        usage_record = {
            "timestamp": datetime.now().isoformat(),
            "project_id": project_id,
            "model": model,
            "model_key": cost_data["model_key"],
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost": cost_data["input_cost"],
            "output_cost": cost_data["output_cost"],
            "total_cost": cost_data["total_cost"]
        }
        
        # In a real implementation, you would save this to a database
        # For now, just return the record
        return usage_record
        
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
