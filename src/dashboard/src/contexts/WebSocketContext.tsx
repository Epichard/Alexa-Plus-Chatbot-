import React, { createContext, useContext, useReducer, useEffect, useRef } from 'react'
import { WebSocketMessage, WebSocketState, WebSocketStatus } from '../types'

interface WebSocketContextType extends WebSocketState {
  sendMessage: (message: any) => void
  connect: () => void
  disconnect: () => void
}

type WebSocketAction =
  | { type: 'SET_STATUS'; payload: WebSocketStatus }
  | { type: 'SET_MESSAGE'; payload: WebSocketMessage }
  | { type: 'INCREMENT_RECONNECT_ATTEMPTS' }
  | { type: 'RESET_RECONNECT_ATTEMPTS' }
  | { type: 'SET_CONNECTION_COUNT'; payload: number }

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

const initialState: WebSocketState = {
  status: 'disconnected',
  lastMessage: undefined,
  connectionCount: 0,
  reconnectAttempts: 0,
}

function webSocketReducer(state: WebSocketState, action: WebSocketAction): WebSocketState {
  switch (action.type) {
    case 'SET_STATUS':
      return {
        ...state,
        status: action.payload,
      }
    case 'SET_MESSAGE':
      return {
        ...state,
        lastMessage: action.payload,
      }
    case 'INCREMENT_RECONNECT_ATTEMPTS':
      return {
        ...state,
        reconnectAttempts: state.reconnectAttempts + 1,
      }
    case 'RESET_RECONNECT_ATTEMPTS':
      return {
        ...state,
        reconnectAttempts: 0,
      }
    case 'SET_CONNECTION_COUNT':
      return {
        ...state,
        connectionCount: action.payload,
      }
    default:
      return state
  }
}

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(webSocketReducer, initialState)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const getWebSocketUrl = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return `${protocol}//${host}/ws/live-updates`
  }

  const connect = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    dispatch({ type: 'SET_STATUS', payload: 'connecting' })

    try {
      const ws = new WebSocket(getWebSocketUrl())
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        dispatch({ type: 'SET_STATUS', payload: 'connected' })
        dispatch({ type: 'RESET_RECONNECT_ATTEMPTS' })
        
        // Start ping interval
        startPingInterval()
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          dispatch({ type: 'SET_MESSAGE', payload: message })
          
          // Handle specific message types
          if (message.type === 'connection_established') {
            console.log('WebSocket connection established:', message.connection_id)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        dispatch({ type: 'SET_STATUS', payload: 'disconnected' })
        stopPingInterval()
        
        // Attempt to reconnect if not a clean close
        if (event.code !== 1000 && state.reconnectAttempts < 5) {
          scheduleReconnect()
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        dispatch({ type: 'SET_STATUS', payload: 'error' })
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      dispatch({ type: 'SET_STATUS', payload: 'error' })
    }
  }

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    stopPingInterval()
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected')
      wsRef.current = null
    }
    
    dispatch({ type: 'SET_STATUS', payload: 'disconnected' })
  }

  const sendMessage = (message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected. Cannot send message:', message)
    }
  }

  const scheduleReconnect = () => {
    dispatch({ type: 'INCREMENT_RECONNECT_ATTEMPTS' })
    
    const delay = Math.min(1000 * Math.pow(2, state.reconnectAttempts), 30000) // Exponential backoff, max 30s
    
    reconnectTimeoutRef.current = setTimeout(() => {
      console.log(`Attempting to reconnect (attempt ${state.reconnectAttempts + 1})`)
      connect()
    }, delay)
  }

  const startPingInterval = () => {
    pingIntervalRef.current = setInterval(() => {
      sendMessage({ type: 'ping', timestamp: new Date().toISOString() })
    }, 30000) // Ping every 30 seconds
  }

  const stopPingInterval = () => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current)
      pingIntervalRef.current = null
    }
  }

  // Connect on mount
  useEffect(() => {
    connect()
    
    return () => {
      disconnect()
    }
  }, [])

  // Handle visibility change to reconnect when tab becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && state.status === 'disconnected') {
        connect()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [state.status])

  const value: WebSocketContextType = {
    ...state,
    sendMessage,
    connect,
    disconnect,
  }

  return <WebSocketContext.Provider value={value}>{children}</WebSocketContext.Provider>
}

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}