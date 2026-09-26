import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { loginDoctor } from '../services/authService'
import './Login.css'

function Login() {
  const navigate = useNavigate()
  const location = useLocation()

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })

  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const registrationMessage = location.state?.message || ''

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    setError('')
    setLoading(true)

    try {
      const data = await loginDoctor(formData)

      localStorage.setItem('access_token', data.access_token)

      navigate('/dashboard', {
        replace: true,
      })
    } catch (error) {
      const detail = error.response?.data?.detail

      if (typeof detail === 'string') {
        setError(detail)
      } else {
        setError('Login failed. Please check your credentials.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-header">
          <p className="login-eyebrow">MedExplain AI</p>
          <h1>Doctor Login</h1>
          <p>
            Sign in to access the MedExplain AI clinical platform.
          </p>
        </div>

        {registrationMessage && (
          <div className="login-success" role="status">
            {registrationMessage}
          </div>
        )}

        {error && (
          <div className="login-error" role="alert">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-field">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="doctor@example.com"
              required
            />
          </div>

          <div className="login-field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
            />
          </div>

          <div className="login-options">
            <button
              type="button"
              className="forgot-password"
              onClick={() =>
                setError('Password reset is not available yet.')
              }
            >
              Forgot password?
            </button>
          </div>

          <button
            type="submit"
            className="login-submit"
            disabled={loading}
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        <p className="login-footer">
          Don't have an account?{' '}
          <Link to="/register">Create an account</Link>
        </p>
      </section>
    </main>
  )
}

export default Login