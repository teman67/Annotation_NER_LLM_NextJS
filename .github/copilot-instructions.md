<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Scientific Text Annotator Project Instructions

This is a full-stack scientific text annotation application with the following architecture:

## Frontend (React + TypeScript + Vite)

- Uses React Router for navigation
- Tailwind CSS for styling
- Supabase for authentication and database
- React Query for data fetching
- Heroicons for icons
- React Hot Toast for notifications

## Backend (FastAPI + Python)

- FastAPI for REST API
- Supabase for database (PostgreSQL)
- JWT authentication
- LLM integration (OpenAI GPT, Anthropic Claude)
- File upload and processing
- Cost calculation and analytics

## Key Features

- AI-powered text annotation using LLMs
- Custom tag definition management
- Project and file organization
- Cost tracking and estimation
- Export capabilities (JSON, CSV, CoNLL)
- Real-time annotation visualization

## Code Style Guidelines

- Use TypeScript for all React components
- Follow React hooks patterns
- Use Tailwind CSS utility classes
- Implement proper error handling
- Use async/await for API calls
- Follow RESTful API conventions
- Use proper TypeScript types and interfaces

## Component Structure

- Pages in `src/pages/`
- Reusable components in `src/components/`
- Context providers in `src/contexts/`
- API utilities in `src/utils/` or `src/services/`
- Types in `src/types/`

## Backend Structure

- API routes in `app/api/`
- Business logic in `app/services/`
- Database models and schemas
- Configuration in `app/config.py`
- Authentication utilities

When generating code:

1. Use proper TypeScript types
2. Handle loading and error states
3. Follow existing patterns and conventions
4. Include proper accessibility attributes
5. Use responsive design principles
6. Implement proper form validation
7. Add appropriate loading indicators
8. Use consistent naming conventions
