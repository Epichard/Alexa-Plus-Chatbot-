"""
Resident management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from ....models.resident import ResidentProfile, ResidentCreate, ResidentUpdate
from ....models.user import User
from ....db.repositories import ResidentRepository
from .auth import get_current_active_user

router = APIRouter()
resident_repo = ResidentRepository()


@router.get("/", response_model=List[ResidentProfile])
async def get_residents(
    active_only: bool = True,
    current_user: User = Depends(get_current_active_user)
):
    """Get all residents"""
    residents = await resident_repo.get_all(active_only=active_only)
    return residents


@router.get("/{resident_id}", response_model=ResidentProfile)
async def get_resident(
    resident_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get resident by ID"""
    resident = await resident_repo.get_by_id(resident_id)
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )
    return resident


@router.post("/", response_model=ResidentProfile)
async def create_resident(
    resident_data: ResidentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create new resident"""
    # Check if room number is already taken
    existing_residents = await resident_repo.get_all(active_only=True)
    for resident in existing_residents:
        if resident.room_number == resident_data.room_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room {resident_data.room_number} is already occupied"
            )
    
    resident = await resident_repo.create(resident_data)
    return resident


@router.put("/{resident_id}", response_model=ResidentProfile)
async def update_resident(
    resident_id: str,
    resident_data: ResidentUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update resident information"""
    # Check if resident exists
    existing_resident = await resident_repo.get_by_id(resident_id)
    if not existing_resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )
    
    # Check room number conflict if updating room
    if resident_data.room_number and resident_data.room_number != existing_resident.room_number:
        all_residents = await resident_repo.get_all(active_only=True)
        for resident in all_residents:
            if resident.resident_id != resident_id and resident.room_number == resident_data.room_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Room {resident_data.room_number} is already occupied"
                )
    
    updated_resident = await resident_repo.update(resident_id, resident_data)
    if not updated_resident:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update resident"
        )
    
    return updated_resident


@router.delete("/{resident_id}")
async def delete_resident(
    resident_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete resident (soft delete)"""
    success = await resident_repo.delete(resident_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )
    
    return {"message": "Resident deactivated successfully"}