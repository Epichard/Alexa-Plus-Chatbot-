import axios, { AxiosResponse } from 'axios'
import { User, AuthToken, LoginForm } from '../types'

const API_BASE_URL = '/api/v1'

class AuthService {
  private token: string | null = null

  setToken(token: string) {
    this.token = token
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  clearToken() {
    this.token = null
    delete axios.defaults.headers.common['Authorization']
  }

  getToken(): string | null {
    return this.token
  }

  async login(credentials: LoginForm): Promise<AuthToken> {
    try {
      const formData = new FormData()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)

      const response: AxiosResponse<AuthToken> = await axios.post(
        `${API_BASE_URL}/auth/token`,
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      )

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || 'Login failed'
        throw new Error(message)
      }
      throw new Error('Network error occurred')
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response: AxiosResponse<User> = await axios.get(`${API_BASE_URL}/auth/me`)
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || 'Failed to get user info'
        throw new Error(message)
      }
      throw new Error('Network error occurred')
    }
  }

  async register(userData: {
    username: string
    email: string
    full_name: string
    password: string
    role?: string
  }): Promise<User> {
    try {
      const response: AxiosResponse<User> = await axios.post(
        `${API_BASE_URL}/auth/register`,
        userData
      )
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || 'Registration failed'
        throw new Error(message)
      }
      throw new Error('Network error occurred')
    }
  }

  isAuthenticated(): boolean {
    return this.token !== null
  }
}

export const authService = new AuthService()

// Set up axios interceptors for token handling
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      authService.clearToken()
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)