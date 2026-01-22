import React, { useEffect, useState } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  Phone as PhoneIcon,
  Emergency as EmergencyIcon,
  People as PeopleIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'

import { useWebSocket } from '../contexts/WebSocketContext'
import { CallEvent, SystemOverview, DashboardMetrics } from '../types'

export default function DashboardPage() {
  const [recentCalls, setRecentCalls] = useState<CallEvent[]>([])
  const [systemStatus, setSystemStatus] = useState<SystemOverview | null>(null)
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { lastMessage, status: wsStatus } = useWebSocket()

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      switch (lastMessage.type) {
        case 'call_event':
          // Add new call to recent calls
          setRecentCalls(prev => [lastMessage.data, ...prev.slice(0, 9)])
          break
        case 'system_status':
          setSystemStatus(lastMessage.data)
          break
      }
    }
  }, [lastMessage])

  // Load initial data
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true)
        
        // In a real app, these would be API calls
        // For now, we'll use mock data
        
        const mockCalls: CallEvent[] = [
          {
            event_id: '1',
            timestamp: new Date().toISOString(),
            resident_id: 'resident-1',
            event_type: 'touch_call',
            status: 'active',
            message: 'Jane is calling',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            event_id: '2',
            timestamp: new Date(Date.now() - 300000).toISOString(),
            resident_id: 'resident-2',
            event_type: 'emergency',
            status: 'acknowledged',
            caregiver_id: 'caregiver-1',
            response_time: 45,
            message: 'Help needed in Room 2',
            created_at: new Date(Date.now() - 300000).toISOString(),
            updated_at: new Date(Date.now() - 240000).toISOString(),
          },
        ]

        const mockSystemStatus: SystemOverview = {
          overall_status: 'healthy',
          components: [
            {
              timestamp: new Date().toISOString(),
              component: 'fastapi_backend',
              status: 'healthy',
              metrics: { response_time: 45.2 },
              alerts: [],
              response_time: 45.2,
              uptime: 99.9,
            },
            {
              timestamp: new Date().toISOString(),
              component: 'lambda_backend',
              status: 'healthy',
              metrics: { invocations: 1250 },
              alerts: [],
              response_time: 120.0,
              uptime: 99.8,
            },
          ],
          last_updated: new Date().toISOString(),
          active_alerts: 0,
          total_calls_today: 15,
          active_residents: 8,
        }

        const mockMetrics: DashboardMetrics = {
          timestamp: new Date().toISOString(),
          calls: {
            today: 15,
            this_week: 89,
            total_recent: 156,
            by_type: {
              touch_call: 45,
              emergency: 8,
              nurse_comm: 23,
            },
            avg_response_time_seconds: 67.5,
          },
          residents: {
            active: 8,
            total: 10,
          },
          system: {
            uptime_hours: 24.5,
            memory_usage_percent: 78.5,
            cpu_usage_percent: 45.2,
          },
        }

        setRecentCalls(mockCalls)
        setSystemStatus(mockSystemStatus)
        setMetrics(mockMetrics)
        
      } catch (err) {
        setError('Failed to load dashboard data')
        console.error('Dashboard data loading error:', err)
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon color="success" />
      case 'degraded':
        return <WarningIcon color="warning" />
      case 'down':
        return <ErrorIcon color="error" />
      default:
        return <CheckCircleIcon />
    }
  }

  const getCallTypeIcon = (type: string) => {
    switch (type) {
      case 'emergency':
        return <EmergencyIcon color="error" />
      case 'nurse_comm':
        return <PhoneIcon color="primary" />
      default:
        return <PhoneIcon />
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress size={48} />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        {error}
      </Alert>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        Dashboard Overview
      </Typography>

      <Grid container spacing={3}>
        {/* Metrics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Calls Today
              </Typography>
              <Typography variant="h4" component="div" color="primary">
                {metrics?.calls.today || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Residents
              </Typography>
              <Typography variant="h4" component="div" color="primary">
                {metrics?.residents.active || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Response Time
              </Typography>
              <Typography variant="h4" component="div" color="primary">
                {metrics?.calls.avg_response_time_seconds || 0}s
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                System Status
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {getStatusIcon(systemStatus?.overall_status || 'healthy')}
                <Typography variant="h6" component="div">
                  {systemStatus?.overall_status || 'Healthy'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Calls */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Calls
              </Typography>
              <List>
                {recentCalls.map((call) => (
                  <ListItem key={call.event_id} divider>
                    <ListItemIcon>
                      {getCallTypeIcon(call.event_type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={call.message || `${call.event_type} from ${call.resident_id}`}
                      secondary={`${formatTimestamp(call.timestamp)} - ${call.status}`}
                    />
                    <Chip
                      label={call.status}
                      color={call.status === 'active' ? 'error' : call.status === 'acknowledged' ? 'warning' : 'success'}
                      size="small"
                    />
                  </ListItem>
                ))}
                {recentCalls.length === 0 && (
                  <ListItem>
                    <ListItemText
                      primary="No recent calls"
                      secondary="All quiet in the care home"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* System Components */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Components
              </Typography>
              <List>
                {systemStatus?.components.map((component) => (
                  <ListItem key={component.component} divider>
                    <ListItemIcon>
                      {getStatusIcon(component.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={component.component.replace('_', ' ').toUpperCase()}
                      secondary={`${component.uptime}% uptime`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* WebSocket Status */}
      <Box sx={{ mt: 3 }}>
        <Chip
          label={`WebSocket: ${wsStatus}`}
          color={wsStatus === 'connected' ? 'success' : 'error'}
          variant="outlined"
        />
      </Box>
    </Box>
  )
}