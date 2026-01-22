"""
End-to-end tests for the complete care home system
Tests the integration between Alexa skill, Lambda backend, FastAPI, and Dashboard
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

# Mock AWS services for testing
@pytest.fixture
def mock_dynamodb():
    """Mock DynamoDB for testing"""
    with patch('boto3.resource') as mock_resource:
        mock_table = Mock()
        mock_resource.return_value.Table.return_value = mock_table
        yield mock_table

@pytest.fixture
def mock_sns():
    """Mock SNS for testing"""
    with patch('boto3.client') as mock_client:
        mock_sns_client = Mock()
        mock_client.return_value = mock_sns_client
        yield mock_sns_client


class TestAlexaToLambdaFlow:
    """Test Alexa skill to Lambda backend flow"""
    
    def test_touch_call_event_processing(self, mock_dynamodb, mock_sns):
        """Test processing of touch call events from Alexa"""
        from src.lambda.lambda_function import AlexaCareHandler
        
        handler = AlexaCareHandler()
        
        # Mock Alexa touch event
        alexa_event = {
            "request": {
                "type": "Alexa.Presentation.APL.UserEvent"
            },
            "context": {
                "System": {
                    "device": {
                        "deviceId": "room1_device_123"
                    }
                }
            }
        }
        
        # Process the event
        response = handler.lambda_handler(alexa_event, None)
        
        # Verify response structure
        assert "response" in response
        assert "outputSpeech" in response["response"]
        assert "Calling caregiver now" in response["response"]["outputSpeech"]["text"]
    
    def test_emergency_help_processing(self, mock_dynamodb, mock_sns):
        """Test emergency help request processing"""
        from src.lambda.lambda_function import AlexaCareHandler
        
        handler = AlexaCareHandler()
        
        # Mock emergency intent
        alexa_event = {
            "request": {
                "type": "IntentRequest",
                "intent": {
                    "name": "HelpWakeWordIntent"
                }
            },
            "context": {
                "System": {
                    "device": {
                        "deviceId": "room2_device_456"
                    }
                }
            }
        }
        
        response = handler.lambda_handler(alexa_event, None)
        
        # Verify emergency response
        assert "Emergency help is on the way" in response["response"]["outputSpeech"]["text"]
    
    def test_nurse_communication_flow(self, mock_dynamodb, mock_sns):
        """Test nurse communication message relay"""
        from src.lambda.lambda_function import AlexaCareHandler
        
        handler = AlexaCareHandler()
        
        # Mock nurse communication intent
        alexa_event = {
            "request": {
                "type": "IntentRequest",
                "intent": {
                    "name": "NurseWakeWordIntent",
                    "slots": {
                        "message": {
                            "value": "I need water"
                        }
                    }
                }
            },
            "context": {
                "System": {
                    "device": {
                        "deviceId": "room1_device_123"
                    }
                }
            }
        }
        
        response = handler.lambda_handler(alexa_event, None)
        
        # Verify message relay response
        assert "Hold on" in response["response"]["outputSpeech"]["text"]


class TestLambdaToFastAPIIntegration:
    """Test Lambda backend to FastAPI integration via SNS"""
    
    @pytest.mark.asyncio
    async def test_sns_message_processing(self):
        """Test SNS message processing from Lambda to FastAPI"""
        from src.fastapi.app.services.sns import handle_sns_message
        
        # Mock SNS message from Lambda
        sns_message = {
            "event_type": "call_event",
            "data": {
                "call_id": "test-call-123",
                "room": "room1",
                "type": "touch_call",
                "message": "Jane is calling",
                "timestamp": datetime.now().isoformat(),
                "status": "pending"
            },
            "source": "lambda_backend"
        }
        
        # Process the message (this would normally trigger WebSocket broadcast)
        await handle_sns_message(sns_message)
        
        # Test passes if no exceptions are raised
        assert True
    
    @pytest.mark.asyncio
    async def test_call_acknowledgment_flow(self):
        """Test call acknowledgment from dashboard back to Lambda"""
        from src.fastapi.app.services.sns import send_acknowledgment_to_lambda
        
        # Mock acknowledgment
        call_id = "test-call-123"
        caregiver_id = "caregiver-1"
        
        # This would normally send SNS message back to Lambda
        await send_acknowledgment_to_lambda(call_id, caregiver_id)
        
        # Test passes if no exceptions are raised
        assert True


class TestDashboardIntegration:
    """Test dashboard integration with backend"""
    
    def test_dashboard_websocket_connection(self):
        """Test WebSocket connection for real-time updates"""
        # This would test WebSocket connection in a real scenario
        # For now, we'll test the connection manager setup
        from src.fastapi.app.websocket.manager import ConnectionManager
        
        manager = ConnectionManager()
        assert manager.get_connection_count() == 0
        assert manager.get_user_count() == 0
    
    def test_real_time_call_broadcast(self):
        """Test real-time call event broadcasting"""
        from src.fastapi.app.websocket.manager import manager
        
        # Mock call event
        call_event = {
            "event_id": "test-123",
            "resident_id": "resident-1",
            "event_type": "touch_call",
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }
        
        # Test broadcast function exists and can be called
        # In real scenario, this would send to connected WebSocket clients
        assert hasattr(manager, 'send_call_event')


class TestSystemHealthMonitoring:
    """Test system health monitoring and status reporting"""
    
    def test_component_health_checks(self):
        """Test individual component health checks"""
        from src.fastapi.app.models.system_status import SystemStatus, ComponentStatus, SystemComponent
        
        # Test system status model
        status = SystemStatus(
            component=SystemComponent.FASTAPI_BACKEND,
            status=ComponentStatus.HEALTHY,
            metrics={"response_time": 45.2},
            alerts=[]
        )
        
        assert status.component == SystemComponent.FASTAPI_BACKEND
        assert status.status == ComponentStatus.HEALTHY
        assert status.metrics["response_time"] == 45.2
    
    def test_overall_system_status(self):
        """Test overall system status aggregation"""
        from src.fastapi.app.models.system_status import SystemOverview, ComponentStatus
        
        overview = SystemOverview(
            overall_status=ComponentStatus.HEALTHY,
            components=[],
            last_updated=datetime.now().isoformat(),
            active_alerts=0,
            total_calls_today=15,
            active_residents=8
        )
        
        assert overview.overall_status == ComponentStatus.HEALTHY
        assert overview.total_calls_today == 15
        assert overview.active_residents == 8


class TestDataConsistency:
    """Test data consistency across systems"""
    
    def test_call_event_data_model_consistency(self):
        """Test that call event models are consistent across Lambda and FastAPI"""
        from src.fastapi.app.models.call_event import CallEvent, CallEventType, CallEventStatus
        
        # Test FastAPI model
        call_event = CallEvent(
            event_id="test-123",
            timestamp=datetime.now(),
            resident_id="resident-1",
            event_type=CallEventType.TOUCH_CALL,
            status=CallEventStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert call_event.event_type == CallEventType.TOUCH_CALL
        assert call_event.status == CallEventStatus.ACTIVE
        
        # Verify enum values match Lambda expectations
        assert CallEventType.TOUCH_CALL.value == "touch_call"
        assert CallEventType.EMERGENCY.value == "emergency"
        assert CallEventType.NURSE_COMM.value == "nurse_comm"
    
    def test_resident_data_model_consistency(self):
        """Test resident profile model consistency"""
        from src.fastapi.app.models.resident import ResidentProfile
        
        resident = ResidentProfile(
            resident_id="resident-1",
            name="Jane Doe",
            room_number="Room 1",
            care_level="standard",
            emergency_contacts=[],
            preferences={},
            active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert resident.name == "Jane Doe"
        assert resident.room_number == "Room 1"
        assert resident.active is True


class TestErrorHandling:
    """Test error handling across the system"""
    
    def test_lambda_error_handling(self):
        """Test Lambda function error handling"""
        from src.lambda.lambda_function import AlexaCareHandler
        
        handler = AlexaCareHandler()
        
        # Test with malformed event
        malformed_event = {"invalid": "event"}
        
        response = handler.lambda_handler(malformed_event, None)
        
        # Should return error response, not crash
        assert "response" in response
        assert "error" in response["response"]["outputSpeech"]["text"].lower()
    
    def test_fastapi_error_handling(self):
        """Test FastAPI error handling"""
        from fastapi.testclient import TestClient
        from src.fastapi.app.main import app
        
        client = TestClient(app)
        
        # Test invalid endpoint
        response = client.get("/api/v1/invalid-endpoint")
        assert response.status_code == 404
        
        # Test invalid authentication
        response = client.get("/api/v1/residents")
        assert response.status_code == 401  # Unauthorized


if __name__ == "__main__":
    pytest.main([__file__, "-v"])