# Scientific Text Annotator Backend

FastAPI backend for the Scientific Text Annotator application with LLM integration, Supabase database, and authentication.

## Features

- **LLM Integration**: OpenAI GPT and Anthropic Claude support
- **Authentication**: JWT-based auth with Supabase
- **Database**: PostgreSQL via Supabase
- **File Processing**: Text file upload and processing
- **Tag Management**: Custom tag definitions and validation
- **Cost Estimation**: Token usage and cost calculation
- **Real-time Updates**: WebSocket support for live annotations

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create `.env` file with your configuration:

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
SECRET_KEY=your_jwt_secret_key
```

3. Run the development server:

```bash
uvicorn main:app --reload
```

## API Documentation

Once running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   ├── services/            # Business logic
│   ├── utils/               # Utility functions
│   └── auth/                # Authentication
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── requirements.txt
└── README.md
```
