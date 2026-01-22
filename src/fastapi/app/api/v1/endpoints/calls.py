"""
Call event endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from ....models.call_event import CallEvent, CallEventCreate, CallEventUpdate
from ....models.user import User
from ....db.repositories import CallEventRepository
from .auth import get_current_active_user

router = APIRouter()
call_repo = CallEventRepository()


@router.get("/recent", response_model=List[CallEvent])
async def get_recent_calls(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user)
):
    """Get recent call events"""
    calls = await call_repo.get_recent(limit=limit)
    return calls


@router.get("/resident/{resident_id}", response_model=List[CallEvent])
async def get_calls_by_resident(
    resident_id: str,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user)
):
    """Get call events for a specific resident"""
    calls = await call_repo.get_by_resident(resident_id, limit=limit)
    return calls


@router.get("/{event_id}", response_model=CallEvent)
async def get_call_event(
    event_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get call event by ID"""
    call = await call_repo.get_by_id(event_id)
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call event not found"
        )
    return call


@router.post("/", response_model=CallEvent)
async def create_call_event(
    call_data: CallEventCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create new call event (typically called by Lambda backend)"""
    call = await call_repo.create(call_data)
    return call


@router.put("/{event_id}", response_model=CallEvent)
async def update_call_event(
    event_id: str,
    update_data: CallEventUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update call event (acknowledge, resolve, etc.)"""
    # Add caregiver ID to update if acknowledging
    if update_data.status and not update_data.caregiver_id:
        update_data.caregiver_id = current_user.user_id
    
    updated_call = await call_repo.update(event_id, update_data)
    if not updated_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call event not found"
        )
    
    return updated_call


@router.post("/{event_id}/acknowledge", response_model=CallEvent)
async def acknowledge_call(
    event_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Acknowledge a call event"""
    update_data = CallEventUpdate(
        status="acknowledged",
        caregiver_id=current_user.user_id
    )
    
    updated_call = await call_repo.update(event_id, update_data)
    if not updated_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call event not found"
        )
    
    return updated_call


@router.post("/{event_id}/resolve", response_model=CallEvent)
async def resolve_call(
    event_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Resolve a call event"""
    update_data = CallEventUpdate(
        status="resolved",
        caregiver_id=current_user.user_id
    )
    
    updated_call = await call_repo.update(event_id, update_data)
    if not updated_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call event not found"
        )
    
    return updated_call