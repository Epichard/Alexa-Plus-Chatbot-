import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  Paper,
} from '@mui/material'
import { LocalHospital as HospitalIcon } from '@mui/icons-material'

import { useAuth } from '../contexts/AuthContext'
import { LoginForm } from '../types'

export default function LoginPage() {
  const [formData, setFormData] = useState<LoginForm>({
    username: '',
    password: '',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { login, isAuthenticated, error, clearError } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = (location.state as any)?.from?.pathname || '/dashboard'
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, location])

  // Clear error when component unmounts or form changes
  useEffect(() => {
    return () => clearError()
  }, [clearError])

  useEffect(() => {
    if (error) {
      const timer = setTimeout(clearError, 5000)
      return () => clearTimeout(timer)
    }
  }, [error, clearError])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
    
    // Clear error when user starts typing
    if (error) {
      clearError()
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.username || !formData.password) {
      return
    }

    setIsSubmitting(true)
    
    try {
      await login(formData)
      // Navigation will be handled by the useEffect above
    } catch (err) {
      // Error is handled by the auth context
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          py: 4,
        }}
      >
        <Paper
          elevation={8}
          sx={{
            p: 4,
            width: '100%',
            maxWidth: 400,
            borderRadius: 3,
          }}
        >
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <HospitalIcon
              sx={{
                fontSize: 48,
                color: 'primary.main',
                mb: 2,
              }}
            />
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
              Care Home Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Sign in to access the care management system
            </Typography>
          </Box>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Login Form */}
          <Box component="form" onSubmit={handleSubmit} noValidate>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus
              value={formData.username}
              onChange={handleInputChange}
              disabled={isSubmitting}
              error={!formData.username && isSubmitting}
              helperText={!formData.username && isSubmitting ? 'Username is required' : ''}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleInputChange}
              disabled={isSubmitting}
              error={!formData.password && isSubmitting}
              helperText={!formData.password && isSubmitting ? 'Password is required' : ''}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{
                mt: 3,
                mb: 2,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
              }}
              disabled={isSubmitting || !formData.username || !formData.password}
            >
              {isSubmitting ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} color="inherit" />
                  Signing in...
                </Box>
              ) : (
                'Sign In'
              )}
            </Button>
          </Box>

          {/* Demo Credentials */}
          <Box sx={{ mt: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Demo Credentials:
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              Username: <strong>admin</strong><br />
              Password: <strong>admin123</strong>
            </Typography>
          </Box>
        </Paper>

        {/* Footer */}
        <Typography variant="body2" color="text.secondary" sx={{ mt: 4, textAlign: 'center' }}>
          Alexa Plus Chatbot - Care Home Management System
        </Typography>
      </Box>
    </Container>
  )
}