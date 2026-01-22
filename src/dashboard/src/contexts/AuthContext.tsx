import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { User, AuthToken, LoginForm } from '../types'
import { authService } from '../services/authService'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: AuthToken } }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'SET_LOADING'; payload: boolean }

interface AuthContextType extends AuthState {
  login: (credentials: LoginForm) => Promise<void>
  logout: () => void
  clearError: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
}

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      }
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token.access_token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      }
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      }
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      }
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      }
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      }
    default:
      return state
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // Check for existing token on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        try {
          authService.setToken(token)
          const user = await authService.getCurrentUser()
          dispatch({
            type: 'LOGIN_SUCCESS',
            payload: {
              user,
              token: { access_token: token, token_type: 'bearer', expires_in: 0 },
            },
          })
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('auth_token')
          authService.clearToken()
          dispatch({ type: 'LOGOUT' })
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false })
      }
    }

    initializeAuth()
  }, [])

  const login = async (credentials: LoginForm) => {
    dispatch({ type: 'LOGIN_START' })
    
    try {
      const tokenResponse = await authService.login(credentials)
      authService.setToken(tokenResponse.access_token)
      
      const user = await authService.getCurrentUser()
      
      // Store token in localStorage
      localStorage.setItem('auth_token', tokenResponse.access_token)
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user, token: tokenResponse },
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed'
      dispatch({ type: 'LOGIN_FAILURE', payload: errorMessage })
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    authService.clearToken()
    dispatch({ type: 'LOGOUT' })
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    clearError,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}