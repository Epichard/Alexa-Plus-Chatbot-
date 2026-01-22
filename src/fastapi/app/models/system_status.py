"""
System Status data models
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class ComponentStatus(str, Enum):
    """Status levels for system components"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class SystemComponent(str, Enum):
    """System components that can be monitored"""
    ALEXA_SKILL = "alexa_skill"
    LAMBDA_BACKEND = "lambda_backend"
    FASTAPI_BACKEND = "fastapi_backend"
    DASHBOARD = "dashboard"
    DYNAMODB = "dynamodb"
    SNS = "sns"


class SystemStatus(BaseModel):
    """System status model"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    component: SystemComponent = Field(..., description="System component being monitored")
    status: ComponentStatus = Field(..., description="Current status of the component")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    alerts: List[str] = Field(default_factory=list, description="Active alerts or issues")
    response_time: Optional[float] = Field(None, description="Component response time in milliseconds")
    uptime: Optional[float] = Field(None, description="Component uptime percentage")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SystemOverview(BaseModel):
    """Overall system health overview"""
    overall_status: ComponentStatus
    components: List[SystemStatus]
    last_updated: datetime
    active_alerts: int
    total_calls_today: int
    active_residents: int