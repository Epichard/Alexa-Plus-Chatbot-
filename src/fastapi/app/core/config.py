"""
Configuration management for FastAPI application
Handles environment variables and application settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application settings
    APP_NAME: str = "Alexa Plus Chatbot API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # AWS settings
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # DynamoDB settings
    DYNAMODB_TABLE_CALLS: str = "alexa-care-calls"
    DYNAMODB_TABLE_RESIDENTS: str = "alexa-care-residents"
    DYNAMODB_TABLE_USERS: str = "alexa-care-users"
    DYNAMODB_ENDPOINT_URL: Optional[str] = None  # For local development
    
    # SNS settings
    SNS_TOPIC_ARN: str = ""
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # WebSocket settings
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 100
    
    # API settings
    API_RATE_LIMIT: str = "100/minute"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings