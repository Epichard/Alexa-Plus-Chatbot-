// Alexa Plus Chatbot Demo - Enhanced JavaScript
// Language: JavaScript (Frontend), Python (Backend)

let currentCall = null;
let callHistory = [];
let systemStats = {
    totalCalls: 0,
    emergencyCalls: 0,
    nurseCalls: 0,
    touchCalls: 0
};

// Touch Call Function
function touchCall(resident, room) {
    const timestamp = new Date().toLocaleTimeString();
    const message = `${resident} is calling`;
    
    // Update statistics
    systemStats.totalCalls++;
    systemStats.touchCalls++;
    
    // Update main device
    updateMainDevice(message, 'call');
    
    // Log activity
    addLogEntry(`[${timestamp}] Touch call from ${resident} (${room})`, 'info');
    addLogEntry(`[${timestamp}] Python backend processing touch event`, 'info');
    
    // Store current call
    currentCall = { resident, room, type: 'touch', timestamp };
    
    // Show confirmation button
    showConfirmButton();
    
    // Simulate Python Lambda processing
    setTimeout(() => {
        addLogEntry(`[${timestamp}] Lambda function executed successfully`, 'success');
        addLogEntry(`[${timestamp}] APL document rendered on Echo Show`, 'info');
    }, 500);
    
    // Auto-resolve after 10 seconds if not confirmed
    setTimeout(() => {
        if (currentCall && currentCall.resident === resident) {
            addLogEntry(`[${new Date().toLocaleTimeString()}] Auto-timeout: ${resident}'s call`, 'info');
            resetMainDevice();
        }
    }, 10000);
}

// Help Request Function
function helpRequest(resident, room) {
    const timestamp = new Date().toLocaleTimeString();
    const message = `URGENT: Help needed in ${room}`;
    
    // Update statistics
    systemStats.totalCalls++;
    systemStats.emergencyCalls++;
    
    // Update main device with emergency styling
    updateMainDevice(message, 'emergency');
    
    // Log emergency
    addLogEntry(`[${timestamp}] EMERGENCY: Help request from ${resident} (${room})`, 'emergency');
    addLogEntry(`[${timestamp}] Python emergency handler triggered`, 'emergency');
    addLogEntry(`[${timestamp}] SNS notification sent to caregivers`, 'emergency');
    
    // Store current call
    currentCall = { resident, room, type: 'emergency', timestamp };
    
    // Show confirmation button
    showConfirmButton();
    
    // Simulate Python processing
    setTimeout(() => {
        addLogEntry(`[${timestamp}] Emergency APL template loaded`, 'emergency');
        addLogEntry(`[${timestamp}] DynamoDB call record created`, 'info');
    }, 300);
    
    // Emergency auto-escalation after 5 seconds
    setTimeout(() => {
        if (currentCall && currentCall.type === 'emergency') {
            addLogEntry(`[${new Date().toLocaleTimeString()}] ESCALATION: No response to emergency in ${room}`, 'emergency');
            addLogEntry(`[${new Date().toLocaleTimeString()}] Python escalation algorithm activated`, 'emergency');
        }
    }, 5000);
}

// Nurse Request Function
function nurseRequest(resident, room) {
    const timestamp = new Date().toLocaleTimeString();
    
    // Update statistics
    systemStats.totalCalls++;
    systemStats.nurseCalls++;
    
    // Simulate asking for message
    const messages = [
        "I need water",
        "I need help to the bathroom", 
        "I'm feeling dizzy",
        "Can you bring my medication",
        "I need assistance getting up",
        "The room is too cold",
        "I can't find my glasses"
    ];
    
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    const fullMessage = `${resident} says: ${randomMessage}`;
    
    // Update main device
    updateMainDevice(fullMessage, 'message');
    
    // Log activity
    addLogEntry(`[${timestamp}] Nurse request from ${resident}: "${randomMessage}"`, 'info');
    addLogEntry(`[${timestamp}] Python NLP processing message`, 'info');
    addLogEntry(`[${timestamp}] Message relayed via AWS Lambda`, 'info');
    
    // Store current call
    currentCall = { resident, room, type: 'nurse', message: randomMessage, timestamp };
    
    // Show confirmation button
    showConfirmButton();
    
    // Simulate Python processing
    setTimeout(() => {
        addLogEntry(`[${timestamp}] Nurse intent processed successfully`, 'success');
        addLogEntry(`[${timestamp}] Multi-device messaging active`, 'info');
    }, 800);
}

// Confirm Call Function
function confirmCall() {
    if (!currentCall) return;
    
    const timestamp = new Date().toLocaleTimeString();
    
    // Log confirmation
    addLogEntry(`[${timestamp}] Call confirmed - Caregiver responding to ${currentCall.resident}`, 'success');
    addLogEntry(`[${timestamp}] Python confirmation handler executed`, 'success');
    addLogEntry(`[${timestamp}] DynamoDB record updated to 'acknowledged'`, 'info');
    
    // Reset main device
    resetMainDevice();
    
    // Add to history
    callHistory.push({...currentCall, confirmedAt: timestamp});
    
    // Clear current call
    currentCall = null;
}

// Update Main Device Display
function updateMainDevice(message, type) {
    const notifications = document.getElementById('main-notifications');
    const screen = notifications.parentElement;
    
    notifications.innerHTML = message;
    
    // Apply styling based on type
    screen.classList.remove('notification-active');
    
    if (type === 'emergency') {
        screen.classList.add('notification-active');
        notifications.style.color = '#ff4444';
        notifications.style.fontWeight = 'bold';
    } else if (type === 'call') {
        notifications.style.color = '#ffaa00';
        notifications.style.fontWeight = 'bold';
    } else if (type === 'message') {
        notifications.style.color = '#00aaff';
        notifications.style.fontWeight = 'normal';
    }
}

// Reset Main Device
function resetMainDevice() {
    const notifications = document.getElementById('main-notifications');
    const screen = notifications.parentElement;
    const confirmBtn = document.getElementById('confirm-btn');
    
    notifications.innerHTML = '🏥 Care Home Assistant Ready<br>Monitoring all rooms...';
    notifications.style.color = '#00ff00';
    notifications.style.fontWeight = 'normal';
    
    screen.classList.remove('notification-active');
    confirmBtn.style.display = 'none';
}

// Show Confirmation Button
function showConfirmButton() {
    const confirmBtn = document.getElementById('confirm-btn');
    confirmBtn.style.display = 'block';
}

// Add Log Entry
function addLogEntry(message, type = 'normal') {
    const logContainer = document.getElementById('activity-log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = message;
    
    // Add to top of log
    logContainer.insertBefore(entry, logContainer.firstChild);
    
    // Keep only last 25 entries
    while (logContainer.children.length > 25) {
        logContainer.removeChild(logContainer.lastChild);
    }
    
    // Auto-scroll to top
    logContainer.scrollTop = 0;
}

// Demo Control Functions
function resetDemo() {
    currentCall = null;
    callHistory = [];
    systemStats = {
        totalCalls: 0,
        emergencyCalls: 0,
        nurseCalls: 0,
        touchCalls: 0
    };
    
    resetMainDevice();
    
    // Clear log except initial entries
    const logContainer = document.getElementById('activity-log');
    logContainer.innerHTML = `
        <div class="log-entry">System initialized - Python backend ready</div>
        <div class="log-entry">All Echo Show devices online</div>
        <div class="log-entry">Demo website loaded successfully</div>
    `;
    
    addLogEntry(`[${new Date().toLocaleTimeString()}] Demo reset - All systems ready`, 'success');
    addLogEntry(`[${new Date().toLocaleTimeString()}] Python Lambda function reinitialized`, 'info');
}

function showStatus() {
    const timestamp = new Date().toLocaleTimeString();
    const totalCalls = callHistory.length;
    const pendingCalls = currentCall ? 1 : 0;
    
    addLogEntry(`[${timestamp}] STATUS: ${totalCalls} total calls, ${pendingCalls} pending`, 'info');
    addLogEntry(`[${timestamp}] STATS: Touch(${systemStats.touchCalls}) Emergency(${systemStats.emergencyCalls}) Nurse(${systemStats.nurseCalls})`, 'info');
    addLogEntry(`[${timestamp}] BACKEND: Python Lambda function healthy`, 'success');
    addLogEntry(`[${timestamp}] DATABASE: DynamoDB tables operational`, 'info');
    
    if (currentCall) {
        addLogEntry(`[${timestamp}] PENDING: ${currentCall.resident} (${currentCall.type}) since ${currentCall.timestamp}`, 'info');
    }
}

function testEmergency() {
    const residents = ['Jane', 'John', 'Mary'];
    const rooms = ['Room 1', 'Room 2', 'Room 3'];
    const randomIndex = Math.floor(Math.random() * residents.length);
    
    addLogEntry(`[${new Date().toLocaleTimeString()}] Automated emergency test initiated`, 'info');
    helpRequest(residents[randomIndex], rooms[randomIndex]);
}

function runTests() {
    addLogEntry(`[${new Date().toLocaleTimeString()}] Running Python unit tests...`, 'info');
    
    // Simulate test execution
    const tests = [
        'test_launch_request_main_device',
        'test_help_wake_word_intent', 
        'test_nurse_wake_word_intent',
        'test_touch_event',
        'test_caregiver_confirm_intent',
        'test_apl_documents'
    ];
    
    let testIndex = 0;
    const runNextTest = () => {
        if (testIndex < tests.length) {
            setTimeout(() => {
                addLogEntry(`[${new Date().toLocaleTimeString()}] ✅ ${tests[testIndex]}: PASS`, 'success');
                testIndex++;
                runNextTest();
            }, 500);
        } else {
            addLogEntry(`[${new Date().toLocaleTimeString()}] All Python tests completed successfully`, 'success');
            addLogEntry(`[${new Date().toLocaleTimeString()}] Lambda function ready for deployment`, 'success');
        }
    };
    
    runNextTest();
}

// Simulate periodic system checks
setInterval(() => {
    if (Math.random() < 0.08) { // 8% chance every 30 seconds
        const timestamp = new Date().toLocaleTimeString();
        const healthChecks = [
            'Python Lambda heartbeat - OK',
            'DynamoDB connection - OK', 
            'SNS topic - OK',
            'All Echo Show devices online',
            'Alexa skill endpoint healthy'
        ];
        const randomCheck = healthChecks[Math.floor(Math.random() * healthChecks.length)];
        addLogEntry(`[${timestamp}] ${randomCheck}`, 'info');
    }
}, 30000);

// Initialize demo
document.addEventListener('DOMContentLoaded', function() {
    addLogEntry(`[${new Date().toLocaleTimeString()}] Alexa Plus Chatbot Demo initialized`, 'success');
    addLogEntry(`[${new Date().toLocaleTimeString()}] Backend: Python 3.9+ with AWS Lambda`, 'info');
    addLogEntry(`[${new Date().toLocaleTimeString()}] Frontend: HTML5/CSS3/JavaScript`, 'info');
    addLogEntry(`[${new Date().toLocaleTimeString()}] Voice Platform: Amazon Alexa Skills Kit`, 'info');
    addLogEntry(`[${new Date().toLocaleTimeString()}] Ready for client demonstration`, 'success');
});

// Keyboard shortcuts for demo
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey) {
        switch(event.key) {
            case '1':
                event.preventDefault();
                touchCall('Jane', 'Room 1');
                break;
            case '2':
                event.preventDefault();
                touchCall('John', 'Room 2');
                break;
            case '3':
                event.preventDefault();
                touchCall('Mary', 'Room 3');
                break;
            case 'h':
            case 'H':
                event.preventDefault();
                testEmergency();
                break;
            case 'r':
            case 'R':
                event.preventDefault();
                resetDemo();
                break;
            case 'Enter':
                event.preventDefault();
                if (currentCall) confirmCall();
                break;
            case 't':
            case 'T':
                event.preventDefault();
                runTests();
                break;
        }
    }
});

// Add enhanced keyboard shortcuts info
setTimeout(() => {
    addLogEntry('Enhanced shortcuts: Ctrl+1/2/3 (calls), Ctrl+H (emergency), Ctrl+R (reset), Ctrl+T (tests), Ctrl+Enter (confirm)', 'info');
}, 3000);

// Performance monitoring
let performanceStats = {
    responseTime: 0,
    callsPerMinute: 0,
    lastCallTime: Date.now()
};

function updatePerformanceStats() {
    const now = Date.now();
    performanceStats.responseTime = now - performanceStats.lastCallTime;
    performanceStats.lastCallTime = now;
    
    // Log performance occasionally
    if (Math.random() < 0.1) {
        addLogEntry(`[${new Date().toLocaleTimeString()}] Performance: Response time < 2s (Python optimized)`, 'info');
    }
}

// Update performance stats on each interaction
document.addEventListener('click', updatePerformanceStats);