# Scientific Text Annotator

A full-stack web application for AI-powered text annotation using Large Language Models (LLMs). This application enables researchers and data scientists to efficiently annotate scientific texts with custom tags using OpenAI GPT models and Anthropic Claude.

## 🚀 Features

### Core Functionality

- **AI-Powered Annotation**: Automatic text annotation using OpenAI GPT and Anthropic Claude models
- **Custom Tag Management**: Create and manage custom annotation tags for your specific use cases
- **Project Organization**: Organize your annotation work into projects with team collaboration
- **File Upload & Processing**: Support for various text formats (.txt, .pdf, .docx, .md)
- **Real-time Annotation**: Interactive annotation interface with real-time preview
- **Cost Tracking**: Monitor LLM usage costs with detailed analytics

### Advanced Features

- **Multi-Model Support**: Choose from different LLM models based on your needs
- **Annotation Confidence**: AI-generated confidence scores for each annotation
- **Human Review**: Approve, reject, or modify AI-generated annotations
- **Export Options**: Export annotations in JSON, CSV, or CoNLL formats
- **Team Collaboration**: Share projects with team members with role-based access
- **Usage Analytics**: Detailed statistics and visualizations of annotation work

## 🏗️ Architecture

### Frontend (React + TypeScript + Vite)

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and building
- **Routing**: React Router for navigation
- **Styling**: Tailwind CSS for modern, responsive UI
- **State Management**: React Context API with React Query for server state
- **Authentication**: Custom backend authentication with JWT tokens
- **Icons**: Heroicons for consistent iconography
- **Notifications**: React Hot Toast for user feedback

### Backend (FastAPI + Python)

- **Framework**: FastAPI for high-performance REST API
- **Database**: Backend database for data persistence
- **Authentication**: JWT-based authentication with custom backend
- **LLM Integration**: OpenAI GPT and Anthropic Claude APIs
- **File Processing**: Multi-format text extraction and processing
- **Cost Calculation**: Real-time usage tracking and cost estimation

## 🎯 Recent Optimizations

### Code Quality Improvements

1. **Consolidated App Components**: Removed duplicate App-\*.tsx files and consolidated to single optimized App.tsx
2. **Enhanced Error Handling**: Added comprehensive error utilities with proper TypeScript types
3. **Optimized AuthContext**: Improved error handling, consistent API calls, and proper type safety
4. **Removed Unused Code**: Eliminated unused SupabaseContext and duplicate files
5. **Custom Hooks**: Separated useAuth into its own hook file for better organization
6. **Loading Components**: Created reusable LoadingSpinner component with customizable sizes
7. **API Constants**: Centralized API endpoints and configuration for better maintainability
8. **TypeScript Improvements**: Fixed all TypeScript compilation errors and improved type safety

### Performance Enhancements

1. **Optimized Bundle Size**: Removed unused dependencies and code
2. **Proper Code Splitting**: Organized components and utilities for better tree-shaking
3. **API Configuration**: Centralized API configuration with environment variables
4. **Error Boundaries**: Improved error handling throughout the application

### Developer Experience

1. **Better File Organization**: Proper separation of concerns across directories
2. **Consistent Coding Patterns**: Standardized error handling and API calls
3. **Type Safety**: Comprehensive TypeScript types throughout the application
4. **Documentation**: Updated README with current architecture and setup instructions

## 🛠️ Setup & Installation

### Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- **Supabase Account** for database and authentication
- **OpenAI API Key** (optional, for GPT models)
- **Anthropic API Key** (optional, for Claude models)

### Frontend Setup

1. **Install Dependencies**

   ```bash
   npm install
   ```

2. **Environment Configuration**

   ```bash
   cp .env.example .env
   ```

   Configure your environment variables:

   ```env
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

### Backend Setup

1. **Navigate to Backend Directory**

   ```bash
   cd backend
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**

   ```bash
   cp .env.example .env
   ```

   Configure your environment variables:

   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   SECRET_KEY=your_jwt_secret_key
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

5. **Start Backend Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Database Setup

1. **Create Supabase Project**

   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Get your project URL and API keys

2. **Run Database Schema**
   - Open the SQL editor in your Supabase dashboard
   - Run the SQL from `backend/supabase_schema.sql`

## 📋 Available Scripts

### Frontend Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Backend Scripts

- `uvicorn app.main:app --reload` - Start development server
- `python -m pytest` - Run tests (when implemented)

### VS Code Tasks

Use Ctrl+Shift+P → "Tasks: Run Task" to access:

- **Start Frontend Dev Server** - Start React development server
- **Start Backend Dev Server** - Start FastAPI development server
- **Install Frontend Dependencies** - Install npm packages
- **Install Backend Dependencies** - Install Python packages
- **Build Frontend** - Build React app for production

## 🎯 Usage Guide

### Getting Started

1. **Create Account**

   - Visit the application and register with your email
   - Verify your email if required

2. **Create Project**

   - Navigate to Projects and create a new project
   - Configure LLM settings (model, temperature, cost limits)

3. **Define Tags**

   - Create custom annotation tags for your use case
   - Examples: "PERSON", "ORGANIZATION", "LOCATION", "SENTIMENT"

4. **Upload Files**

   - Upload text files for annotation
   - Supported formats: .txt, .pdf, .docx, .md

5. **Generate Annotations**

   - Use AI to automatically annotate your texts
   - Review and approve/reject annotations
   - Make manual corrections as needed

6. **Export Results**
   - Export your annotations in various formats
   - Use for training ML models or further analysis

### Best Practices

- **Start Small**: Begin with a small set of files to test your tags and prompts
- **Iterative Approach**: Refine your tags and prompts based on initial results
- **Human Review**: Always review AI-generated annotations for accuracy
- **Cost Monitoring**: Keep track of LLM usage costs, especially with larger models
- **Team Coordination**: Use project sharing for collaborative annotation work

## 🔧 Configuration

### LLM Models

#### OpenAI Models

- **GPT-3.5 Turbo**: Fast and cost-effective for most tasks
- **GPT-4**: Higher accuracy for complex annotation tasks
- **GPT-4 Turbo**: Balance of speed and accuracy with larger context

#### Anthropic Models

- **Claude 3 Haiku**: Fastest and most cost-effective
- **Claude 3 Sonnet**: Balanced performance and cost
- **Claude 3 Opus**: Highest accuracy for complex tasks

### Cost Optimization

- Choose appropriate models for your accuracy needs
- Set cost limits per project to prevent overspending
- Use smaller context windows when possible
- Batch process similar texts together

## 📁 Project Structure

```
/
├── src/                      # Frontend source code
│   ├── components/           # Reusable React components
│   ├── contexts/            # React context providers
│   ├── pages/               # Page components
│   ├── services/            # API service functions
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   └── styles.css           # Global styles
├── backend/                 # Backend source code
│   ├── app/
│   │   ├── api/            # FastAPI route handlers
│   │   ├── services/       # Business logic services
│   │   ├── config.py       # Configuration settings
│   │   ├── database.py     # Database operations
│   │   └── main.py         # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── supabase_schema.sql # Database schema
├── public/                 # Static assets
├── .vscode/               # VS Code configuration
└── README.md             # This file
```

## 🧪 Development

### Code Style

- **Frontend**: ESLint + Prettier for consistent code formatting
- **Backend**: Black + isort for Python code formatting
- **TypeScript**: Strict type checking enabled
- **Naming**: camelCase for JavaScript/TypeScript, snake_case for Python

### Testing

- **Frontend**: Jest + React Testing Library (to be implemented)
- **Backend**: pytest for API testing (to be implemented)

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper type annotations
4. Add tests for new functionality
5. Submit a pull request

## 🚀 Deployment

### Frontend Deployment

- Build with `npm run build`
- Deploy `dist/` folder to any static hosting (Vercel, Netlify, etc.)

### Backend Deployment

- Deploy to any Python hosting platform (Railway, Heroku, DigitalOcean, etc.)
- Ensure environment variables are properly configured
- Use production WSGI server like Gunicorn

### Database

- Supabase handles hosting and scaling automatically
- Backup policies can be configured in Supabase dashboard

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For questions, issues, or contributions:

- Create an issue in the repository
- Contact the development team
- Check the documentation for troubleshooting guides

## 🔮 Roadmap

### Short Term

- [ ] Complete backend API implementation
- [ ] Add comprehensive tests
- [ ] Implement real-time collaboration features
- [ ] Add more export formats

### Long Term

- [ ] Support for more LLM providers
- [ ] Advanced annotation analytics
- [ ] Integration with ML training pipelines
- [ ] Mobile responsive improvements
- [ ] Automated annotation workflows

---

## 🚀 Quick Start

For the fastest way to get started:

1. **Clone and setup frontend:**

   ```bash
   npm install
   npm run dev
   ```

2. **Setup backend in another terminal:**

   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Configure Supabase:**

   - Create account at supabase.com
   - Create new project
   - Run the SQL schema
   - Add environment variables

4. **Start annotating!** 🎉

The application will be available at `http://localhost:5173` (frontend) and `http://localhost:8000` (backend API).

> > > > > > > 98bb8d4 (push all codes to git repo)
