# 🧪 Step-by-Step Testing Guide for Clients

**Complete Testing Walkthrough for Alexa Plus Chatbot System**

---

## 📋 Pre-Testing Checklist

Before you begin testing, make sure you have:

- [ ] Cloned the repository from GitHub
- [ ] Installed Python 3.11+ and Node.js 18+
- [ ] Installed all dependencies (`pip install -r requirements.txt`)
- [ ] Two terminal windows open
- [ ] Web browser ready (Chrome, Firefox, or Edge recommended)

---

## 🚀 Phase 1: System Startup (5 minutes)

### Step 1.1: Start the Backend Server

**Terminal 1:**
```bash
# Navigate to the project directory
cd Alexa-Plus-Chatbot-

# Go to FastAPI directory
cd src/fastapi

# Start the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**What to Look For:**
```
✅ INFO:     Uvicorn running on http://0.0.0.0:8000
✅ INFO:     Application startup complete
```

**If You See Errors:**
- Check Python version: `python --version` (should be 3.11+)
- Reinstall dependencies: `pip install -r requirements.txt`
- Check if port 8000 is available

**Status:** Backend is running ✅

---

### Step 1.2: Verify Backend Health

**Open Browser:**
- Go to: `http://localhost:8000/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "alexa-plus-chatbot-api",
  "version": "1.0.0"
}
```

**Status:** Backend health check passed ✅

---

### Step 1.3: Check API Documentation

**Open Browser:**
- Go to: `http://localhost:8000/docs`

**What You Should See:**
- Interactive API documentation (Swagger UI)
- List of all available endpoints
- Ability to test endpoints

**Try This:**
1. Find the `GET /health` endpoint
2. Click "Try it out"
3. Click "Execute"
4. See the response

**Status:** API documentation accessible ✅

---

### Step 1.4: Start the Dashboard

**Terminal 2 (New Window):**
```bash
# Navigate to dashboard directory
cd Alexa-Plus-Chatbot-/src/dashboard

# Install dependencies (first time only)
npm install

# Start the dashboard
npm run dev
```

**What to Look For:**
```
✅ VITE v4.5.0  ready in 1234 ms
✅ ➜  Local:   http://localhost:3000/
```

**If You See Errors:**
- Check Node.js version: `node --version` (should be 18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check if port 3000 is available

**Status:** Dashboard is running ✅

---

## 🔐 Phase 2: Authentication Testing (3 minutes)

### Step 2.1: Access the Dashboard

**Open Browser:**
- Go to: `http://localhost:3000`

**What You Should See:**
- Login page with username and password fields
- "Alexa Plus Chatbot" branding
- Clean, professional interface

**Status:** Dashboard loads successfully ✅

---

### Step 2.2: Test Login

**Enter Credentials:**
- **Username:** `admin`
- **Password:** `admin123`
- Click "Login" button

**Expected Result:**
- Redirect to main dashboard
- Welcome message appears
- Navigation menu visible
- No error messages

**Status:** Login successful ✅

---

### Step 2.3: Verify Session Persistence

**Test:**
1. Refresh the page (F5)
2. You should remain logged in
3. Dashboard should load without asking for credentials again

**Status:** Session persistence working ✅

---

## 📊 Phase 3: Dashboard Features Testing (10 minutes)

### Step 3.1: Main Dashboard Overview

**What to Check:**
- [ ] Navigation menu on the left
- [ ] Real-time call feed in the center
- [ ] System status indicators
- [ ] User profile in top-right corner
- [ ] WebSocket connection status (green indicator)

**Status:** Dashboard layout correct ✅

---

### Step 3.2: Navigation Testing

**Test Each Menu Item:**

1. **Dashboard** (Home icon)
   - Click it
   - Should show main dashboard
   - ✅ Works

2. **Calls** (Phone icon)
   - Click it
   - Should show call history
   - ✅ Works

3. **Residents** (People icon)
   - Click it
   - Should show resident list
   - ✅ Works

4. **System** (Settings icon)
   - Click it
   - Should show system status
   - ✅ Works

**Status:** All navigation links working ✅

---

### Step 3.3: Resident Management Testing

**Navigate to Residents Page:**

**Test 1: View Residents**
- You should see a list or table of residents
- Each resident should show: name, room number, status
- ✅ Resident list displays

**Test 2: Add New Resident**
1. Click "Add Resident" button
2. Fill in the form:
   - **First Name:** `Test`
   - **Last Name:** `Resident`
   - **Room Number:** `999`
   - **Device ID:** `test_device_123`
3. Click "Save"
4. New resident should appear in the list
5. ✅ Add resident works

**Test 3: Edit Resident**
1. Find the test resident you just added
2. Click "Edit" button
3. Change room number to `998`
4. Click "Save"
5. Changes should be reflected
6. ✅ Edit resident works

**Test 4: Search/Filter**
1. Use the search box (if available)
2. Type "Test"
3. Only matching residents should show
4. ✅ Search works

**Status:** Resident management fully functional ✅

---

### Step 3.4: System Status Testing

**Navigate to System Page:**

**What to Check:**
- [ ] Component health indicators
  - FastAPI Backend: 🟢 Healthy
  - Lambda Backend: 🟢 Healthy
  - DynamoDB: 🟢 Healthy
  - SNS: 🟢 Healthy

- [ ] System metrics
  - Response times
  - Memory usage
  - CPU usage

- [ ] Active alerts count
- [ ] Total calls today
- [ ] Active residents count

**Status:** System status page working ✅

---

## 🔄 Phase 4: Real-Time Features Testing (10 minutes)

### Step 4.1: WebSocket Connection Test

**Check Connection Status:**
- Look at top-right corner of dashboard
- Should see green indicator or "Connected" status
- If red or "Disconnected", refresh the page

**Status:** WebSocket connected ✅

---

### Step 4.2: Real-Time Call Simulation

**Using the Demo Page:**

1. **Open Demo in New Tab:**
   - Navigate to: `file:///path/to/Alexa-Plus-Chatbot-/demo/index.html`
   - Or open `demo/index.html` directly in browser

2. **Keep Dashboard Open in Another Tab:**
   - Position windows side-by-side if possible

3. **Test Touch Call:**
   - In demo page, click "Touch Call" button
   - Watch the dashboard tab
   - New call should appear within 1-2 seconds
   - ✅ Real-time update works

4. **Test Emergency Call:**
   - In demo page, click "Emergency Help" button
   - Watch the dashboard
   - Emergency call should appear in RED
   - ✅ Emergency prioritization works

5. **Test Nurse Request:**
   - In demo page, type message: "I need water"
   - Click "Send to Nurse"
   - Watch the dashboard
   - Message should appear with full text
   - ✅ Message relay works

**Status:** Real-time updates working perfectly ✅

---

### Step 4.3: Call Acknowledgment Test

**On Dashboard:**

1. Find a pending call in the call feed
2. Click "Acknowledge" button
3. Watch the status change to "Acknowledged"
4. Response time should be calculated
5. Call should move to history

**Status:** Call acknowledgment working ✅

---

### Step 4.4: Call Resolution Test

**On Dashboard:**

1. Find an acknowledged call
2. Click "Resolve" button
3. Status should change to "Resolved"
4. Call should be marked as complete

**Status:** Call resolution working ✅

---

## 🔌 Phase 5: API Testing (5 minutes)

### Step 5.1: Test Authentication API

**Using API Documentation:**
1. Go to: `http://localhost:8000/docs`
2. Find `POST /api/v1/auth/token`
3. Click "Try it out"
4. Enter:
   - **username:** `admin`
   - **password:** `admin123`
5. Click "Execute"
6. Should receive JWT token in response

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

**Status:** Authentication API working ✅

---

### Step 5.2: Test Calls API

**Get Recent Calls:**
1. In API docs, find `GET /api/v1/calls/recent`
2. Click "Try it out"
3. Click "Authorize" and paste your JWT token
4. Click "Execute"
5. Should receive list of recent calls

**Status:** Calls API working ✅

---

### Step 5.3: Test Residents API

**Get All Residents:**
1. Find `GET /api/v1/residents`
2. Click "Try it out"
3. Make sure you're authorized
4. Click "Execute"
5. Should receive list of residents

**Status:** Residents API working ✅

---

### Step 5.4: Test System API

**Get System Status:**
1. Find `GET /api/v1/system/status`
2. Click "Try it out"
3. Click "Execute"
4. Should receive system overview

**Expected Response:**
```json
{
  "overall_status": "healthy",
  "components": [...],
  "active_alerts": 0,
  "total_calls_today": 5,
  "active_residents": 3
}
```

**Status:** System API working ✅

---

## 🧪 Phase 6: Integration Testing (10 minutes)

### Step 6.1: End-to-End Call Flow

**Complete Call Lifecycle:**

1. **Create Call** (Demo page)
   - Click "Touch Call"
   - ✅ Call created

2. **Receive Notification** (Dashboard)
   - Call appears in feed
   - ✅ Notification received

3. **Acknowledge Call** (Dashboard)
   - Click "Acknowledge"
   - ✅ Status updated

4. **Resolve Call** (Dashboard)
   - Click "Resolve"
   - ✅ Call completed

5. **View History** (Dashboard)
   - Go to Calls page
   - Find completed call
   - ✅ History recorded

**Status:** End-to-end flow working ✅

---

### Step 6.2: Multi-Call Handling

**Test Concurrent Calls:**

1. Open demo page
2. Quickly create 3 calls:
   - Touch Call
   - Emergency Help
   - Nurse Request
3. Watch dashboard
4. All 3 should appear
5. Emergency should be at top (red)
6. Acknowledge each one
7. All should update correctly

**Status:** Multi-call handling working ✅

---

### Step 6.3: Data Persistence Test

**Test Data Survives Refresh:**

1. Create a call on demo page
2. Acknowledge it on dashboard
3. Refresh the dashboard page (F5)
4. Call should still be there
5. Status should be preserved

**Status:** Data persistence working ✅

---

## 📈 Phase 7: Performance Testing (5 minutes)

### Step 7.1: Load Time Test

**Measure Dashboard Load Time:**

1. Open browser DevTools (F12)
2. Go to Network tab
3. Refresh dashboard page
4. Check "Load" time at bottom

**Expected:** < 3 seconds

**Status:** Load time acceptable ✅

---

### Step 7.2: API Response Time Test

**Measure API Performance:**

1. Go to `http://localhost:8000/docs`
2. Test any endpoint
3. Check response time in the result

**Expected:** < 500ms for most endpoints

**Status:** API response time good ✅

---

### Step 7.3: WebSocket Latency Test

**Measure Real-Time Update Speed:**

1. Open demo page and dashboard side-by-side
2. Note the time when you click "Touch Call"
3. Note the time when it appears on dashboard
4. Calculate difference

**Expected:** < 2 seconds

**Status:** WebSocket latency acceptable ✅

---

## 🐛 Phase 8: Error Handling Testing (5 minutes)

### Step 8.1: Invalid Login Test

**Test:**
1. Logout from dashboard
2. Try to login with wrong password
3. Should see error message
4. Should not be logged in

**Status:** Error handling working ✅

---

### Step 8.2: Network Disconnection Test

**Test:**
1. Stop the backend server (Ctrl+C in Terminal 1)
2. Try to perform action on dashboard
3. Should see error message
4. Restart backend
5. Dashboard should reconnect automatically

**Status:** Network error handling working ✅

---

### Step 8.3: Invalid Data Test

**Test:**
1. Try to add resident with duplicate room number
2. Should see validation error
3. Should not create duplicate

**Status:** Data validation working ✅

---

## ✅ Final Verification Checklist

### System Startup
- [x] Backend starts without errors
- [x] Dashboard starts without errors
- [x] Health checks pass
- [x] API documentation loads

### Authentication
- [x] Login works
- [x] Logout works
- [x] Session persists
- [x] Invalid credentials rejected

### Dashboard Features
- [x] Navigation works
- [x] All pages load
- [x] Resident management works
- [x] System status displays

### Real-Time Features
- [x] WebSocket connects
- [x] Calls appear in real-time
- [x] Status updates instantly
- [x] No lag or delays

### API Functionality
- [x] All endpoints respond
- [x] Authentication works
- [x] Data CRUD operations work
- [x] Error responses correct

### Integration
- [x] End-to-end flow works
- [x] Multi-call handling works
- [x] Data persists correctly
- [x] Cross-component communication works

### Performance
- [x] Load times < 3 seconds
- [x] API responses < 500ms
- [x] WebSocket latency < 2 seconds
- [x] No memory leaks

### Error Handling
- [x] Invalid input rejected
- [x] Network errors handled
- [x] User-friendly error messages
- [x] System recovers gracefully

---

## 🎉 Testing Complete!

**If all checkboxes are marked, your system is:**
✅ Fully functional  
✅ Ready for client demonstration  
✅ Ready for production deployment  
✅ Meeting all requirements

---

## 📊 Test Results Summary

**Total Tests:** 50+  
**Passed:** ___  
**Failed:** ___  
**Success Rate:** ___%

**Critical Issues:** None / List any  
**Minor Issues:** None / List any  
**Recommendations:** List any improvements

---

## 📞 Next Steps

1. **If All Tests Pass:**
   - Schedule client demo
   - Prepare production deployment
   - Document any custom configurations

2. **If Tests Fail:**
   - Review error messages
   - Check troubleshooting guide
   - Contact development team

3. **For Production:**
   - Follow deployment guide
   - Configure AWS resources
   - Set up monitoring
   - Train end users

---

**🎊 Congratulations! You've completed comprehensive testing of the Alexa Plus Chatbot system!**

*For questions or issues, refer to CLIENT_DEMO_GUIDE.md or README.md*
