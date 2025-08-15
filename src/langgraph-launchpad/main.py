import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .api.routes import chat, threads, users
from .config.settings import get_settings
from .core.database import create_tables
from .utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()
    logger = structlog.get_logger()
    
    logger.info("Starting LangGraph Launchpad", version=app.version)
    
    # Create database tables
    create_tables()
    logger.info("Database tables created/verified")
    
    yield
    
    logger.info("Shutting down LangGraph Launchpad")


def create_app() -> FastAPI:
    """Create FastAPI application instance."""
    settings = get_settings()
    setup_logging(settings.log_level, settings.debug)
    
    app = FastAPI(
        title="LangGraph Launchpad",
        description="Professional FastAPI-based REST API for LangGraph multi-agent systems",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure as needed
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(threads.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    
    @app.get("/", include_in_schema=False)
    async def root():
        """Redirect to documentation."""
        return RedirectResponse(url="/docs")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": app.version}
    
    return app


def main() -> None:
    """Main entry point for CLI usage."""
    settings = get_settings()
    
    uvicorn.run(
        "langgraph_launchpad.main:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None,  # We handle logging ourselves
    )


if __name__ == "__main__":
    main()