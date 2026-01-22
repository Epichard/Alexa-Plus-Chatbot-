#!/bin/bash

# Alexa Plus Chatbot - Automated Deployment Script
# This script automates the entire AWS and Alexa skill deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="alexa-care"
AWS_REGION="us-east-1"
LAMBDA_FUNCTION_NAME="${PROJECT_NAME}-handler"
STACK_NAME="${PROJECT_NAME}-stack"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check AWS CLI configuration
check_aws_config() {
    print_status "Checking AWS CLI configuration..."
    
    if ! command_exists aws; then
        print_error "AWS CLI not found. Please install AWS CLI first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS CLI not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "AWS CLI configured successfully"
}

# Function to check ASK CLI configuration
check_ask_config() {
    print_status "Checking ASK CLI configuration..."
    
    if ! command_exists ask; then
        print_warning "ASK CLI not found. Installing..."
        npm install -g ask-cli
    fi
    
    # Check if ASK CLI is configured
    if ! ask api list-skills >/dev/null 2>&1; then
        print_warning "ASK CLI not configured. Please run 'ask configure' to set up your Amazon Developer Account."
        read -p "Press Enter after configuring ASK CLI..."
    fi
    
    print_success "ASK CLI configured successfully"
}

# Function to deploy AWS resources
deploy_aws_resources() {
    print_status "Deploying AWS resources using CloudFormation..."
    
    # Check if stack already exists
    if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION >/dev/null 2>&1; then
        print_warning "Stack $STACK_NAME already exists. Updating..."
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://aws-setup.yaml \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION \
            --parameters ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME
    else
        print_status "Creating new stack..."
        aws cloudformation create-stack \
            --stack-name $STACK_NAME \
            --template-body file://aws-setup.yaml \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION \
            --parameters ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME
    fi
    
    print_status "Waiting for stack deployment to complete..."
    aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $AWS_REGION 2>/dev/null || \
    aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $AWS_REGION
    
    print_success "AWS resources deployed successfully"
}

# Function to get stack outputs
get_stack_outputs() {
    print_status "Retrieving stack outputs..."
    
    LAMBDA_ROLE_ARN=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`LambdaRoleArn`].OutputValue' \
        --output text)
    
    DYNAMODB_TABLE=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`DynamoDBTableName`].OutputValue' \
        --output text)
    
    SNS_TOPIC_ARN=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`SNSTopicArn`].OutputValue' \
        --output text)
    
    print_success "Stack outputs retrieved"
    echo "  Lambda Role ARN: $LAMBDA_ROLE_ARN"
    echo "  DynamoDB Table: $DYNAMODB_TABLE"
    echo "  SNS Topic ARN: $SNS_TOPIC_ARN"
}

# Function to deploy Lambda function
deploy_lambda() {
    print_status "Deploying Lambda function..."
    
    # Navigate to Lambda source directory
    cd src/lambda
    
    # Create deployment package
    print_status "Creating deployment package..."
    zip -r ../../lambda-deployment.zip . -x "*.pyc" "__pycache__/*"
    cd ../..
    
    # Check if Lambda function exists
    if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION >/dev/null 2>&1; then
        print_warning "Lambda function exists. Updating code..."
        aws lambda update-function-code \
            --function-name $LAMBDA_FUNCTION_NAME \
            --zip-file fileb://lambda-deployment.zip \
            --region $AWS_REGION
        
        # Update environment variables
        aws lambda update-function-configuration \
            --function-name $LAMBDA_FUNCTION_NAME \
            --environment Variables="{\"DYNAMODB_TABLE\":\"$DYNAMODB_TABLE\",\"SNS_TOPIC_ARN\":\"$SNS_TOPIC_ARN\",\"AWS_REGION\":\"$AWS_REGION\"}" \
            --region $AWS_REGION
    else
        print_status "Creating new Lambda function..."
        aws lambda create-function \
            --function-name $LAMBDA_FUNCTION_NAME \
            --runtime python3.9 \
            --role $LAMBDA_ROLE_ARN \
            --handler lambda_function.lambda_handler \
            --zip-file fileb://lambda-deployment.zip \
            --timeout 30 \
            --memory-size 256 \
            --environment Variables="{\"DYNAMODB_TABLE\":\"$DYNAMODB_TABLE\",\"SNS_TOPIC_ARN\":\"$SNS_TOPIC_ARN\",\"AWS_REGION\":\"$AWS_REGION\"}" \
            --region $AWS_REGION
        
        # Add Alexa permission
        aws lambda add-permission \
            --function-name $LAMBDA_FUNCTION_NAME \
            --statement-id alexa-skill-trigger \
            --action lambda:InvokeFunction \
            --principal alexa-appkit.amazon.com \
            --region $AWS_REGION
    fi
    
    # Get Lambda ARN
    LAMBDA_ARN=$(aws lambda get-function \
        --function-name $LAMBDA_FUNCTION_NAME \
        --region $AWS_REGION \
        --query 'Configuration.FunctionArn' \
        --output text)
    
    print_success "Lambda function deployed successfully"
    echo "  Lambda ARN: $LAMBDA_ARN"
    
    # Clean up
    rm -f lambda-deployment.zip
}

# Function to deploy Alexa skill
deploy_alexa_skill() {
    print_status "Deploying Alexa skill..."
    
    # Navigate to skill directory
    cd src/skill
    
    # Update skill.json with Lambda ARN
    print_status "Updating skill configuration with Lambda ARN..."
    
    # Create backup of original skill.json
    cp skill.json skill.json.backup
    
    # Update the Lambda ARN in skill.json
    sed -i.tmp "s|YOUR_LAMBDA_ARN|$LAMBDA_ARN|g" skill.json
    rm -f skill.json.tmp
    
    # Deploy skill
    print_status "Deploying skill to Alexa..."
    ask deploy
    
    # Get skill ID
    SKILL_ID=$(ask api list-skills | grep -A 5 "Care Home Assistant" | grep "skillId" | cut -d'"' -f4)
    
    if [ -z "$SKILL_ID" ]; then
        print_error "Failed to get Skill ID. Please check the deployment."
        cd ../..
        return 1
    fi
    
    print_success "Alexa skill deployed successfully"
    echo "  Skill ID: $SKILL_ID"
    
    # Restore original skill.json
    mv skill.json.backup skill.json
    
    cd ../..
}

# Function to display device setup instructions
display_device_setup() {
    print_status "Device Setup Instructions:"
    echo ""
    echo "1. Register your Echo Show devices in the Alexa app"
    echo "2. Name them appropriately:"
    echo "   - Main Device: 'Main Station' or 'Caregiver Device'"
    echo "   - Room Devices: 'Room 1 Device', 'Room 2 Device', etc."
    echo ""
    echo "3. Get device IDs from Alexa app:"
    echo "   - Devices → Echo & Alexa → Select device → Settings → Device Options"
    echo ""
    echo "4. Update device mapping in src/lambda/lambda_function.py:"
    echo "   DEVICE_MAP = {"
    echo "       'YOUR_MAIN_DEVICE_ID': 'Main Station',"
    echo "       'YOUR_ROOM1_DEVICE_ID': 'Room 1 - Jane',"
    echo "       # Add your actual device IDs"
    echo "   }"
    echo ""
    echo "5. Redeploy Lambda function after updating device IDs"
    echo ""
    echo "6. Enable skill on all devices:"
    echo "   - Alexa app → Skills & Games → Your Skills → Dev Skills"
    echo "   - Find 'Care Home Assistant' and enable on all devices"
    echo ""
}

# Function to display testing instructions
display_testing_instructions() {
    print_status "Testing Instructions:"
    echo ""
    echo "Test 1: Touch Call"
    echo "  - Room Device: Touch call button on screen"
    echo "  - Main Device: Should hear 'Jane is calling'"
    echo "  - Say: 'OK'"
    echo ""
    echo "Test 2: Emergency Help"
    echo "  - Room Device: 'Alexa, help'"
    echo "  - Main Device: Should hear 'URGENT: Help needed in Room 1'"
    echo "  - Say: 'OK'"
    echo ""
    echo "Test 3: Nurse Communication"
    echo "  - Room Device: 'Alexa, nurse I need water'"
    echo "  - Main Device: Should hear 'Jane says: I need water'"
    echo "  - Say: 'OK'"
    echo ""
}

# Function to run tests
run_tests() {
    print_status "Running local tests..."
    
    if [ -f "tests/test_local.py" ]; then
        python tests/test_local.py
        print_success "Local tests completed"
    else
        print_warning "Local test file not found. Skipping tests."
    fi
}

# Function to display monitoring setup
display_monitoring() {
    print_status "Monitoring and Troubleshooting:"
    echo ""
    echo "View Lambda logs:"
    echo "  aws logs filter-log-events \\"
    echo "    --log-group-name /aws/lambda/$LAMBDA_FUNCTION_NAME \\"
    echo "    --start-time \$(date -d '1 hour ago' +%s)000 \\"
    echo "    --region $AWS_REGION"
    echo ""
    echo "Check DynamoDB call records:"
    echo "  aws dynamodb scan \\"
    echo "    --table-name $DYNAMODB_TABLE \\"
    echo "    --region $AWS_REGION \\"
    echo "    --max-items 10"
    echo ""
    echo "Test Lambda function directly:"
    echo "  aws lambda invoke \\"
    echo "    --function-name $LAMBDA_FUNCTION_NAME \\"
    echo "    --payload file://test-event.json \\"
    echo "    --region $AWS_REGION \\"
    echo "    response.json"
    echo ""
}

# Main deployment function
main() {
    echo "=================================================="
    echo "  Alexa Plus Chatbot - Automated Deployment"
    echo "=================================================="
    echo ""
    
    # Check prerequisites
    check_aws_config
    check_ask_config
    
    # Deploy AWS resources
    deploy_aws_resources
    get_stack_outputs
    
    # Deploy Lambda function
    deploy_lambda
    
    # Deploy Alexa skill
    deploy_alexa_skill
    
    # Run local tests
    run_tests
    
    echo ""
    echo "=================================================="
    print_success "Deployment completed successfully!"
    echo "=================================================="
    echo ""
    
    # Display next steps
    display_device_setup
    display_testing_instructions
    display_monitoring
    
    echo ""
    print_success "Your Alexa Plus Chatbot is ready for device testing!"
    echo ""
    echo "Next steps:"
    echo "1. Update device IDs in Lambda function"
    echo "2. Enable skill on all Echo Show devices"
    echo "3. Test the three main features"
    echo "4. Monitor logs for any issues"
    echo ""
    echo "For detailed instructions, see:"
    echo "- README.md (complete guide)"
    echo "- QUICK_START.md (quick setup)"
    echo "- DEPLOYMENT_GUIDE.md (detailed deployment)"
    echo ""
}

# Run main function
main "$@"