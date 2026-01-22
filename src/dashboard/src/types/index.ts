// Type definitions for the Care Home Dashboard

export interface User {
  user_id: string
  username: string
  email: string
  full_name: string
  role: 'admin' | 'caregiver' | 'supervisor'
  active: boolean
  created_at: string
  updated_at: string
  last_login?: string
}

export interface AuthToken {
  access_token: string
  token_type: string
  expires_in: number
}

export interface CallEvent {
  event_id: string
  timestamp: string
  resident_id: string
  event_type: 'touch_call' | 'emergency' | 'nurse_comm'
  status: 'active' | 'acknowledged' | 'resolved'
  caregiver_id?: string
  response_time?: number
  message?: string
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface ResidentProfile {
  resident_id: string
  name: string
  room_number: string
  device_id?: string
  care_level: string
  emergency_contacts: Array<{
    name: string
    relationship: string
    phone: string
    email?: string
  }>
  preferences: Record<string, any>
  active: boolean
  created_at: string
  updated_at: string
}

export interface SystemStatus {
  timestamp: string
  component: 'alexa_skill' | 'lambda_backend' | 'fastapi_backend' | 'dashboard' | 'dynamodb' | 'sns'
  status: 'healthy' | 'degraded' | 'down'
  metrics: Record<string, any>
  alerts: string[]
  response_time?: number
  uptime?: number
}

export interface SystemOverview {
  overall_status: 'healthy' | 'degraded' | 'down'
  components: SystemStatus[]
  last_updated: string
  active_alerts: number
  total_calls_today: number
  active_residents: number
}

export interface WebSocketMessage {
  type: 'call_event' | 'system_status' | 'resident_update' | 'connection_established' | 'pong'
  data?: any
  timestamp: string
  connection_id?: string
}

export interface DashboardMetrics {
  timestamp: string
  calls: {
    today: number
    this_week: number
    total_recent: number
    by_type: Record<string, number>
    avg_response_time_seconds: number
  }
  residents: {
    active: number
    total: number
  }
  system: {
    uptime_hours: number
    memory_usage_percent: number
    cpu_usage_percent: number
  }
}

// API Response types
export interface ApiResponse<T> {
  data?: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// Form types
export interface LoginForm {
  username: string
  password: string
}

export interface ResidentForm {
  name: string
  room_number: string
  device_id?: string
  care_level: string
  emergency_contacts: Array<{
    name: string
    relationship: string
    phone: string
    email?: string
  }>
  preferences?: Record<string, any>
}

export interface CallEventUpdate {
  status?: 'active' | 'acknowledged' | 'resolved'
  caregiver_id?: string
  response_time?: number
  metadata?: Record<string, any>
}

// UI State types
export interface NotificationState {
  open: boolean
  message: string
  severity: 'success' | 'error' | 'warning' | 'info'
}

export interface LoadingState {
  [key: string]: boolean
}

export interface FilterState {
  dateRange?: {
    start: string
    end: string
  }
  status?: string[]
  eventType?: string[]
  residentId?: string
}

// WebSocket connection states
export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export interface WebSocketState {
  status: WebSocketStatus
  lastMessage?: WebSocketMessage
  connectionCount: number
  reconnectAttempts: number
}