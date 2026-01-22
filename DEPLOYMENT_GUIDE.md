# 🚀 AWS Deployment Guide - Alexa Plus Chatbot

Complete step-by-step guide for deploying the Alexa Plus Chatbot system to AWS with Echo Show device testing.

## 📋 Prerequisites Checklist

### Required Accounts & Access
- [ ] AWS Account with admin access
- [ ] Amazon Developer Account (for Alexa skills)
- [ ] 2+ Echo Show devices (Gen 4+)
- [ ] AWS CLI installed and configured
- [ ] ASK CLI installed

### Required Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:*",
        "dynamodb:*",
        "sns:*",
        "iam:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## STEP 1: AWS CLI Setup

### 1.1 Install AWS CLI
```bash
# Windows
curl "https://awscli.amazonaws.com/AWSCLIV2.msi" -o "AWSCLIV2.msi"
msiexec /i AWSCLIV2.msi

# Verify installation
aws --version
```

### 1.2 Configure AWS Credentials
```bash
# Configure AWS CLI
aws configure

# Enter your credentials:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json
```

### 1.3 Test AWS Access
```bash
# Test connection
aws sts get-caller-identity

# Should return your account info
```

---

## STEP 2: Create IAM Role for Lambda

### 2.1 Create Trust Policy
```bash
# Create trust-policy.json
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
```

### 2.2 Create IAM Role
```bash
# Create Lambda execution role
aws iam create-role \
    --role-name alexa-care-lambda-role \
    --assume-role-policy-document file://trust-policy.json

# Attach basic Lambda execution policy
aws iam attach-role-policy \
    --role-name alexa-care-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### 2.3 Create Custom Policy for DynamoDB & SNS
```bash
# Create custom-policy.json
cat > custom-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:*:table/alexa-care-calls"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:us-east-1:*:alexa-care-notifications"
    }
  ]
}
EOF

# Create and attach custom policy
aws iam create-policy \
    --policy-name alexa-care-custom-policy \
    --policy-document file://custom-policy.json

aws iam attach-role-policy \
    --role-name alexa-care-lambda-role \
    --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/alexa-care-custom-policy
```

---

## STEP 3: Create DynamoDB Table

### 3.1 Create Call Logging Table
```bash
# Create DynamoDB table for call records
aws dynamodb create-table \
    --table-name alexa-care-calls \
    --attribute-definitions \
        AttributeName=call_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=call_id,KeyType=HASH \
    --global-secondary-indexes \
        IndexName=timestamp-index,KeySchema=[{AttributeName=timestamp,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-1
```

### 3.2 Verify Table Creation
```bash
# Check table status
aws dynamodb describe-table \
    --table-name alexa-care-calls \
    --region us-east-1

# Wait for table to be ACTIVE
aws dynamodb wait table-exists \
    --table-name alexa-care-calls \
    --region us-east-1
```

---

## STEP 4: Create SNS Topic

### 4.1 Create Notification Topic
```bash
# Create SNS topic
aws sns create-topic \
    --name alexa-care-notifications \
    --region us-east-1

# Save the TopicArn from output - you'll need it later
```

### 4.2 Get Topic ARN
```bash
# Get topic ARN for later use
TOPIC_ARN=$(aws sns list-topics --region us-east-1 --query 'Topics[?contains(TopicArn, `alexa-care-notifications`)].TopicArn' --output text)
echo "Topic ARN: $TOPIC_ARN"
```

---

## STEP 5: Deploy Lambda Function

### 5.1 Prepare Lambda Package
```bash
# Navigate to Lambda source
cd src/lambda

# Install dependencies (if any)
pip install -r requirements.txt -t .

# Create deployment package
zip -r ../lambda-deployment.zip .
cd ..
```

### 5.2 Create Lambda Function
```bash
# Get IAM role ARN
ROLE_ARN=$(aws iam get-role --role-name alexa-care-lambda-role --query 'Role.Arn' --output text)

# Create Lambda function
aws lambda create-function \
    --function-name alexa-care-handler \
    --runtime python3.9 \
    --role $ROLE_ARN \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda-deployment.zip \
    --timeout 30 \
    --memory-size 256 \
    --region us-east-1

# Save Lambda ARN for skill configuration
LAMBDA_ARN=$(aws lambda get-function --function-name alexa-care-handler --region us-east-1 --query 'Configuration.FunctionArn' --output text)
echo "Lambda ARN: $LAMBDA_ARN"
```

### 5.3 Configure Environment Variables
```bash
# Set environment variables
aws lambda update-function-configuration \
    --function-name alexa-care-handler \
    --environment Variables="{
        \"DYNAMODB_TABLE\":\"alexa-care-calls\",
        \"SNS_TOPIC_ARN\":\"$TOPIC_ARN\",
        \"AWS_REGION\":\"us-east-1\"
    }" \
    --region us-east-1
```

### 5.4 Add Alexa Trigger Permission
```bash
# Allow Alexa to invoke Lambda
aws lambda add-permission \
    --function-name alexa-care-handler \
    --statement-id alexa-skill-trigger \
    --action lambda:InvokeFunction \
    --principal alexa-appkit.amazon.com \
    --region us-east-1
```

---

## STEP 6: Install ASK CLI

### 6.1 Install Node.js and ASK CLI
```bash
# Install Node.js (if not installed)
# Download from: https://nodejs.org/

# Install ASK CLI
npm install -g ask-cli

# Verify installation
ask --version
```

### 6.2 Configure ASK CLI
```bash
# Initialize ASK CLI
ask configure

# Follow prompts to:
# 1. Sign in to Amazon Developer Account
# 2. Choose AWS profile
# 3. Set default region (us-east-1)
```

---

## STEP 7: Deploy Alexa Skill

### 7.1 Update Skill Configuration
```bash
# Navigate to skill directory
cd src/skill

# Update skill.json with your Lambda ARN
# Replace YOUR_LAMBDA_ARN with actual ARN from Step 5.2
sed -i "s/YOUR_LAMBDA_ARN/$LAMBDA_ARN/g" skill.json
```

### 7.2 Deploy Skill
```bash
# Deploy the skill
ask deploy

# Note the Skill ID from output for testing
SKILL_ID=$(ask api list-skills | grep -A 5 "Care Home Assistant" | grep "skillId" | cut -d'"' -f4)
echo "Skill ID: $SKILL_ID"
```

### 7.3 Enable Skill for Testing
```bash
# Enable skill for development testing
ask api enable-skill \
    --skill-id $SKILL_ID \
    --stage development
```

---

## STEP 8: Configure Echo Show Devices

### 8.1 Get Device IDs

**Method 1: Alexa App**
1. Open Alexa app on phone
2. Devices → Echo & Alexa
3. Select each device
4. Settings → Device Options
5. Copy Device ID

**Method 2: ASK CLI**
```bash
# List registered devices (requires device registration)
ask api get-device-settings \
    --device-id YOUR_DEVICE_ID
```

### 8.2 Update Device Mapping
```python
# Edit src/lambda/lambda_function.py
# Replace with your actual device IDs

DEVICE_MAP = {
    'amzn1.ask.device.ACTUAL_MAIN_DEVICE_ID': 'Main Station',
    'amzn1.ask.device.ACTUAL_ROOM1_DEVICE_ID': 'Room 1 - Jane',
    'amzn1.ask.device.ACTUAL_ROOM2_DEVICE_ID': 'Room 2 - Bob',
    # Add more devices as needed
}
```

### 8.3 Redeploy Lambda with Device IDs
```bash
# Repackage and update Lambda
cd src/lambda
zip -r ../lambda-deployment-updated.zip .
cd ..

aws lambda update-function-code \
    --function-name alexa-care-handler \
    --zip-file fileb://lambda-deployment-updated.zip \
    --region us-east-1
```

---

## STEP 9: Enable Skill on Devices

### 9.1 Enable via Alexa App
1. Open Alexa app
2. Skills & Games → Your Skills → Dev Skills
3. Find "Care Home Assistant"
4. Enable skill
5. Grant permissions:
   - Device address
   - Customer profile
   - Lists read/write

### 9.2 Test Skill Activation
```bash
# Test with ASK CLI simulator
ask dialog --locale en-US --skill-id $SKILL_ID

# Try test utterances:
# "help"
# "nurse I need water"
# "ok"
```

---

## STEP 10: Physical Device Testing

### 10.1 Test Touch Interface
**On Room Device:**
1. Look for call button on screen
2. Touch the button
3. Should hear: "Calling caregiver now"

**On Main Device:**
1. Should hear: "Jane is calling"
2. Say: "OK"
3. Should hear: "Acknowledged"

### 10.2 Test Voice Commands
**Emergency Test:**
```
Resident: "Alexa, help"
Device: "Emergency help is on the way"
Main Device: "URGENT: Help needed in Room 1"
Caregiver: "OK"
Main Device: "Acknowledged"
```

**Nurse Communication Test:**
```
Resident: "Alexa, nurse I need water"
Device: "Hold on, I'm getting help for you"
Main Device: "Jane says: I need water"
Caregiver: "OK"
Main Device: "Acknowledged"
```

### 10.3 Verify Call Logging
```bash
# Check DynamoDB for call records
aws dynamodb scan \
    --table-name alexa-care-calls \
    --region us-east-1 \
    --max-items 10

# Should show call records with timestamps
```

---

## STEP 11: Monitoring & Troubleshooting

### 11.1 Set Up CloudWatch Monitoring
```bash
# Create CloudWatch alarm for Lambda errors
aws cloudwatch put-metric-alarm \
    --alarm-name "AlexaCare-LambdaErrors" \
    --alarm-description "Lambda function errors" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --dimensions Name=FunctionName,Value=alexa-care-handler \
    --region us-east-1
```

### 11.2 View Lambda Logs
```bash
# View recent Lambda logs
aws logs filter-log-events \
    --log-group-name /aws/lambda/alexa-care-handler \
    --start-time $(date -d '1 hour ago' +%s)000 \
    --region us-east-1
```

### 11.3 Test Lambda Function Directly
```bash
# Create test event
cat > test-event.json << EOF
{
  "request": {
    "type": "IntentRequest",
    "intent": {
      "name": "HelpWakeWordIntent"
    }
  },
  "context": {
    "System": {
      "device": {
        "deviceId": "test-device-id"
      }
    }
  }
}
EOF

# Invoke Lambda directly
aws lambda invoke \
    --function-name alexa-care-handler \
    --payload file://test-event.json \
    --region us-east-1 \
    response.json

# Check response
cat response.json
```

---

## 🔧 Common Issues & Solutions

### Issue: "Skill not found"
```bash
# Check skill deployment
ask api get-skill --skill-id $SKILL_ID

# Redeploy if needed
ask deploy --target skill
```

### Issue: "Lambda timeout"
```bash
# Increase timeout
aws lambda update-function-configuration \
    --function-name alexa-care-handler \
    --timeout 60 \
    --region us-east-1
```

### Issue: "DynamoDB access denied"
```bash
# Check IAM permissions
aws iam list-attached-role-policies \
    --role-name alexa-care-lambda-role

# Verify table exists
aws dynamodb describe-table \
    --table-name alexa-care-calls \
    --region us-east-1
```

### Issue: "Device not responding"
```bash
# Check device registration
# Verify skill enabled on device
# Check device ID mapping in Lambda
```

---

## 📊 Deployment Verification Checklist

### AWS Resources
- [ ] IAM role created with correct permissions
- [ ] DynamoDB table active and accessible
- [ ] SNS topic created
- [ ] Lambda function deployed and configured
- [ ] CloudWatch logging enabled

### Alexa Skill
- [ ] Skill deployed successfully
- [ ] Interaction model uploaded
- [ ] Endpoint configured with Lambda ARN
- [ ] Skill enabled for testing
- [ ] Skill enabled on all devices

### Device Configuration
- [ ] All Echo Show devices registered
- [ ] Device IDs collected and mapped
- [ ] Skill enabled on each device
- [ ] Permissions granted

### Functionality Testing
- [ ] Touch call works
- [ ] Emergency help works
- [ ] Nurse communication works
- [ ] Multi-device notifications work
- [ ] Call logging to DynamoDB works
- [ ] "OK" confirmations work

---

## 🚀 Production Readiness

### Security Checklist
- [ ] IAM roles follow least privilege
- [ ] DynamoDB encryption enabled
- [ ] Lambda environment variables secured
- [ ] CloudTrail logging enabled
- [ ] VPC configuration (if required)

### Performance Optimization
- [ ] Lambda memory optimized (256MB recommended)
- [ ] DynamoDB read/write capacity appropriate
- [ ] CloudWatch alarms configured
- [ ] Error handling implemented
- [ ] Retry logic in place

### Skill Certification (Optional)
- [ ] Privacy policy created
- [ ] Terms of use defined
- [ ] Skill testing completed
- [ ] Certification submission (if distributing)

**System is now ready for production use!** 🎉

---

## 📞 Support Resources

- **AWS Documentation**: https://docs.aws.amazon.com/
- **Alexa Skills Kit**: https://developer.amazon.com/alexa/alexa-skills-kit
- **ASK CLI Reference**: https://developer.amazon.com/docs/smapi/ask-cli-intro.html
- **Local Testing**: Run `python tests/test_local.py`
- **Demo Website**: Open `demo/index.html`