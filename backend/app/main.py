from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import traceback

from app.config import settings
from app.database import init_db
from app.api import auth, annotations, tags, files, users, projects, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Scientific Text Annotator API",
    description="Backend API for Scientific Text Annotation with LLM integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global exception handler to always return JSON
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_detail = {
        "error": True,
        "message": "Internal server error",
        "detail": str(exc),
        "traceback": traceback.format_exc(),
        "path": str(request.url.path),
        "method": request.method
    }
    print(f"Exception in {request.method} {request.url.path}: {exc}")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content=error_detail
    )

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(annotations.router, prefix="/api/annotations", tags=["Annotations"])
app.include_router(tags.router, prefix="/api/tags", tags=["Tags"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    return {"message": "Scientific Text Annotator API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
