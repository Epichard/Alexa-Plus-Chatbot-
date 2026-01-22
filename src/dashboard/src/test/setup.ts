import '@testing-library/jest-dom'

// Mock WebSocket for testing
global.WebSocket = class MockWebSocket {
  constructor(url: string) {
    // Mock implementation
  }
  
  close() {}
  send() {}
  
  // Mock properties
  readyState = 1
  CONNECTING = 0
  OPEN = 1
  CLOSING = 2
  CLOSED = 3
} as any

// Mock window.location for testing
Object.defineProperty(window, 'location', {
  value: {
    host: 'localhost:3000',
    protocol: 'http:',
    href: 'http://localhost:3000',
  },
  writable: true,
})