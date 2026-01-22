"""
Alexa Plus Chatbot - Care Home Assistant
Python Lambda Handler for AWS

Language: Python 3.9+
Purpose: Handle Alexa skill requests for care home call bell system
"""

import json
import boto3
import logging
from datetime import datetime
import uuid
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Device mapping for care home
DEVICE_MAP = {
    'main_device': 'Main Station',
    'room1_device': 'Room 1 - Jane',
    'room2_device': 'Room 2 - John', 
    'room3_device': 'Room 3 - Mary'
}

RESIDENTS = {
    'room1': 'Jane',
    'room2': 'John', 
    'room3': 'Mary'
}

class AlexaCareHandler:
    """Main handler class for Alexa Care Assistant skill"""
    
    def __init__(self):
        """Initialize handler with AWS resources"""
        try:
            self.calls_table = dynamodb.Table('CareHomeCalls')
            self.status_table = dynamodb.Table('CaregiverStatus')
        except Exception as e:
            logger.error(f"Error initializing AWS resources: {str(e)}")
            # Use mock tables for local testing
            self.calls_table = None
            self.status_table = None
        
    def lambda_handler(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """Main Lambda handler entry point"""
        try:
            logger.info(f"Received event: {json.dumps(event)}")
            
            request_type = event['request']['type']
            
            if request_type == 'LaunchRequest':
                return self.handle_launch(event)
            elif request_type == 'IntentRequest':
                return self.handle_intent(event)
            elif request_type == 'Alexa.Presentation.APL.UserEvent':
                return self.handle_touch_event(event)
            else:
                return self.build_response("I didn't understand that request.")
                
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return self.build_response("Sorry, there was an error processing your request.")
    
    def handle_launch(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle skill launch request"""
        device_id = event['context']['System']['device']['deviceId']
        
        if self.is_main_device(device_id):
            return self.build_response(
                "Care Home Assistant ready. Monitoring all rooms.",
                apl_document=self.get_main_device_apl()
            )
        else:
            return self.build_response(
                "Hello! Touch the call button or say Help for assistance.",
                apl_document=self.get_resident_device_apl()
            )
    
    def handle_intent(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intent requests"""
        intent_name = event['request']['intent']['name']
        
        if intent_name == 'HelpWakeWordIntent':
            return self.handle_help_request(event)
        elif intent_name == 'NurseWakeWordIntent':
            return self.handle_nurse_request(event)
        elif intent_name == 'CaregiverConfirmIntent':
            return self.handle_caregiver_confirm(event)
        elif intent_name == 'AMAZON.HelpIntent':
            return self.build_response("Say Help for emergency, or Nurse to send a message.")
        elif intent_name == 'AMAZON.StopIntent' or intent_name == 'AMAZON.CancelIntent':
            return self.build_response("Care Assistant standing by.")
        else:
            return self.build_response("I didn't understand that command.")
    
    def handle_touch_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle touch call button press"""
        device_id = event['context']['System']['device']['deviceId']
        room = self.get_room_from_device(device_id)
        resident_name = RESIDENTS.get(room, f"Room {room}")
        
        # Create call record
        call_id = str(uuid.uuid4())
        self.create_call_record(call_id, room, 'touch_call', resident_name)
        
        # Notify main device
        self.notify_main_device(f"{resident_name} is calling")
        
        return self.build_response(
            "Calling caregiver now. Help is on the way.",
            apl_document=self.get_calling_apl()
        )
    
    def handle_help_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency help request"""
        device_id = event['context']['System']['device']['deviceId']
        room = self.get_room_from_device(device_id)
        
        # Create emergency call record
        call_id = str(uuid.uuid4())
        self.create_call_record(call_id, room, 'emergency', 'Help Request')
        
        # Notify main device with urgency
        self.notify_main_device(f"URGENT: Help needed in {room}")
        
        return self.build_response(
            "Emergency help is on the way. Stay calm.",
            apl_document=self.get_emergency_apl()
        )
    
    def handle_nurse_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle nurse communication request"""
        device_id = event['context']['System']['device']['deviceId']
        room = self.get_room_from_device(device_id)
        resident_name = RESIDENTS.get(room, f"Room {room}")
        
        # Get message from slot
        slots = event['request']['intent'].get('slots', {})
        message = slots.get('message', {}).get('value', '')
        
        if message:
            # Create communication record
            call_id = str(uuid.uuid4())
            self.create_call_record(call_id, room, 'nurse_request', message)
            
            # Relay message to main device
            self.notify_main_device(f"{resident_name} says: {message}")
            
            return self.build_response("Hold on, I'm getting help for you.")
        else:
            return self.build_response(
                f"What do you need, {resident_name}? Please speak clearly.",
                reprompt=f"{resident_name}, I'm here to help. What do you need?"
            )
    
    def handle_caregiver_confirm(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle caregiver OK confirmation"""
        # Update latest call as acknowledged
        self.acknowledge_latest_call()
        
        return self.build_response("Acknowledged. Resident has been notified.")
    
    def create_call_record(self, call_id: str, room: str, call_type: str, message: str):
        """Create call record in DynamoDB"""
        if not self.calls_table:
            logger.info(f"Mock call record: {call_id}, {room}, {call_type}, {message}")
            return
            
        try:
            self.calls_table.put_item(
                Item={
                    'call_id': call_id,
                    'room': room,
                    'type': call_type,
                    'message': message,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'pending'
                }
            )
            logger.info(f"Created call record: {call_id}")
        except Exception as e:
            logger.error(f"Error creating call record: {str(e)}")
    
    def notify_main_device(self, message: str):
        """Send notification to main device via SNS"""
        try:
            topic_arn = 'arn:aws:sns:us-east-1:123456789012:CareHomeNotifications'
            sns.publish(
                TopicArn=topic_arn,
                Message=message,
                Subject='Care Home Alert'
            )
            logger.info(f"Sent notification: {message}")
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    def acknowledge_latest_call(self):
        """Mark latest call as acknowledged"""
        if not self.calls_table:
            logger.info("Mock acknowledgment of latest call")
            return
            
        try:
            # Get latest pending call
            response = self.calls_table.scan(
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': 'pending'}
            )
            
            if response['Items']:
                latest_call = max(response['Items'], key=lambda x: x['timestamp'])
                self.calls_table.update_item(
                    Key={'call_id': latest_call['call_id']},
                    UpdateExpression='SET #status = :status, acknowledged_at = :time',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':status': 'acknowledged',
                        ':time': datetime.now().isoformat()
                    }
                )
                logger.info(f"Acknowledged call: {latest_call['call_id']}")
        except Exception as e:
            logger.error(f"Error acknowledging call: {str(e)}")
    
    def is_main_device(self, device_id: str) -> bool:
        """Check if device is main caregiver device"""
        return 'main' in device_id.lower()
    
    def get_room_from_device(self, device_id: str) -> str:
        """Extract room number from device ID"""
        if 'room1' in device_id.lower():
            return 'room1'
        elif 'room2' in device_id.lower():
            return 'room2'
        elif 'room3' in device_id.lower():
            return 'room3'
        return 'unknown'
    
    def get_main_device_apl(self) -> Dict[str, Any]:
        """APL document for main caregiver device"""
        return {
            "type": "APL",
            "version": "1.6",
            "mainTemplate": {
                "items": [
                    {
                        "type": "Container",
                        "width": "100vw",
                        "height": "100vh",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "backgroundColor": "#2c3e50",
                        "items": [
                            {
                                "type": "Text",
                                "text": "🏥 Care Home Assistant",
                                "fontSize": "40dp",
                                "color": "white",
                                "textAlign": "center"
                            },
                            {
                                "type": "Text",
                                "text": "Main Station - Monitoring All Rooms",
                                "fontSize": "20dp",
                                "color": "#ecf0f1",
                                "textAlign": "center",
                                "paddingTop": "20dp"
                            }
                        ]
                    }
                ]
            }
        }
    
    def get_resident_device_apl(self) -> Dict[str, Any]:
        """APL document for resident device with touch button"""
        return {
            "type": "APL",
            "version": "1.6",
            "mainTemplate": {
                "items": [
                    {
                        "type": "Container",
                        "width": "100vw",
                        "height": "100vh",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "backgroundColor": "#34495e",
                        "items": [
                            {
                                "type": "TouchWrapper",
                                "width": "300dp",
                                "height": "150dp",
                                "onPress": {
                                    "type": "SendEvent",
                                    "arguments": ["touchCall"]
                                },
                                "items": [
                                    {
                                        "type": "Frame",
                                        "backgroundColor": "#e74c3c",
                                        "borderRadius": "20dp",
                                        "width": "100%",
                                        "height": "100%",
                                        "items": [
                                            {
                                                "type": "Text",
                                                "text": "📞 CALL CAREGIVER",
                                                "fontSize": "24dp",
                                                "color": "white",
                                                "fontWeight": "bold",
                                                "textAlign": "center",
                                                "width": "100%",
                                                "height": "100%",
                                                "textAlignVertical": "center"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "Text",
                                "text": "Say 'Help' for emergency or 'Nurse' to send a message",
                                "fontSize": "16dp",
                                "color": "#bdc3c7",
                                "textAlign": "center",
                                "paddingTop": "30dp"
                            }
                        ]
                    }
                ]
            }
        }
    
    def get_calling_apl(self) -> Dict[str, Any]:
        """APL document for calling state"""
        return {
            "type": "APL",
            "version": "1.6",
            "mainTemplate": {
                "items": [
                    {
                        "type": "Container",
                        "width": "100vw",
                        "height": "100vh",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "backgroundColor": "#3498db",
                        "items": [
                            {
                                "type": "Text",
                                "text": "📞 Calling Caregiver...",
                                "fontSize": "32dp",
                                "color": "white",
                                "textAlign": "center"
                            },
                            {
                                "type": "Text",
                                "text": "Help is on the way",
                                "fontSize": "18dp",
                                "color": "#ecf0f1",
                                "textAlign": "center",
                                "paddingTop": "20dp"
                            }
                        ]
                    }
                ]
            }
        }
    
    def get_emergency_apl(self) -> Dict[str, Any]:
        """APL document for emergency state"""
        return {
            "type": "APL",
            "version": "1.6",
            "mainTemplate": {
                "items": [
                    {
                        "type": "Container",
                        "width": "100vw",
                        "height": "100vh",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "backgroundColor": "#e74c3c",
                        "items": [
                            {
                                "type": "Text",
                                "text": "🚨 EMERGENCY",
                                "fontSize": "48dp",
                                "color": "white",
                                "fontWeight": "bold",
                                "textAlign": "center"
                            },
                            {
                                "type": "Text",
                                "text": "Help is Coming",
                                "fontSize": "24dp",
                                "color": "#ecf0f1",
                                "textAlign": "center",
                                "paddingTop": "20dp"
                            }
                        ]
                    }
                ]
            }
        }
    
    def build_response(self, speech_text: str, reprompt: Optional[str] = None, 
                      apl_document: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build Alexa response with optional APL"""
        response = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": speech_text
                },
                "shouldEndSession": False
            }
        }
        
        if reprompt:
            response["response"]["reprompt"] = {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": reprompt
                }
            }
        
        if apl_document:
            response["response"]["directives"] = [
                {
                    "type": "Alexa.Presentation.APL.RenderDocument",
                    "document": apl_document
                }
            ]
        
        return response

# Global handler instance
handler = AlexaCareHandler()

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    return handler.lambda_handler(event, context)

# For local testing
if __name__ == "__main__":
    # Test launch request
    test_event = {
        "request": {"type": "LaunchRequest"},
        "context": {"System": {"device": {"deviceId": "main_device_123"}}}
    }
    
    result = lambda_handler(test_event, None)
    print("Test Result:", json.dumps(result, indent=2))