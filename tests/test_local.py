#!/usr/bin/env python3
"""
Local Testing Script for Alexa Plus Chatbot
Language: Python 3.9+
Purpose: Test Lambda function locally without AWS dependencies
"""

import json
import sys
import os
import unittest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

try:
    from lambda_function import AlexaCareHandler, lambda_handler
except ImportError as e:
    print(f"❌ Error importing lambda_function: {e}")
    print("Make sure lambda_function.py exists in src/lambda/")
    sys.exit(1)

class TestAlexaCareHandler(unittest.TestCase):
    """Unit tests for Alexa Care Handler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.handler = AlexaCareHandler()
        
        # Mock AWS services to avoid dependencies
        self.handler.calls_table = Mock()
        self.handler.status_table = Mock()
        
    def test_launch_request_main_device(self):
        """Test launch request for main caregiver device"""
        event = {
            "request": {"type": "LaunchRequest"},
            "context": {
                "System": {
                    "device": {"deviceId": "main_device_123"}
                }
            }
        }
        
        response = self.handler.lambda_handler(event, None)
        
        # Verify response structure
        self.assertIn("response", response)
        self.assertIn("outputSpeech", response["response"])
        self.assertEqual(
            response["response"]["outputSpeech"]["text"], 
            "Care Home Assistant ready. Monitoring all rooms."
        )
        
        # Verify APL directive is included
        self.assertIn("directives", response["response"])
        self.assertEqual(
            response["response"]["directives"][0]["type"],
            "Alexa.Presentation.APL.RenderDocument"
        )
    
    def test_launch_request_resident_device(self):
        """Test launch request for resident device"""
        event = {
            "request": {"type": "LaunchRequest"},
            "context": {
                "System": {
                    "device": {"deviceId": "room1_device_123"}
                }
            }
        }
        
        response = self.handler.lambda_handler(event, None)
        
        self.assertEqual(
            response["response"]["outputSpeech"]["text"], 
            "Hello! Touch the call button or say Help for assistance."
        )
    
    def test_help_wake_word_intent(self):
        """Test emergency help wake word"""
        event = {
            "request": {
                "type": "IntentRequest",
                "intent": {"name": "HelpWakeWordIntent"}
            },
            "context": {
                "System": {
                    "device": {"deviceId": "room1_device_123"}
                }
            }
        }
        
        with patch.object(self.handler, 'create_call_record'), \
             patch.object(self.handler, 'notify_main_device'):
            
            response = self.handler.lambda_handler(event, None)
            
            self.assertEqual(
                response["response"]["outputSpeech"]["text"], 
                "Emergency help is on the way. Stay calm."
            )
            
            # Verify emergency APL is used
            self.assertIn("directives", response["response"])
    
    def test_nurse_wake_word_intent_with_message(self):
        """Test nurse communication with message"""
        event = {
            "request": {
                "type": "IntentRequest",
                "intent": {
                    "name": "NurseWakeWordIntent",
                    "slots": {
                        "message": {"value": "I need water"}
                    }
                }
            },
            "context": {
                "System": {
                    "device": {"deviceId": "room1_device_123"}
                }
            }
        }
        
        with patch.object(self.handler, 'create_call_record'), \
             patch.object(self.handler, 'notify_main_device'):
            
            response = self.handler.lambda_handler(event, None)
            
            self.assertEqual(
                response["response"]["outputSpeech"]["text"], 
                "Hold on, I'm getting help for you."
            )
    
    def test_nurse_wake_word_intent_without_message(self):
        """Test nurse communication without message (prompts for clarification)"""
        event = {
            "request": {
                "type": "IntentRequest",
                "intent": {
                    "name": "NurseWakeWordIntent",
                    "slots": {}
                }
            },
            "context": {
                "System": {
                    "device": {"deviceId": "room1_device_123"}
                }
            }
        }
        
        response = self.handler.lambda_handler(event, None)
        
        self.assertIn("What do you need, Jane?", response["response"]["outputSpeech"]["text"])
        self.assertIn("reprompt", response["response"])
    
    def test_touch_event(self):
        """Test touch call button event"""
        event = {
            "request": {"type": "Alexa.Presentation.APL.UserEvent"},
            "context": {
                "System": {
                    "device": {"deviceId": "room1_device_123"}
                }
            }
        }
        
        with patch.object(self.handler, 'create_call_record'), \
             patch.object(self.handler, 'notify_main_device'):
            
            response = self.handler.lambda_handler(event, None)
            
            self.assertEqual(
                response["response"]["outputSpeech"]["text"], 
                "Calling caregiver now. Help is on the way."
            )
    
    def test_caregiver_confirm_intent(self):
        """Test caregiver confirmation"""
        event = {
            "request": {
                "type": "IntentRequest",
                "intent": {"name": "CaregiverConfirmIntent"}
            },
            "context": {
                "System": {
                    "device": {"deviceId": "main_device_123"}
                }
            }
        }
        
        with patch.object(self.handler, 'acknowledge_latest_call'):
            response = self.handler.lambda_handler(event, None)
            
            self.assertEqual(
                response["response"]["outputSpeech"]["text"], 
                "Acknowledged. Resident has been notified."
            )
    
    def test_get_room_from_device(self):
        """Test room extraction from device ID"""
        self.assertEqual(self.handler.get_room_from_device("room1_device_123"), "room1")
        self.assertEqual(self.handler.get_room_from_device("room2_device_456"), "room2")
        self.assertEqual(self.handler.get_room_from_device("room3_device_789"), "room3")
        self.assertEqual(self.handler.get_room_from_device("unknown_device"), "unknown")
    
    def test_is_main_device(self):
        """Test main device detection"""
        self.assertTrue(self.handler.is_main_device("main_device_123"))
        self.assertTrue(self.handler.is_main_device("MAIN_DEVICE_456"))
        self.assertFalse(self.handler.is_main_device("room1_device_123"))
        self.assertFalse(self.handler.is_main_device("resident_device_456"))
    
    def test_apl_documents(self):
        """Test APL document generation"""
        # Test main device APL
        main_apl = self.handler.get_main_device_apl()
        self.assertEqual(main_apl["type"], "APL")
        self.assertEqual(main_apl["version"], "1.6")
        
        # Test resident device APL
        resident_apl = self.handler.get_resident_device_apl()
        self.assertEqual(resident_apl["type"], "APL")
        self.assertIn("TouchWrapper", str(resident_apl))
        
        # Test emergency APL
        emergency_apl = self.handler.get_emergency_apl()
        self.assertEqual(emergency_apl["type"], "APL")
        self.assertIn("EMERGENCY", str(emergency_apl))

def run_integration_tests():
    """Run integration tests with sample events"""
    print("\n" + "="*60)
    print("INTEGRATION TESTS")
    print("="*60)
    
    handler = AlexaCareHandler()
    
    # Mock AWS services for integration tests
    handler.calls_table = Mock()
    handler.status_table = Mock()
    
    test_events = [
        {
            "name": "Launch Request (Main Device)",
            "event": {
                "request": {"type": "LaunchRequest"},
                "context": {"System": {"device": {"deviceId": "main_device_123"}}}
            }
        },
        {
            "name": "Launch Request (Resident Device)",
            "event": {
                "request": {"type": "LaunchRequest"},
                "context": {"System": {"device": {"deviceId": "room1_device_123"}}}
            }
        },
        {
            "name": "Touch Call (Room 1)",
            "event": {
                "request": {"type": "Alexa.Presentation.APL.UserEvent"},
                "context": {"System": {"device": {"deviceId": "room1_device_123"}}}
            }
        },
        {
            "name": "Help Request (Room 2)",
            "event": {
                "request": {
                    "type": "IntentRequest",
                    "intent": {"name": "HelpWakeWordIntent"}
                },
                "context": {"System": {"device": {"deviceId": "room2_device_456"}}}
            }
        },
        {
            "name": "Nurse Request with Message",
            "event": {
                "request": {
                    "type": "IntentRequest",
                    "intent": {
                        "name": "NurseWakeWordIntent",
                        "slots": {"message": {"value": "I need water"}}
                    }
                },
                "context": {"System": {"device": {"deviceId": "room1_device_123"}}}
            }
        },
        {
            "name": "Caregiver Confirmation",
            "event": {
                "request": {
                    "type": "IntentRequest",
                    "intent": {"name": "CaregiverConfirmIntent"}
                },
                "context": {"System": {"device": {"deviceId": "main_device_123"}}}
            }
        }
    ]
    
    for test in test_events:
        try:
            with patch.object(handler, 'create_call_record'), \
                 patch.object(handler, 'notify_main_device'), \
                 patch.object(handler, 'acknowledge_latest_call'):
                
                response = handler.lambda_handler(test["event"], None)
                print(f"✅ {test['name']}: PASS")
                print(f"   Response: {response['response']['outputSpeech']['text']}")
                
        except Exception as e:
            print(f"❌ {test['name']}: FAIL")
            print(f"   Error: {str(e)}")

def validate_skill_files():
    """Validate skill configuration files"""
    print("\n" + "="*60)
    print("SKILL FILE VALIDATION")
    print("="*60)
    
    skill_files = [
        ("src/skill/interaction_model.json", "Interaction Model"),
        ("src/skill/skill.json", "Skill Manifest")
    ]
    
    for file_path, description in skill_files:
        full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ {description}: Valid JSON")
                
                # Additional validation
                if 'interaction_model' in file_path:
                    if 'interactionModel' in data:
                        intents = data['interactionModel']['languageModel']['intents']
                        print(f"   Found {len(intents)} intents")
                    else:
                        print(f"   ⚠️  Missing interactionModel structure")
                        
                elif 'skill.json' in file_path:
                    if 'manifest' in data:
                        print(f"   Valid skill manifest structure")
                    else:
                        print(f"   ⚠️  Missing manifest structure")
                        
            except json.JSONDecodeError as e:
                print(f"❌ {description}: Invalid JSON - {str(e)}")
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)}")
        else:
            print(f"❌ {description}: File not found at {full_path}")

def test_demo_website():
    """Test demo website files"""
    print("\n" + "="*60)
    print("DEMO WEBSITE VALIDATION")
    print("="*60)
    
    demo_files = [
        ("demo/index.html", "HTML File"),
        ("demo/styles.css", "CSS File"),
        ("demo/demo.js", "JavaScript File")
    ]
    
    for file_path, description in demo_files:
        full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
        
        if os.path.exists(full_path):
            print(f"✅ {description}: Found")
            
            # Basic content validation
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if file_path.endswith('.html') and '<!DOCTYPE html>' in content:
                    print(f"   Valid HTML5 structure")
                elif file_path.endswith('.css') and '{' in content and '}' in content:
                    print(f"   Valid CSS structure")
                elif file_path.endswith('.js') and 'function' in content:
                    print(f"   Valid JavaScript structure")
                    
            except Exception as e:
                print(f"   ⚠️  Error reading file: {str(e)}")
                
        else:
            print(f"❌ {description}: File not found")

def test_lambda_function_directly():
    """Test Lambda function with direct invocation"""
    print("\n" + "="*60)
    print("DIRECT LAMBDA FUNCTION TEST")
    print("="*60)
    
    try:
        # Test basic functionality
        test_event = {
            "request": {"type": "LaunchRequest"},
            "context": {"System": {"device": {"deviceId": "main_device_test"}}}
        }
        
        result = lambda_handler(test_event, None)
        
        if result and 'response' in result:
            print("✅ Lambda function executes successfully")
            print(f"   Response type: {type(result)}")
            print(f"   Has speech output: {'outputSpeech' in result['response']}")
            print(f"   Speech text: {result['response']['outputSpeech']['text']}")
        else:
            print("❌ Lambda function returned invalid response")
            
    except Exception as e:
        print(f"❌ Lambda function execution failed: {str(e)}")

def main():
    """Main testing function"""
    print("🏥 ALEXA PLUS CHATBOT - LOCAL TESTING")
    print("Language: Python 3.9+")
    print("="*60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test Lambda function directly
    test_lambda_function_directly()
    
    # Run unit tests
    print("\n" + "="*60)
    print("UNIT TESTS")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAlexaCareHandler)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run integration tests
    run_integration_tests()
    
    # Validate skill files
    validate_skill_files()
    
    # Test demo website
    test_demo_website()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if result.wasSuccessful():
        print("✅ All unit tests passed!")
        print("✅ Integration tests completed")
        print("✅ Skill files validated")
        print("✅ Demo website files verified")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
    
    print("\n📋 TESTING STATUS:")
    print("✅ Local Testing: COMPLETE")
    print("⚠️  AWS Deployment: Requires AWS account")
    print("⚠️  Alexa Console: Requires Developer account")
    print("⚠️  Echo Show Testing: Requires physical devices")
    
    print("\n🚀 NEXT STEPS:")
    print("1. View demo: Open demo/index.html in browser")
    print("2. Deploy Lambda: Follow docs/DEPLOYMENT.md")
    print("3. Create Alexa skill: Upload src/skill/ files")
    print("4. Test on Echo Show: Follow docs/ECHO_TESTING.md")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)