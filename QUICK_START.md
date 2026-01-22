# ⚡ Quick Start Guide - Echo Show Testing

**Get your Alexa Plus Chatbot running on Echo Show devices in 30 minutes!**

## 🎯 What You'll Need

- **2+ Echo Show devices** (Gen 4+)
- **AWS Account** (free tier works)
- **Amazon Developer Account** (free)
- **Computer** with internet access

---

## 🚀 5-Minute AWS Setup

### 1. Create AWS Resources
```bash
# Install AWS CLI (Windows)
curl "https://awscli.amazonaws.com/AWSCLIV2.msi" -o "AWSCLIV2.msi"
msiexec /i AWSCLIV2.msi

# Configure AWS (enter your credentials)
aws configure

# Create everything at once
aws cloudformation create-stack \
    --stack-name alexa-care-stack \
    --template-body file://aws-setup.yaml \
    --capabilities CAPABILITY_IAM \
    --region us-east-1
```

### 2. Deploy Lambda Function
```bash
# Package and deploy
cd src/lambda
zip -r lambda.zip .
aws lambda create-function \
    --function-name alexa-care-handler \
    --runtime python3.9 \
    --role arn:aws:iam::YOUR_ACCOUNT:role/alexa-care-lambda-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda.zip \
    --region us-east-1
```

---

## 🎤 5-Minute Alexa Skill Setup

### 1. Install ASK CLI
```bash
npm install -g ask-cli
ask configure  # Sign in to Amazon Developer Account
```

### 2. Deploy Skill
```bash
cd src/skill
# Update skill.json with your Lambda ARN
ask deploy
```

---

## 📱 5-Minute Device Setup

### 1. Register Echo Shows
1. **Main Device**: Name it "Main Station"
2. **Room Devices**: Name them "Room 1", "Room 2", etc.
3. **Get Device IDs**: Alexa App → Devices → Settings

### 2. Update Device Mapping
```python
# Edit src/lambda/lambda_function.py
DEVICE_MAP = {
    'YOUR_MAIN_DEVICE_ID': 'Main Station',
    'YOUR_ROOM1_DEVICE_ID': 'Room 1 - Jane',
    # Add your actual device IDs
}
```

### 3. Enable Skill
1. Alexa App → Skills & Games → Your Skills → Dev Skills
2. Enable "Care Home Assistant" on ALL devices

---

## ✅ 5-Minute Testing

### Test 1: Touch Call
**Room Device**: Touch call button
**Main Device**: Should hear "Jane is calling"
**Say**: "OK"

### Test 2: Emergency
**Room Device**: "Alexa, help"
**Main Device**: Should hear "URGENT: Help needed in Room 1"
**Say**: "OK"

### Test 3: Nurse Communication
**Room Device**: "Alexa, nurse I need water"
**Main Device**: Should hear "Jane says: I need water"
**Say**: "OK"

---

## 🔧 Troubleshooting (2 minutes)

### Skill Not Working?
```bash
# Check Lambda logs
aws logs filter-log-events \
    --log-group-name /aws/lambda/alexa-care-handler \
    --start-time $(date -d '10 minutes ago' +%s)000
```

### Device Not Responding?
1. Check device IDs in Lambda code
2. Verify skill enabled on device
3. Test with "Alexa, open care home assistant"

### No Notifications?
1. Verify SNS topic ARN in Lambda environment
2. Check device mapping
3. Test with single device first

---

## 📋 Complete Setup Checklist

**AWS (5 min):**
- [ ] AWS CLI installed and configured
- [ ] Lambda function deployed
- [ ] DynamoDB table created
- [ ] SNS topic created

**Alexa Skill (5 min):**
- [ ] ASK CLI installed
- [ ] Skill deployed
- [ ] Lambda ARN configured

**Devices (5 min):**
- [ ] Echo Shows registered
- [ ] Device IDs collected
- [ ] Device mapping updated
- [ ] Skill enabled on all devices

**Testing (5 min):**
- [ ] Touch call works
- [ ] Emergency help works
- [ ] Nurse communication works
- [ ] Multi-device notifications work

**Total Time: ~20 minutes** ⏱️

---

## 🎯 Next Steps

1. **Add More Rooms**: Update DEVICE_MAP with additional devices
2. **Customize Names**: Change resident names in RESIDENTS dictionary
3. **Add Caregivers**: Update CaregiverNames slot type
4. **Monitor Usage**: Check DynamoDB for call logs
5. **Scale Up**: Deploy to production environment

---

## 📞 Need Help?

- **Full Guide**: See `DEPLOYMENT_GUIDE.md` for detailed instructions
- **Demo**: Open `demo/index.html` for interactive simulation
- **Testing**: Run `python tests/test_local.py` for local tests
- **Requirements**: See `REQUIREMENTS_VERIFICATION.md` for feature coverage

**Ready to help care homes communicate better!** 🏥✨