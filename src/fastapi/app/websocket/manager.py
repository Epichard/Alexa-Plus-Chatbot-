"""
WebSocket connection manager for real-time updates
"""

import json
import logging
from typing import Dict, List, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter

logger = logging.getLogger(__name__)

websocket_router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        # User connections mapping
        self.user_connections: Dict[str, Set[str]] = {}
        # Connection metadata
        self.connection_metadata: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow()
        }
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
        
        logger.info(f"WebSocket connection {connection_id} established for user {user_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
    
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            metadata = self.connection_metadata.get(connection_id, {})
            user_id = metadata.get("user_id")
            
            # Remove from active connections
            del self.active_connections[connection_id]
            del self.connection_metadata[connection_id]
            
            # Remove from user connections
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            logger.info(f"WebSocket connection {connection_id} disconnected for user {user_id}")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {str(e)}")
                self.disconnect(connection_id)
    
    async def send_to_user(self, message: dict, user_id: str):
        """Send message to all connections for a user"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id].copy():
                await self.send_personal_message(message, connection_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all active connections"""
        disconnected = []
        
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {str(e)}")
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    async def send_call_event(self, call_event: dict):
        """Send call event to all connected clients"""
        message = {
            "type": "call_event",
            "data": call_event,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def send_system_status(self, status_data: dict):
        """Send system status update"""
        message = {
            "type": "system_status",
            "data": status_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def send_resident_update(self, resident_data: dict):
        """Send resident profile update"""
        message = {
            "type": "resident_update",
            "data": resident_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    def get_user_count(self) -> int:
        """Get number of unique connected users"""
        return len(self.user_connections)


# Global connection manager instance
manager = ConnectionManager()


@websocket_router.websocket("/live-updates")
async def websocket_live_updates(websocket: WebSocket):
    """WebSocket endpoint for live system updates"""
    connection_id = f"conn_{datetime.utcnow().timestamp()}"
    
    try:
        await manager.connect(websocket, connection_id)
        
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "ping":
                    # Handle ping/pong for connection health
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, connection_id)
                    
                    # Update last ping time
                    if connection_id in manager.connection_metadata:
                        manager.connection_metadata[connection_id]["last_ping"] = datetime.utcnow()
                
                elif message_type == "subscribe":
                    # Handle subscription to specific event types
                    await manager.send_personal_message({
                        "type": "subscription_confirmed",
                        "subscriptions": message.get("events", []),
                        "timestamp": datetime.utcnow().isoformat()
                    }, connection_id)
                
                else:
                    logger.warning(f"Unknown message type: {message_type}")
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from {connection_id}")
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {str(e)}")
        manager.disconnect(connection_id)


@websocket_router.websocket("/call-status")
async def websocket_call_status(websocket: WebSocket):
    """WebSocket endpoint specifically for call status updates"""
    connection_id = f"call_{datetime.utcnow().timestamp()}"
    
    try:
        await manager.connect(websocket, connection_id)
        
        # Send current call status on connection
        await manager.send_personal_message({
            "type": "call_status_init",
            "message": "Connected to call status updates",
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
        
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, connection_id)
                    
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Call status WebSocket error for {connection_id}: {str(e)}")
        manager.disconnect(connection_id)


# Utility functions for other modules to use
async def broadcast_call_event(call_event: dict):
    """Broadcast call event to all connected clients"""
    await manager.send_call_event(call_event)


async def broadcast_system_status(status_data: dict):
    """Broadcast system status to all connected clients"""
    await manager.send_system_status(status_data)


async def broadcast_resident_update(resident_data: dict):
    """Broadcast resident update to all connected clients"""
    await manager.send_resident_update(resident_data)


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance"""
    return manager