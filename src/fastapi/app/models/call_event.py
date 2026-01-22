"""
Call Event data models
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class CallEventType(str, Enum):
    """Types of call events"""
    TOUCH_CALL = "touch_call"
    EMERGENCY = "emergency"
    NURSE_COMM = "nurse_comm"


class CallEventStatus(str, Enum):
    """Status of call events"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class CallEventBase(BaseModel):
    """Base call event model"""
    resident_id: str = Field(..., description="ID of the resident making the call")
    event_type: CallEventType = Field(..., description="Type of call event")
    message: Optional[str] = Field(None, description="Message content for nurse communications")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event data")


class CallEventCreate(CallEventBase):
    """Model for creating new call events"""
    pass


class CallEventUpdate(BaseModel):
    """Model for updating call events"""
    status: Optional[CallEventStatus] = None
    caregiver_id: Optional[str] = None
    response_time: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class CallEvent(CallEventBase):
    """Complete call event model"""
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(..., description="When the event occurred")
    status: CallEventStatus = Field(default=CallEventStatus.ACTIVE, description="Current event status")
    caregiver_id: Optional[str] = Field(None, description="ID of responding caregiver")
    response_time: Optional[int] = Field(None, description="Time to acknowledgment in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }