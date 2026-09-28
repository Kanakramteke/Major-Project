
import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  Activity,
  ArrowLeft,
  Brain,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'
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
  const [showPassword, setShowPassword] = useState(false)

  const registrationMessage = location.state?.message || ''

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }))

    if (error) {
      setError('')
    }
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
    <main className="auth-page">
      <section className="auth-brand-panel">
        <Link to="/" className="auth-brand" aria-label="MedExplain AI home">
          <span className="auth-brand-icon">
            <Brain size={25} strokeWidth={1.8} />
          </span>

          <span>
            <span className="auth-brand-name">MedExplain AI</span>
            <span className="auth-brand-tagline">
              Explainable medical imaging
            </span>
          </span>
        </Link>

        <div className="auth-panel-content">
          <span className="auth-eyebrow">
            <Sparkles size={14} />
            AI-POWERED CLINICAL SUPPORT
          </span>

          <h1>
            Clarity in every
            <span>brain scan.</span>
          </h1>

          <p>
            Access explainable MRI analysis, visual insights, and
            structured clinical reports through one secure workspace.
          </p>

          <div className="auth-benefits">
            <div className="auth-benefit">
              <span className="auth-benefit-icon">
                <Activity size={18} />
              </span>
              <span>
                <strong>AI-assisted MRI analysis</strong>
                <small>Review predicted tumor categories and confidence.</small>
              </span>
            </div>

            <div className="auth-benefit">
              <span className="auth-benefit-icon">
                <Brain size={18} />
              </span>
              <span>
                <strong>Visual explainability</strong>
                <small>Explore Grad-CAM visualizations alongside MRI scans.</small>
              </span>
            </div>

            <div className="auth-benefit">
              <span className="auth-benefit-icon">
                <ShieldCheck size={18} />
              </span>
              <span>
                <strong>Clinical reporting workflow</strong>
                <small>Generate structured reports for review.</small>
              </span>
            </div>
          </div>
        </div>

        <p className="auth-panel-footer">
          MedExplain AI · Research and clinical decision-support platform
        </p>
      </section>

      <section className="auth-form-panel">
        <div className="auth-form-wrapper">
          <Link to="/" className="back-link">
            <ArrowLeft size={15} />
            Back to home
          </Link>

          <div className="auth-form-heading">
            <span>DOCTOR PORTAL</span>
            <h2>Welcome back</h2>
            <p>
              Sign in to continue to your MedExplain AI workspace.
            </p>
          </div>

          {registrationMessage && (
            <div className="auth-message auth-message-success" role="status">
              <ShieldCheck size={17} />
              <span>{registrationMessage}</span>
            </div>
          )}

          {error && (
            <div className="auth-message auth-message-error" role="alert">
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-field">
              <label htmlFor="email">Email address</label>

              <div className="input-wrapper">
                <Mail size={18} aria-hidden="true" />
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="doctor@example.com"
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            <div className="form-field">
              <label htmlFor="password">Password</label>

              <div className="input-wrapper">
                <LockKeyhole size={18} aria-hidden="true" />
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword((previous) => !previous)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  aria-pressed={showPassword}
                >
                  {showPassword ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}
                </button>
              </div>
            </div>

            <div className="form-options">
              <span className="secure-note">
                <ShieldCheck size={14} />
                Secure doctor sign-in
              </span>

              <button
                type="button"
                className="forgot-button"
                onClick={() =>
                  setError('Password reset is not available yet.')
                }
              >
                Forgot password?
              </button>
            </div>

            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="login-spinner" />
                  Signing in...
                </>
              ) : (
                <>
                  Sign in to your account
                  <span aria-hidden="true">→</span>
                </>
              )}
            </button>
          </form>

          <div className="auth-switch">
            <span>Don't have an account?</span>
            <Link to="/register">Create an account</Link>
          </div>

          <p className="auth-disclaimer">
            MedExplain AI is a research and clinical decision-support
            platform. AI-generated results should be reviewed by a
            qualified healthcare professional.
          </p>
        </div>
      </section>
    </main>
  )
}

export default Login