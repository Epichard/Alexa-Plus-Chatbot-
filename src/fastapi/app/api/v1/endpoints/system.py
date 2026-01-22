"""
System status and monitoring endpoints
"""

from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends

from ....models.system_status import SystemStatus, SystemOverview, ComponentStatus, SystemComponent
from ....models.user import User
from ....db.repositories import CallEventRepository, ResidentRepository
from .auth import get_current_active_user

router = APIRouter()


@router.get("/status", response_model=SystemOverview)
async def get_system_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get overall system status"""
    
    # Get component statuses (simplified for now)
    components = [
        SystemStatus(
            component=SystemComponent.FASTAPI_BACKEND,
            status=ComponentStatus.HEALTHY,
            metrics={"response_time": 45.2, "memory_usage": 78.5},
            response_time=45.2,
            uptime=99.9
        ),
        SystemStatus(
            component=SystemComponent.LAMBDA_BACKEND,
            status=ComponentStatus.HEALTHY,
            metrics={"invocations": 1250, "errors": 2},
            response_time=120.0,
            uptime=99.8
        ),
        SystemStatus(
            component=SystemComponent.DYNAMODB,
            status=ComponentStatus.HEALTHY,
            metrics={"read_capacity": 85.0, "write_capacity": 45.0},
            response_time=15.5,
            uptime=100.0
        ),
        SystemStatus(
            component=SystemComponent.SNS,
            status=ComponentStatus.HEALTHY,
            metrics={"messages_sent": 890, "delivery_rate": 99.9},
            response_time=25.0,
            uptime=99.9
        )
    ]
    
    # Calculate overall status
    overall_status = ComponentStatus.HEALTHY
    if any(c.status == ComponentStatus.DOWN for c in components):
        overall_status = ComponentStatus.DOWN
    elif any(c.status == ComponentStatus.DEGRADED for c in components):
        overall_status = ComponentStatus.DEGRADED
    
    # Get metrics
    call_repo = CallEventRepository()
    resident_repo = ResidentRepository()
    
    # Count today's calls
    today_calls = await call_repo.get_recent(limit=1000)  # Simplified
    today = datetime.utcnow().date()
    calls_today = len([c for c in today_calls if c.timestamp.date() == today])
    
    # Count active residents
    residents = await resident_repo.get_all(active_only=True)
    active_residents = len(residents)
    
    # Count active alerts
    active_alerts = sum(len(c.alerts) for c in components)
    
    return SystemOverview(
        overall_status=overall_status,
        components=components,
        last_updated=datetime.utcnow(),
        active_alerts=active_alerts,
        total_calls_today=calls_today,
        active_residents=active_residents
    )


@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "alexa-plus-chatbot-system"
    }


@router.get("/metrics")
async def get_system_metrics(
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed system metrics"""
    
    call_repo = CallEventRepository()
    resident_repo = ResidentRepository()
    
    # Get recent calls for metrics
    recent_calls = await call_repo.get_recent(limit=1000)
    
    # Calculate metrics
    now = datetime.utcnow()
    today = now.date()
    week_ago = now - timedelta(days=7)
    
    calls_today = len([c for c in recent_calls if c.timestamp.date() == today])
    calls_this_week = len([c for c in recent_calls if c.timestamp >= week_ago])
    
    # Response time metrics
    acknowledged_calls = [c for c in recent_calls if c.response_time is not None]
    avg_response_time = sum(c.response_time for c in acknowledged_calls) / len(acknowledged_calls) if acknowledged_calls else 0
    
    # Call type breakdown
    call_types = {}
    for call in recent_calls:
        call_types[call.event_type] = call_types.get(call.event_type, 0) + 1
    
    # Active residents
    residents = await resident_repo.get_all(active_only=True)
    
    return {
        "timestamp": now.isoformat(),
        "calls": {
            "today": calls_today,
            "this_week": calls_this_week,
            "total_recent": len(recent_calls),
            "by_type": call_types,
            "avg_response_time_seconds": round(avg_response_time, 2)
        },
        "residents": {
            "active": len(residents),
            "total": len(await resident_repo.get_all(active_only=False))
        },
        "system": {
            "uptime_hours": 24.5,  # Simplified
            "memory_usage_percent": 78.5,
            "cpu_usage_percent": 45.2
        }
    }