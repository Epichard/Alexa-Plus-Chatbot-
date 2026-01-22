"""
SNS (Simple Notification Service) integration
"""

import json
import logging
import aioboto3
from typing import Dict, Any, Optional
from datetime import datetime

from ..core.config import settings
from ..websocket.manager import broadcast_call_event, broadcast_system_status

logger = logging.getLogger(__name__)

# Global SNS client
_sns_client = None


class SNSService:
    """Service for SNS operations"""
    
    def __init__(self, sns_client):
        self.sns_client = sns_client
        self.topic_arn = settings.SNS_TOPIC_ARN
    
    async def publish_call_event(self, call_event: Dict[str, Any]) -> bool:
        """Publish call event to SNS topic"""
        try:
            message = {
                "event_type": "call_event",
                "data": call_event,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "fastapi_backend"
            }
            
            response = await self.sns_client.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(message),
                Subject="Care Home Call Event",
                MessageAttributes={
                    'event_type': {
                        'DataType': 'String',
                        'StringValue': 'call_event'
                    },
                    'source': {
                        'DataType': 'String', 
                        'StringValue': 'fastapi_backend'
                    }
                }
            )
            
            logger.info(f"Published call event to SNS: {response['MessageId']}")
            
            # Also broadcast to WebSocket clients
            await broadcast_call_event(call_event)
            
            return True
            
        except Exception as e:
            logger.error(f"Error publishing call event to SNS: {str(e)}")
            return False
    
    async def publish_system_status(self, status_data: Dict[str, Any]) -> bool:
        """Publish system status update to SNS topic"""
        try:
            message = {
                "event_type": "system_status",
                "data": status_data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "fastapi_backend"
            }
            
            response = await self.sns_client.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(message),
                Subject="Care Home System Status",
                MessageAttributes={
                    'event_type': {
                        'DataType': 'String',
                        'StringValue': 'system_status'
                    },
                    'source': {
                        'DataType': 'String',
                        'StringValue': 'fastapi_backend'
                    }
                }
            )
            
            logger.info(f"Published system status to SNS: {response['MessageId']}")
            
            # Also broadcast to WebSocket clients
            await broadcast_system_status(status_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error publishing system status to SNS: {str(e)}")
            return False
    
    async def publish_resident_update(self, resident_data: Dict[str, Any]) -> bool:
        """Publish resident profile update to SNS topic"""
        try:
            message = {
                "event_type": "resident_update",
                "data": resident_data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "fastapi_backend"
            }
            
            response = await self.sns_client.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(message),
                Subject="Care Home Resident Update",
                MessageAttributes={
                    'event_type': {
                        'DataType': 'String',
                        'StringValue': 'resident_update'
                    },
                    'source': {
                        'DataType': 'String',
                        'StringValue': 'fastapi_backend'
                    }
                }
            )
            
            logger.info(f"Published resident update to SNS: {response['MessageId']}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing resident update to SNS: {str(e)}")
            return False
    
    async def subscribe_to_lambda_events(self, callback_url: str) -> bool:
        """Subscribe to Lambda backend events (for future use)"""
        try:
            # This would set up subscription to receive events from Lambda backend
            # For now, we'll assume Lambda publishes to the same topic
            logger.info(f"Would subscribe to Lambda events at {callback_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to Lambda events: {str(e)}")
            return False


async def init_sns():
    """Initialize SNS client"""
    global _sns_client
    
    try:
        session = aioboto3.Session()
        
        # Configure SNS client
        sns_config = {
            'region_name': settings.AWS_REGION
        }
        
        # Add credentials if provided
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            sns_config.update({
                'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY
            })
        
        _sns_client = session.client('sns', **sns_config)
        logger.info("SNS client initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize SNS client: {str(e)}")
        raise


def get_sns_service() -> SNSService:
    """Get SNS service instance"""
    if _sns_client is None:
        raise RuntimeError("SNS not initialized. Call init_sns() first.")
    return SNSService(_sns_client)


async def handle_sns_message(message: Dict[str, Any]):
    """Handle incoming SNS message (from Lambda backend)"""
    try:
        event_type = message.get("event_type")
        data = message.get("data", {})
        source = message.get("source", "unknown")
        
        logger.info(f"Received SNS message: {event_type} from {source}")
        
        if event_type == "call_event":
            # Broadcast call event to WebSocket clients
            await broadcast_call_event(data)
            
        elif event_type == "system_status":
            # Broadcast system status to WebSocket clients
            await broadcast_system_status(data)
            
        else:
            logger.warning(f"Unknown SNS message type: {event_type}")
            
    except Exception as e:
        logger.error(f"Error handling SNS message: {str(e)}")


# Message processing functions for integration with Lambda backend
async def process_lambda_call_event(event_data: Dict[str, Any]):
    """Process call event from Lambda backend"""
    try:
        # Transform Lambda event format to our format if needed
        call_event = {
            "event_id": event_data.get("call_id"),
            "resident_id": event_data.get("room", "unknown"),
            "event_type": event_data.get("type", "unknown"),
            "message": event_data.get("message", ""),
            "timestamp": event_data.get("timestamp"),
            "status": event_data.get("status", "active")
        }
        
        # Broadcast to WebSocket clients
        await broadcast_call_event(call_event)
        
        logger.info(f"Processed Lambda call event: {call_event['event_id']}")
        
    except Exception as e:
        logger.error(f"Error processing Lambda call event: {str(e)}")


async def send_acknowledgment_to_lambda(call_id: str, caregiver_id: str):
    """Send acknowledgment back to Lambda backend via SNS"""
    try:
        sns_service = get_sns_service()
        
        ack_data = {
            "call_id": call_id,
            "caregiver_id": caregiver_id,
            "acknowledged_at": datetime.utcnow().isoformat(),
            "source": "fastapi_dashboard"
        }
        
        message = {
            "event_type": "call_acknowledgment",
            "data": ack_data,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "fastapi_backend"
        }
        
        await sns_service.sns_client.publish(
            TopicArn=settings.SNS_TOPIC_ARN,
            Message=json.dumps(message),
            Subject="Call Acknowledgment",
            MessageAttributes={
                'event_type': {
                    'DataType': 'String',
                    'StringValue': 'call_acknowledgment'
                },
                'target': {
                    'DataType': 'String',
                    'StringValue': 'lambda_backend'
                }
            }
        )
        
        logger.info(f"Sent acknowledgment to Lambda for call {call_id}")
        
    except Exception as e:
        logger.error(f"Error sending acknowledgment to Lambda: {str(e)}")