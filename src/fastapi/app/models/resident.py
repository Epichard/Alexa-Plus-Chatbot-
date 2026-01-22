"""
Resident Profile data models
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class ResidentBase(BaseModel):
    """Base resident model"""
    name: str = Field(..., description="Full name of the resident")
    room_number: str = Field(..., description="Room assignment")
    device_id: Optional[str] = Field(None, description="Associated Echo Show device ID")
    care_level: str = Field(default="standard", description="Level of care required")
    emergency_contacts: List[Dict[str, str]] = Field(default_factory=list, description="Emergency contact information")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Communication preferences")
    active: bool = Field(default=True, description="Whether resident is currently active")


class ResidentCreate(ResidentBase):
    """Model for creating new residents"""
    pass


class ResidentUpdate(BaseModel):
    """Model for updating resident information"""
    name: Optional[str] = None
    room_number: Optional[str] = None
    device_id: Optional[str] = None
    care_level: Optional[str] = None
    emergency_contacts: Optional[List[Dict[str, str]]] = None
    preferences: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


class ResidentProfile(ResidentBase):
    """Complete resident profile model"""
    resident_id: str = Field(..., description="Unique resident identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }