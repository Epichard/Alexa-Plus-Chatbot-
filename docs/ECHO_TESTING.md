# 📱 Amazon Echo Device Testing Guide

## 🎯 Overview

This guide provides step-by-step instructions for testing the Alexa Plus Chatbot on actual Amazon Echo Show devices.

**Language Used:** Python 3.9+ (Backend), JavaScript (Demo)

**Testing Status:** ⚠️ Requires Physical Echo Show Devices

## 📋 Prerequisites

### Required Hardware
- [ ] **Amazon Echo Show Gen 4 or newer** (minimum 2 devices)
- [ ] **Stable Wi-Fi connection**
- [ ] **Same Amazon account** on all devices

### Required Accounts
- [ ] **Amazon Developer Account** (free)
- [ ] **AWS Account** with Lambda access
- [ ] **Amazon account** with Echo devices registered

### Required Software
- [ ] **Python 3.9+** installed locally
- [ ] **AWS CLI** configured
- [ ] **ASK CLI** (optional but recommended)

## 🚀 Step-by-Step Testing Process

### Phase 1: Local Verification (✅ Working)

**1. Test Demo Website**
```bash
cd demo
python -m http.server 8080
# Open: http://localhost:8080
```

**Expected Result:**
- ✅ Website loads with interactive interface
- ✅ Touch call buttons work
- ✅ Emergency simulation works
- ✅ Activity log updates

**2. Run Python Tests**
```bash
python tests/test_local.py
```

**Expected Output:**
```
🏥 ALEXA PLUS CHATBOT - LOCAL TESTING
============================================================
UNIT TESTS
test_launch_request_main_device ... ok
test_help_wake_word_intent ... ok
test_nurse_wake_word_intent ... ok
test_touch_event ... ok

✅ All tests passed!
```

### Phase 2: AWS Lambda Deployment (⚠️ Requires AWS Account)

**1. Package Lambda Function**
```bash
cd src/lambda
zip -r lambda.zip lambda_function.py
```

**2. Deploy to AWS**
```bash
aws lambda create-function \
  --function-name AlexaCareAssistant \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda.zip
```

**3. Test Lambda Function**
```bash
aws lambda invoke \
  --function-name AlexaCareAssistant \
  --payload '{"request":{"type":"LaunchRequest"}}' \
  response.json
```

**Expected Result:**
- ✅ Lambda function deploys successfully
- ✅ Function responds to test invocation
- ✅ No errors in CloudWatch logs

### Phase 3: Alexa Skill Creation (⚠️ Requires Developer Account)

**1. Access Developer Console**
- URL: https://developer.amazon.com/alexa/console/ask
- Login with Amazon Developer account
- Click "Create Skill"

**2. Create Skill**
- **Skill Name:** Care Assistant
- **Primary Locale:** English (US)
- **Model:** Custom
- **Hosting:** Provision your own
- Click "Create Skill"

**3. Upload Interaction Model**
```bash
# Copy contents of src/skill/interaction_model.json
# Paste into JSON Editor in Developer Console
# Click "Save Model" → "Build Model"
```

**4. Configure Endpoint**
- Go to "Endpoint" section
- Select "AWS Lambda ARN"
- Enter: `arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:AlexaCareAssistant`
- Click "Save Endpoints"

**Expected Result:**
- ✅ Skill builds without errors
- ✅ Endpoint connects to Lambda
- ✅ Model validation passes

### Phase 4: Alexa Console Testing (✅ Can Test Without Devices)

**1. Enable Testing**
- Go to "Test" tab
- Set stage to "Development"

**2. Test Commands**
```
Test 1: "Alexa, open care assistant"
Expected: "Hello! Touch the call button or say Help for assistance."

Test 2: "Help"
Expected: "Emergency help is on the way. Stay calm."

Test 3: "Nurse, I need water"
Expected: "Hold on, I'm getting help for you."

Test 4: "OK"
Expected: "Acknowledged. Resident has been notified."
```

**3. Verify APL Templates**
- Check "Display" section in test results
- Verify visual elements render correctly

**Expected Result:**
- ✅ All voice commands respond correctly
- ✅ APL templates display properly
- ✅ No errors in test console

### Phase 5: Echo Show Device Testing (⚠️ Requires Physical Devices)

**1. Enable Skill on Devices**
- Open Alexa app on phone
- Go to "More" → "Skills & Games"
- Search "Care Assistant"
- Click "Enable to Use"
- Select your Echo Show devices

**2. Get Device IDs**
```bash
# Method 1: Alexa App
# Settings → Device Settings → [Device Name] → About

# Method 2: Developer Console
# Go to your skill → Test → Device Log
```

**3. Update Lambda Environment Variables**
```bash
aws lambda update-function-configuration \
  --function-name AlexaCareAssistant \
  --environment Variables="{
    MAIN_DEVICE_ID=amzn1.ask.device.ACTUAL_MAIN_ID,
    ROOM1_DEVICE_ID=amzn1.ask.device.ACTUAL_ROOM1_ID,
    ROOM2_DEVICE_ID=amzn1.ask.device.ACTUAL_ROOM2_ID
  }"
```

**4. Test Touch Interface**
```bash
# On resident Echo Show:
"Alexa, open care assistant"
[Touch the red "CALL CAREGIVER" button]

# Expected on main Echo Show:
"Jane is calling" (or similar announcement)
```

**5. Test Voice Commands**
```bash
# Emergency Test
Resident Device: "Alexa, open care assistant"
Resident Device: "Help"
# Expected: Main device announces emergency

# Nurse Communication Test
Resident Device: "Alexa, open care assistant"
Resident Device: "Nurse, I need water"
# Expected: Main device relays message

# Confirmation Test
Main Device: "OK"
# Expected: Acknowledgment response
```

**Expected Results:**
- ✅ Skill opens on Echo Show
- ✅ Touch interface displays correctly
- ✅ Touch button triggers notifications
- ✅ Voice commands work reliably
- ✅ Multi-device messaging functions
- ✅ Emergency escalation works

## 🔍 Verification Checklist

### Local Testing (✅ Verified Working)
- [x] Demo website loads at http://localhost:8080
- [x] Interactive buttons work
- [x] Python unit tests pass
- [x] Lambda function code validates
- [x] Skill JSON files are valid

### AWS Testing (⚠️ Requires AWS Account)
- [ ] Lambda function deploys successfully
- [ ] DynamoDB tables created
- [ ] SNS topic configured
- [ ] IAM permissions set correctly
- [ ] Environment variables configured

### Alexa Console Testing (⚠️ Requires Developer Account)
- [ ] Skill builds without errors
- [ ] All intents respond in simulator
- [ ] APL templates render correctly
- [ ] Voice recognition works accurately
- [ ] Endpoint connects to Lambda

### Echo Show Testing (⚠️ Requires Physical Devices)
- [ ] Skill enables on devices
- [ ] Touch interface displays
- [ ] Touch buttons trigger calls
- [ ] Voice wake words work
- [ ] Multi-device messaging works
- [ ] Emergency alerts function
- [ ] Caregiver confirmations work

## 🚨 Known Testing Limitations

### What's Currently Working ✅
- **Local Demo:** Fully functional simulation
- **Python Code:** All unit tests pass
- **Skill Configuration:** Valid JSON, ready for upload
- **Lambda Function:** Syntactically correct, ready for deployment

### What Requires Physical Testing ⚠️
- **Touch Interface:** Needs actual Echo Show devices
- **Multi-device Messaging:** Requires 2+ Echo Shows
- **Voice Recognition:** Needs real Alexa testing
- **APL Rendering:** Must verify on actual screens

### What Needs AWS Resources 💰
- **Lambda Deployment:** Requires AWS account
- **DynamoDB Tables:** Requires AWS resources
- **SNS Notifications:** Requires AWS configuration

## 🛠️ Troubleshooting Guide

### Issue: Skill Won't Open on Echo Show
**Possible Causes:**
- Skill not enabled in Development stage
- Device not linked to correct Amazon account
- Skill name pronunciation issues

**Solutions:**
```bash
# Check skill status
ask api get-skill-status -s YOUR_SKILL_ID

# Verify device registration
# Alexa app → Devices → Echo & Alexa → [Your Device]
```

### Issue: Touch Interface Not Working
**Possible Causes:**
- APL not supported on device
- Incorrect APL document syntax
- Device ID mismatch

**Solutions:**
```bash
# Verify APL support
# Echo Show Gen 4+ required

# Check APL document
# Test in Developer Console first
```

### Issue: Multi-Device Messaging Fails
**Possible Causes:**
- Incorrect device IDs
- Lambda environment variables not set
- SNS permissions missing

**Solutions:**
```bash
# Get correct device IDs
aws alexa-for-business list-devices

# Update Lambda environment
aws lambda update-function-configuration --function-name AlexaCareAssistant
```

## 📊 Testing Results Template

### Test Environment
- **Date:** [Date of testing]
- **Devices:** [List of Echo Show devices used]
- **AWS Region:** [us-east-1, etc.]
- **Skill ID:** [Your skill ID]

### Test Results
```
✅ Local Demo: PASS
✅ Python Tests: PASS
⚠️  AWS Deployment: REQUIRES AWS ACCOUNT
⚠️  Alexa Console: REQUIRES DEVELOPER ACCOUNT
⚠️  Echo Show Testing: REQUIRES PHYSICAL DEVICES

Overall Status: READY FOR DEPLOYMENT
```

### Performance Metrics
- **Response Time:** < 2 seconds (target)
- **Voice Recognition:** > 95% accuracy (target)
- **Touch Response:** Immediate (target)
- **Multi-device Latency:** < 1 second (target)

## 🎯 Next Steps

### For Complete Testing
1. **Set up AWS account** and deploy Lambda function
2. **Create Alexa Developer account** and upload skill
3. **Acquire Echo Show devices** (Gen 4+) for physical testing
4. **Configure device IDs** in Lambda environment
5. **Test all functionality** end-to-end

### For Demo Purposes
1. **Use local demo website** at http://localhost:8080
2. **Show Python test results** from `python tests/test_local.py`
3. **Demonstrate code quality** and architecture
4. **Explain deployment process** using documentation

## 📞 Support

**Issues:** Create GitHub issue with testing results
**Documentation:** See [docs/](../docs/) folder
**Demo:** http://localhost:8080

---

**Testing Status:** ✅ Local Testing Complete | ⚠️ Device Testing Requires Hardware

**Last Updated:** December 2024