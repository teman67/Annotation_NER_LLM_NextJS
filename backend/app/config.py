from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Scientific Text Annotator"
    debug: bool = False
    
    # Database
    supabase_url: str = "https://placeholder.supabase.co"
    supabase_key: str = "placeholder_key"
    supabase_service_key: str = "placeholder_service_key"
    
    # Security
    secret_key: str = "development-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # LLM APIs
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # File storage
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".txt", ".pdf", ".docx", ".md", ".rtf"]
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Cost estimation (per 1K tokens)
    openai_gpt4_input_cost: float = 0.01
    openai_gpt4_output_cost: float = 0.03
    openai_gpt35_input_cost: float = 0.0015
    openai_gpt35_output_cost: float = 0.002
    claude_haiku_input_cost: float = 0.00025
    claude_haiku_output_cost: float = 0.00125
    claude_sonnet_input_cost: float = 0.003
    claude_sonnet_output_cost: float = 0.015
    claude_opus_input_cost: float = 0.015
    claude_opus_output_cost: float = 0.075
    
    # Default limits
    default_cost_limit: float = 100.0  # $100 USD
    max_annotations_per_request: int = 1000
    max_text_length: int = 500000  # 500K characters
    
    # Email Configuration
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    smtp_from_name: str = "Scientific Text Annotator"
    smtp_use_tls: bool = True
    
    class Config:
        env_file = ".env"


# LLM Model configurations
LLM_MODELS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "models": [
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "max_tokens": 16385},
            {"id": "gpt-4", "name": "GPT-4", "max_tokens": 8192},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "max_tokens": 128000},
            {"id": "gpt-4o", "name": "GPT-4o", "max_tokens": 128000},
        ]
    },
    "anthropic": {
        "models": [
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "max_tokens": 200000},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "max_tokens": 200000},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "max_tokens": 200000},
        ]
    }
}

# Default annotation prompts
ANNOTATION_PROMPTS = {
    "ner": """You are an expert in Named Entity Recognition (NER). Extract and classify named entities from the given text using the provided tags.

Text: {text}

Available tags: {tags}

Instructions:
1. Identify all entities that match the provided tags
2. Be precise with start and end character positions
3. Assign confidence scores based on clarity and context
4. Only include entities you are confident about

Return the entities in the following JSON format:
[
    {{
        "text": "entity text",
        "start": start_position,
        "end": end_position,
        "tag": "tag_name",
        "confidence": 0.95
    }}
]""",
    
    "classification": """You are an expert text classifier. Classify segments of the given text into the appropriate categories using the provided tags.

Text: {text}

Available categories: {tags}

Instructions:
1. Identify text segments that belong to each category
2. Provide precise character positions for each classification
3. Assign confidence scores based on certainty
4. You may classify overlapping segments if appropriate

Return the classifications in JSON format:
[
    {{
        "text": "classified text segment",
        "start": start_position,
        "end": end_position,
        "tag": "category_name",
        "confidence": 0.95
    }}
]""",
    
    "sentiment": """You are an expert in sentiment analysis. Identify and classify sentiment-bearing expressions in the given text.

Text: {text}

Available sentiment tags: {tags}

Instructions:
1. Identify phrases or sentences that express sentiment
2. Classify sentiment as positive, negative, or neutral
3. Provide confidence scores based on sentiment strength
4. Include contextual information where helpful

Return sentiment annotations in JSON format:
[
    {{
        "text": "sentiment-bearing text",
        "start": start_position,
        "end": end_position,
        "tag": "sentiment_tag",
        "confidence": 0.95
    }}
]""",
    
    "custom": """You are an expert annotator. Analyze the given text and extract information according to the provided instructions and tags.

Text: {text}

Available tags: {tags}

Custom instructions: {instructions}

Return annotations in JSON format:
[
    {{
        "text": "annotated text",
        "start": start_position,
        "end": end_position,
        "tag": "tag_name",
        "confidence": 0.95
    }}
]"""
}

settings = Settings()
