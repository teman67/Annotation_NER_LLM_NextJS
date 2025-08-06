# 🔬 Scientific Text Annotation System

A comprehensive web application for scientific text annotation using AI models, with advanced features for validation, export, and cost estimation.

## 🌟 Features Overview

### Core Annotation Features

- **Multi-Model Support**: OpenAI (GPT-4O, GPT-4O Mini, GPT-4) and Claude (3.5 Haiku, 3.5 Sonnet)
- **Intelligent Text Chunking**: Automatic text splitting with configurable overlap
- **Interactive Highlighting**: Visual annotation display with click-to-select functionality
- **Manual Annotation**: Add custom annotations by selecting text
- **Real-time Processing**: Live token counting and cost estimation

### Advanced Processing

- **Text Chunking with Overlap**: Handles large documents by splitting into processable chunks
- **Token Optimization**: Smart chunk sizing based on model limits
- **Batch Processing**: Efficient handling of multiple text chunks
- **Statistics Tracking**: Comprehensive processing metrics

### Validation & Quality Control

- **Position Validation**: Ensures annotation positions match text content
- **Automatic Fixing**: Corrects common annotation errors automatically
- **Overlap Detection**: Identifies and resolves overlapping annotations
- **Quality Metrics**: Detailed validation statistics and error reporting

### Export Capabilities

- **Multiple Formats**: JSON, CSV, CoNLL, and comprehensive JSON exports
- **Metadata Inclusion**: Processing statistics, model information, and timestamps
- **Evaluation Results**: Export includes confidence scores and processing details
- **Standard Formats**: Compatible with common NLP tools and frameworks

### Cost Management

- **Real-time Estimation**: Live cost calculation based on current settings
- **Token Breakdown**: Detailed input/output token analysis
- **Model Comparison**: Cost comparison across different models
- **Budget Warnings**: Alerts for high-cost operations

## 🏗️ Architecture

### Backend Services

- **LLM Service** (`app/services/llm_service.py`): Core annotation processing with chunking and validation
- **Validation Service** (`app/services/validation_service.py`): Position validation and automatic fixing
- **Export Service** (`app/services/export_service.py`): Multi-format export functionality
- **Cost Calculator** (`app/services/cost_calculator.py`): Token counting and cost estimation

### Frontend Components

- **AnnotationPage** (`src/pages/AnnotationPage.tsx`): Main interface with tabbed layout
- **ValidationComponent** (`src/components/ValidationComponent.tsx`): Quality control interface
- **ExportComponent** (`src/components/ExportComponent.tsx`): Export options and controls
- **CostCalculator** (`src/components/CostCalculator.tsx`): Real-time cost estimation

### API Endpoints

- `POST /annotations/annotate` - Main annotation processing
- `POST /annotations/validate` - Annotation validation
- `POST /annotations/fix` - Automatic error fixing
- `POST /annotations/export` - Export annotations
- `POST /annotations/estimate-cost` - Cost estimation
- `POST /annotations/evaluate` - Annotation evaluation

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+ and pip
- OpenAI API key
- Claude API key (optional)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-key"
export CLAUDE_API_KEY="your-claude-key"  # optional

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd react
npm install
npm run dev
```

### Production Build

```bash
# Frontend
npm run build

# Backend (with your deployment method)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📖 Usage Guide

### 1. File Upload

- **Tags CSV**: Upload a CSV file with columns: `tag_name`, `definition`, `examples`
- **Text File**: Upload a `.txt` file with the text to annotate

### 2. Settings Configuration

- **Model Selection**: Choose from available AI models
- **Temperature**: Control response creativity (0.0 = consistent, 1.0 = creative)
- **Chunk Size**: Set text chunk size for processing (200-4000 chars)
- **Max Tokens**: Configure output token limit
- **Overlap**: Set chunk overlap to maintain context

### 3. Annotation Process

- Click "Run Annotation" to start AI processing
- View real-time progress and statistics
- Review highlighted annotations in the text preview
- Add manual annotations by selecting text

### 4. Quality Control

- Use the **Validation** tab to check annotation quality
- Review error details and suggestions
- Apply automatic fixes for common issues
- Monitor validation statistics

### 5. Export Options

- **JSON**: Lightweight format for integration
- **CSV**: Tabular format for spreadsheet analysis
- **CoNLL**: Standard NLP format for training/evaluation
- **Comprehensive**: Complete export with metadata and statistics

## 🔧 Configuration

### Model Settings

```typescript
// Available models with their characteristics
const models = {
  "gpt-4o-mini": { fast: true, cost: "low", quality: "good" },
  "gpt-4o": { fast: false, cost: "medium", quality: "excellent" },
  "gpt-4": { fast: false, cost: "high", quality: "excellent" },
  "claude-3-5-haiku": { fast: true, cost: "low", quality: "good" },
  "claude-3-5-sonnet": { fast: false, cost: "medium", quality: "excellent" },
};
```

### Chunking Strategy

- **Small texts** (< 1000 chars): Process without chunking
- **Medium texts** (1000-4000 chars): Single chunk with full context
- **Large texts** (> 4000 chars): Multiple chunks with overlap
- **Overlap recommendations**: 50-100 chars for most use cases

### Cost Optimization

- Use **gpt-4o-mini** or **claude-3-5-haiku** for cost-effective processing
- Reduce chunk size for lower token consumption
- Set appropriate max_tokens limits
- Monitor real-time cost estimates

## 🎯 Advanced Features

### Interactive Text Selection

- Click and drag to select text for manual annotation
- Choose from available tag categories
- Visual distinction between AI and manual annotations
- Easy removal and editing of annotations

### Validation Strategies

- **Position Validation**: Ensures start/end positions match text content
- **Boundary Fixing**: Adjusts positions to word boundaries
- **Overlap Resolution**: Handles overlapping annotations
- **Content Verification**: Validates extracted text matches positions

### Export Formats Detail

#### JSON Format

```json
{
  "entities": [
    {
      "start_char": 0,
      "end_char": 10,
      "text": "example",
      "label": "TERM",
      "confidence": 0.95,
      "source": "llm"
    }
  ]
}
```

#### CSV Format

```csv
text,label,start_char,end_char,confidence,source
"example","TERM",0,10,0.95,"llm"
```

#### CoNLL Format

```
Example B-TERM
text I-TERM
follows O
```

## 🔍 Troubleshooting

### Common Issues

1. **High API Costs**: Use smaller models or reduce text length
2. **Position Errors**: Use validation and auto-fix features
3. **Missing Annotations**: Adjust temperature and chunk settings
4. **Export Failures**: Check annotation validity before export

### Performance Tips

- Use appropriate chunk sizes for your text length
- Enable cost estimation to avoid unexpected charges
- Validate annotations before export
- Use manual annotation for high-precision requirements

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

### Code Style

- Backend: Follow PEP 8 Python standards
- Frontend: Use TypeScript with strict mode
- Components: Functional components with hooks
- Testing: Unit tests for all services

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- React community for frontend tools
- FastAPI community for backend framework

---

For detailed API documentation, see the FastAPI auto-generated docs at `/docs` when running the backend server.
