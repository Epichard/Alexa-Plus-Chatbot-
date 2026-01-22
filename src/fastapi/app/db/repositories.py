"""
Repository pattern for database operations
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from boto3.dynamodb.conditions import Key, Attr

from ..models import CallEvent, CallEventCreate, CallEventUpdate
from ..models import ResidentProfile, ResidentCreate, ResidentUpdate  
from ..models import User, UserCreate, UserUpdate
from ..core.config import settings
from .dynamodb import get_table

logger = logging.getLogger(__name__)


class CallEventRepository:
    """Repository for call event operations"""
    
    def __init__(self):
        self.table_name = settings.DYNAMODB_TABLE_CALLS
    
    async def create(self, call_data: CallEventCreate) -> CallEvent:
        """Create a new call event"""
        table = await get_table(self.table_name)
        
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        item = {
            'event_id': event_id,
            'timestamp': timestamp.isoformat(),
            'resident_id': call_data.resident_id,
            'event_type': call_data.event_type.value,
            'status': 'active',
            'message': call_data.message,
            'metadata': call_data.metadata or {},
            'created_at': timestamp.isoformat(),
            'updated_at': timestamp.isoformat()
        }
        
        await table.put_item(Item=item)
        
        return CallEvent(
            event_id=event_id,
            timestamp=timestamp,
            **call_data.dict()
        )
    
    async def get_by_id(self, event_id: str) -> Optional[CallEvent]:
        """Get call event by ID"""
        table = await get_table(self.table_name)
        
        response = await table.get_item(Key={'event_id': event_id})
        item = response.get('Item')
        
        if not item:
            return None
            
        return CallEvent(**item)
    
    async def update(self, event_id: str, update_data: CallEventUpdate) -> Optional[CallEvent]:
        """Update call event"""
        table = await get_table(self.table_name)
        
        # Build update expression
        update_expr = "SET updated_at = :updated_at"
        expr_values = {':updated_at': datetime.utcnow().isoformat()}
        
        if update_data.status:
            update_expr += ", #status = :status"
            expr_values[':status'] = update_data.status.value
            
        if update_data.caregiver_id:
            update_expr += ", caregiver_id = :caregiver_id"
            expr_values[':caregiver_id'] = update_data.caregiver_id
            
        if update_data.response_time is not None:
            update_expr += ", response_time = :response_time"
            expr_values[':response_time'] = update_data.response_time
            
        if update_data.metadata:
            update_expr += ", metadata = :metadata"
            expr_values[':metadata'] = update_data.metadata
        
        expr_names = {'#status': 'status'} if update_data.status else None
        
        try:
            response = await table.update_item(
                Key={'event_id': event_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values,
                ExpressionAttributeNames=expr_names,
                ReturnValues='ALL_NEW'
            )
            
            return CallEvent(**response['Attributes'])
        except Exception as e:
            logger.error(f"Error updating call event {event_id}: {str(e)}")
            return None
    
    async def get_recent(self, limit: int = 50) -> List[CallEvent]:
        """Get recent call events"""
        table = await get_table(self.table_name)
        
        # Query using timestamp index
        response = await table.scan(
            Limit=limit,
            ScanFilter={
                'timestamp': {
                    'AttributeValueList': [
                        (datetime.utcnow() - datetime.timedelta(days=7)).isoformat()
                    ],
                    'ComparisonOperator': 'GT'
                }
            }
        )
        
        items = response.get('Items', [])
        return [CallEvent(**item) for item in items]
    
    async def get_by_resident(self, resident_id: str, limit: int = 20) -> List[CallEvent]:
        """Get call events for a specific resident"""
        table = await get_table(self.table_name)
        
        response = await table.query(
            IndexName='resident-index',
            KeyConditionExpression=Key('resident_id').eq(resident_id),
            Limit=limit,
            ScanIndexForward=False  # Most recent first
        )
        
        items = response.get('Items', [])
        return [CallEvent(**item) for item in items]


class ResidentRepository:
    """Repository for resident operations"""
    
    def __init__(self):
        self.table_name = settings.DYNAMODB_TABLE_RESIDENTS
    
    async def create(self, resident_data: ResidentCreate) -> ResidentProfile:
        """Create a new resident"""
        table = await get_table(self.table_name)
        
        resident_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        item = {
            'resident_id': resident_id,
            'name': resident_data.name,
            'room_number': resident_data.room_number,
            'device_id': resident_data.device_id,
            'care_level': resident_data.care_level,
            'emergency_contacts': resident_data.emergency_contacts,
            'preferences': resident_data.preferences,
            'active': resident_data.active,
            'created_at': timestamp.isoformat(),
            'updated_at': timestamp.isoformat()
        }
        
        await table.put_item(Item=item)
        
        return ResidentProfile(
            resident_id=resident_id,
            created_at=timestamp,
            updated_at=timestamp,
            **resident_data.dict()
        )
    
    async def get_by_id(self, resident_id: str) -> Optional[ResidentProfile]:
        """Get resident by ID"""
        table = await get_table(self.table_name)
        
        response = await table.get_item(Key={'resident_id': resident_id})
        item = response.get('Item')
        
        if not item:
            return None
            
        return ResidentProfile(**item)
    
    async def get_all(self, active_only: bool = True) -> List[ResidentProfile]:
        """Get all residents"""
        table = await get_table(self.table_name)
        
        if active_only:
            response = await table.scan(
                FilterExpression=Attr('active').eq(True)
            )
        else:
            response = await table.scan()
        
        items = response.get('Items', [])
        return [ResidentProfile(**item) for item in items]
    
    async def update(self, resident_id: str, update_data: ResidentUpdate) -> Optional[ResidentProfile]:
        """Update resident"""
        table = await get_table(self.table_name)
        
        # Build update expression
        update_expr = "SET updated_at = :updated_at"
        expr_values = {':updated_at': datetime.utcnow().isoformat()}
        
        for field, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                update_expr += f", {field} = :{field}"
                expr_values[f':{field}'] = value
        
        try:
            response = await table.update_item(
                Key={'resident_id': resident_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values,
                ReturnValues='ALL_NEW'
            )
            
            return ResidentProfile(**response['Attributes'])
        except Exception as e:
            logger.error(f"Error updating resident {resident_id}: {str(e)}")
            return None
    
    async def delete(self, resident_id: str) -> bool:
        """Delete resident (soft delete by setting active=False)"""
        update_data = ResidentUpdate(active=False)
        result = await self.update(resident_id, update_data)
        return result is not None


class UserRepository:
    """Repository for user operations"""
    
    def __init__(self):
        self.table_name = settings.DYNAMODB_TABLE_USERS
    
    async def create(self, user_data: UserCreate, hashed_password: str) -> User:
        """Create a new user"""
        table = await get_table(self.table_name)
        
        user_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        item = {
            'user_id': user_id,
            'username': user_data.username,
            'email': user_data.email,
            'full_name': user_data.full_name,
            'role': user_data.role.value,
            'active': user_data.active,
            'hashed_password': hashed_password,
            'created_at': timestamp.isoformat(),
            'updated_at': timestamp.isoformat()
        }
        
        await table.put_item(Item=item)
        
        return User(
            user_id=user_id,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            active=user_data.active,
            created_at=timestamp,
            updated_at=timestamp
        )
    
    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username (includes hashed password for auth)"""
        table = await get_table(self.table_name)
        
        response = await table.query(
            IndexName='username-index',
            KeyConditionExpression=Key('username').eq(username)
        )
        
        items = response.get('Items', [])
        return items[0] if items else None
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        table = await get_table(self.table_name)
        
        response = await table.get_item(Key={'user_id': user_id})
        item = response.get('Item')
        
        if not item:
            return None
        
        # Remove hashed_password from response
        item.pop('hashed_password', None)
        return User(**item)