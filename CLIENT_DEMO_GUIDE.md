# 🏥 Alexa Plus Chatbot - Client Demo & Testing Guide

**AI-Powered Care Home Call Bell & Intercom System**

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Quick Start - Local Demo](#quick-start---local-demo)
3. [Testing the System](#testing-the-system)
4. [Feature Demonstrations](#feature-demonstrations)
5. [Web Dashboard Guide](#web-dashboard-guide)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)

---

## 🎯 System Overview

### What This System Does

The Alexa Plus Chatbot is a comprehensive care home management system that provides:

✅ **Voice-Activated Call Bell** - Residents can call for help using voice or touch  
✅ **Emergency Response** - Urgent "Help" requests are prioritized  
✅ **Two-Way Communication** - Residents can send messages to caregivers  
✅ **Real-Time Dashboard** - Web interface for monitoring all calls and residents  
✅ **Multi-Device Support** - Up to 10 resident rooms + 1 main caregiver station

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    CARE HOME SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🏠 Resident Rooms (Echo Show Devices)                     │
│     • Touch screen call button                             │
│     • Voice commands: "Help", "Nurse"                      │
│     • Visual feedback on screen                            │
│                                                             │
│  🏥 Main Caregiver Station (Echo Show Device)              │
│     • Receives all call notifications                      │
│     • Voice confirmation: "OK"                             │
│     • Real-time status display                             │
│                                                             │
│  💻 Web Dashboard (Browser-Based)                          │
│     • Real-time call monitoring                            │
│     • Resident management                                  │
│     • System analytics                                     │
│     • Multi-user access                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start - Local Demo

### Prerequisites

Before starting, ensure you have:

- ✅ **Python 3.11+** installed ([Download](https://www.python.org/downloads/))
- ✅ **Node.js 18+** installed ([Download](https://nodejs.org/))
- ✅ **Git** installed ([Download](https://git-scm.com/))
- ✅ **Web browser** (Chrome, Firefox, or Edge)

### Step 1: Clone the Repository

```bash
# Open terminal/command prompt and run:
git clone https://github.com/pallavanand305/Alexa-Plus-Chatbot-.git
cd Alexa-Plus-Chatbot-
```

### Step 2: Install Python Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

### Step 3: Start the Backend Server

```bash
# Navigate to FastAPI directory
cd src/fastapi

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Backend is now running!** Keep this terminal open.

### Step 4: Start the Dashboard (New Terminal)

Open a **NEW terminal window** and run:

```bash
# Navigate to dashboard directory
cd src/dashboard

# Install Node.js dependencies (first time only)
npm install

# Start the dashboard
npm run dev
```

**Expected output:**
```
  VITE v4.5.0  ready in 1234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.1.100:3000/
```

✅ **Dashboard is now running!** Keep this terminal open.

### Step 5: Open the Dashboard

1. Open your web browser
2. Go to: **http://localhost:3000**
3. You should see the login page

---

## 🧪 Testing the System

### Test 1: Dashboard Login

**Steps:**
1. Open browser to `http://localhost:3000`
2. Enter credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
3. Click "Login"

**Expected Result:**
✅ You should see the main dashboard with:
- Real-time call monitoring panel
- Resident list
- System status indicators
- Navigation menu

**Screenshot Location:** Dashboard shows "Welcome to Care Home Dashboard"

---

### Test 2: API Health Check

**Steps:**
1. Open browser to `http://localhost:8000/health`

**Expected Result:**
```json
{
  "status": "healthy",
  "service": "alexa-plus-chatbot-api",
  "version": "1.0.0"
}
```

✅ Backend is working correctly!

---

### Test 3: Interactive API Documentation

**Steps:**
1. Open browser to `http://localhost:8000/docs`
2. You'll see the FastAPI Swagger UI

**What You Can Do:**
- View all available API endpoints
- Test endpoints directly from the browser
- See request/response examples

**Try This:**
1. Click on `GET /health`
2. Click "Try it out"
3. Click "Execute"
4. See the response below

---

### Test 4: Real-Time WebSocket Connection

**Steps:**
1. Open the dashboard at `http://localhost:3000`
2. Login with admin credentials
3. Look at the top-right corner

**Expected Result:**
✅ You should see a green indicator showing "Connected" or "WebSocket Active"

This means the real-time updates are working!

---

## 🎬 Feature Demonstrations

### Demo 1: Touch Call Simulation

**Scenario:** Resident touches the call button on their Echo Show

**How to Simulate:**
1. Open the demo page: `demo/index.html` in your browser
2. Click the "Touch Call" button
3. Watch the dashboard update in real-time

**What Happens:**
1. ✅ Call appears on dashboard immediately
2. ✅ Caregiver receives notification
3. ✅ Call status shows "Pending"
4. ✅ Timestamp is recorded

---

### Demo 2: Emergency Help Request

**Scenario:** Resident says "Help" for emergency

**How to Simulate:**
1. Open demo page: `demo/index.html`
2. Click "Emergency Help" button
3. Watch the dashboard

**What Happens:**
1. ✅ Emergency call appears in RED
2. ✅ Marked as "URGENT"
3. ✅ Notification sent to main device
4. ✅ Response time tracking starts

---

### Demo 3: Nurse Communication

**Scenario:** Resident says "Nurse, I need water"

**How to Simulate:**
1. Open demo page: `demo/index.html`
2. Type message: "I need water"
3. Click "Send to Nurse"
4. Watch the dashboard

**What Happens:**
1. ✅ Message appears on dashboard
2. ✅ Caregiver sees full message
3. ✅ Status shows "Pending Response"
4. ✅ Message is logged in history

---

### Demo 4: Caregiver Acknowledgment

**Scenario:** Caregiver says "OK" to acknowledge call

**How to Simulate:**
1. Find a pending call on the dashboard
2. Click "Acknowledge" button
3. Watch the status change

**What Happens:**
1. ✅ Call status changes to "Acknowledged"
2. ✅ Response time is calculated
3. ✅ Resident is notified
4. ✅ Call moves to history

---

## 💻 Web Dashboard Guide

### Dashboard Features

#### 1. **Real-Time Call Monitoring**

**Location:** Main dashboard page

**What You See:**
- Live call feed (updates automatically)
- Call type (Touch, Emergency, Nurse Request)
- Resident name and room number
- Timestamp
- Current status
- Action buttons

**Actions You Can Take:**
- ✅ Acknowledge calls
- ✅ Resolve calls
- ✅ View call details
- ✅ Filter by status/type

---

#### 2. **Resident Management**

**Location:** Click "Residents" in navigation

**What You Can Do:**
- ✅ View all residents
- ✅ Add new residents
- ✅ Edit resident information
- ✅ Assign room numbers
- ✅ Manage device IDs
- ✅ Add emergency contacts

**How to Add a Resident:**
1. Click "Add Resident" button
2. Fill in the form:
   - First Name: `Jane`
   - Last Name: `Smith`
   - Room Number: `101`
   - Device ID: `room1_device_123`
3. Click "Save"
4. Resident appears in the list

---

#### 3. **System Status**

**Location:** Click "System" in navigation

**What You See:**
- Component health status
- Performance metrics
- Active alerts
- System uptime
- Connection status

**Health Indicators:**
- 🟢 **Green** = Healthy
- 🟡 **Yellow** = Degraded
- 🔴 **Red** = Down

---

#### 4. **Analytics Dashboard**

**Location:** Main dashboard page (bottom section)

**Metrics Displayed:**
- Total calls today
- Average response time
- Call type breakdown
- Busiest rooms
- Peak hours

**Charts:**
- Call volume over time
- Response time trends
- Call type distribution

---

## 🔍 Troubleshooting

### Issue 1: Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Try starting again
cd src/fastapi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Issue 2: Dashboard Won't Load

**Error:** `Cannot GET /`

**Solution:**
```bash
# Make sure you're in the right directory
cd src/dashboard

# Reinstall node modules
rm -rf node_modules
npm install

# Start again
npm run dev
```

---

### Issue 3: Dashboard Can't Connect to Backend

**Error:** "Connection failed" or "API Error"

**Solution:**
1. Check backend is running: `http://localhost:8000/health`
2. Check CORS settings in `src/fastapi/app/core/config.py`
3. Restart both backend and dashboard

---

### Issue 4: WebSocket Not Connecting

**Symptom:** Dashboard shows "Disconnected" or no real-time updates

**Solution:**
1. Check browser console for errors (F12)
2. Verify WebSocket endpoint: `ws://localhost:8000/ws/live-updates`
3. Restart backend server
4. Refresh dashboard page

---

### Issue 5: Port Already in Use

**Error:** `Address already in use: 8000`

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

---

## 🎥 Live Demo Script

### For Client Presentation (10 minutes)

**Minute 1-2: Introduction**
- "This is the Alexa Plus Chatbot system for care homes"
- "It provides voice-activated call bell and real-time monitoring"
- "Let me show you how it works"

**Minute 3-4: Dashboard Overview**
- Open `http://localhost:3000`
- Login with admin credentials
- "This is the main dashboard where caregivers monitor all rooms"
- Point out: call feed, resident list, system status

**Minute 5-6: Touch Call Demo**
- Open `demo/index.html`
- Click "Touch Call" button
- "Watch the dashboard - the call appears instantly"
- Show acknowledgment process

**Minute 7-8: Emergency Demo**
- Click "Emergency Help" button
- "Notice how emergency calls are highlighted in red"
- "Response time is tracked automatically"

**Minute 9: Resident Management**
- Navigate to Residents page
- "Caregivers can manage resident information here"
- Show add/edit functionality

**Minute 10: Q&A**
- "Any questions about the system?"
- Show API documentation if technical questions

---

## 📊 Testing Checklist

Use this checklist during client demos:

### Backend Tests
- [ ] Backend starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] API documentation loads at `/docs`
- [ ] All endpoints respond correctly

### Dashboard Tests
- [ ] Dashboard loads successfully
- [ ] Login works with test credentials
- [ ] Navigation menu works
- [ ] All pages load without errors

### Real-Time Features
- [ ] WebSocket connects successfully
- [ ] Call updates appear in real-time
- [ ] Status changes reflect immediately
- [ ] No lag or delays

### Functionality Tests
- [ ] Can create new calls
- [ ] Can acknowledge calls
- [ ] Can resolve calls
- [ ] Can add/edit residents
- [ ] Can view system status

### Performance Tests
- [ ] Dashboard loads in < 3 seconds
- [ ] API responses in < 500ms
- [ ] WebSocket latency < 100ms
- [ ] No memory leaks after 1 hour

---

## 🚀 Production Deployment

### For AWS Deployment

**Prerequisites:**
- AWS Account
- AWS CLI configured
- Domain name (optional)

**Deployment Steps:**

1. **Deploy Lambda Function**
```bash
cd src/lambda
zip -r lambda-deployment.zip .
aws lambda update-function-code \
    --function-name alexa-care-handler \
    --zip-file fileb://lambda-deployment.zip
```

2. **Deploy FastAPI Backend**
```bash
# Build Docker image
docker build -t alexa-care-fastapi src/fastapi/

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag alexa-care-fastapi:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/alexa-care-fastapi:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/alexa-care-fastapi:latest
```

3. **Deploy Dashboard**
```bash
cd src/dashboard
npm run build
aws s3 sync dist/ s3://your-dashboard-bucket/
```

4. **Configure Alexa Skill**
- Go to Alexa Developer Console
- Upload `src/skill/interaction_model.json`
- Configure endpoint to Lambda ARN
- Test with Echo Show devices

---

## 📞 Support & Resources

### Documentation
- **Full README:** `README.md`
- **API Documentation:** `http://localhost:8000/docs` (when running)
- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **Testing Guide:** `TESTING_VERIFICATION.md`

### Demo Files
- **Interactive Demo:** `demo/index.html`
- **Demo Styles:** `demo/styles.css`
- **Demo Script:** `demo/demo.js`

### Contact
- **GitHub Repository:** https://github.com/pallavanand305/Alexa-Plus-Chatbot-.git
- **Issues:** Report bugs via GitHub Issues

---

## ✅ Success Criteria

Your demo is successful when:

✅ Backend starts and responds to health checks  
✅ Dashboard loads and login works  
✅ WebSocket connection is established  
✅ Real-time updates work correctly  
✅ All demo scenarios execute smoothly  
✅ Client can navigate the system independently  
✅ No errors in browser console  
✅ Performance is acceptable (< 3s load times)

---

**🎉 You're ready to demo the Alexa Plus Chatbot system!**

*For technical support or questions, refer to the main README.md or contact the development team.*
