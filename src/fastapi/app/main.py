"""
FastAPI main application for Alexa Plus Chatbot
Provides REST API and WebSocket endpoints for care home management
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import os
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging import setup_logging
from .api.v1.api import api_router
from .websocket.manager import websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    setup_logging()
    logging.info("Starting Alexa Plus Chatbot FastAPI backend")
    
    # Initialize database connections
    from .db.dynamodb import init_dynamodb
    await init_dynamodb()
    
    # Initialize SNS client
    from .services.sns import init_sns
    await init_sns()
    
    yield
    
    # Shutdown
    logging.info("Shutting down Alexa Plus Chatbot FastAPI backend")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Alexa Plus Chatbot API",
        description="REST API and WebSocket server for care home intercom system",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan
    )
    
    # Add security middleware
    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(websocket_router, prefix="/ws")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "alexa-plus-chatbot-api",
            "version": "1.0.0"
        }
    
    return app


# Create the application instance
app = create_application()