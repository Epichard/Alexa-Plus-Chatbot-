"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from .endpoints import auth, residents, calls, system

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(residents.router, prefix="/residents", tags=["residents"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(system.router, prefix="/system", tags=["system"])

# Health check endpoint for API
@api_router.get("/health")
async def api_health():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "alexa-plus-chatbot-api-v1",
        "version": "1.0.0"
    }