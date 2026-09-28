import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Brain,
  Eye,
  EyeOff,
  FileText,
  LockKeyhole,
  Mail,
  ShieldCheck,
  Stethoscope,
  UserRound,
} from 'lucide-react'

import { registerDoctor } from '../services/authService'
import './Register.css'

function Register() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    specialization: '',
    password: '',
  })

  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (event) => {
    const { name, value } = event.target

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (formData.password.length < 8) {
      setError('Password must contain at least 8 characters.')
      return
    }

    try {
      setLoading(true)

      await registerDoctor(formData)

      navigate('/login', {
        state: {
          message: 'Account created successfully. Please sign in.',
        },
      })
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          'Unable to create your account. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="register-page">
      <section className="register-card">
        {/* Branding panel */}
        <aside className="register-brand-panel">
          <Link to="/" className="register-brand">
            <span className="register-brand-mark">
              <Brain size={25} />
            </span>

            <span className="register-brand-name">
              MedExplain <span>AI</span>
            </span>
          </Link>

          <div className="register-brand-content">
            <div className="register-badge">
              <ShieldCheck size={16} />
              <span>For healthcare professionals</span>
            </div>

            <h1>
              Make every
              <br />
              diagnosis more
              <br />
              <span>explainable.</span>
            </h1>

            <p className="register-brand-description">
              Explore AI-assisted MRI analysis, visual explanations, and
              automated clinical reporting in one workspace.
            </p>

            <div className="register-feature-list">
              <div className="register-feature">
                <span className="register-feature-icon">
                  <Brain size={19} />
                </span>

                <div>
                  <h3>AI-assisted MRI analysis</h3>
                  <p>Review predictions and confidence scores.</p>
                </div>
              </div>

              <div className="register-feature">
                <span className="register-feature-icon">
                  <FileText size={19} />
                </span>

                <div>
                  <h3>Clinical reporting</h3>
                  <p>Generate structured reports for review.</p>
                </div>
              </div>

              <div className="register-feature">
                <span className="register-feature-icon">
                  <ShieldCheck size={19} />
                </span>

                <div>
                  <h3>Organized workspace</h3>
                  <p>Keep analysis and patient records together.</p>
                </div>
              </div>
            </div>
          </div>

          <p className="register-brand-footer">
            MedExplain AI · Research and clinical decision support
          </p>
        </aside>

        {/* Registration form */}
        <section className="register-form-panel">
          <Link to="/" className="register-back-link">
            <ArrowLeft size={17} />
            <span>Back to home</span>
          </Link>

          <div className="register-form-content">
            <div className="register-heading-icon">
              <Stethoscope size={23} />
            </div>

            <p className="register-eyebrow">DOCTOR REGISTRATION</p>

            <h2>Create your account</h2>

            <p className="register-subtitle">
              Enter your details to get started with MedExplain AI.
            </p>

            {error && (
              <div className="register-error" role="alert">
                {error}
              </div>
            )}

            <form className="register-form" onSubmit={handleSubmit}>
              <div className="register-field">
                <label htmlFor="full_name">Full name</label>

                <div className="register-input-wrap">
                  <UserRound size={18} />

                  <input
                    id="full_name"
                    type="text"
                    name="full_name"
                    placeholder="Enter your full name"
                    value={formData.full_name}
                    onChange={handleChange}
                    autoComplete="name"
                    required
                  />
                </div>
              </div>

              <div className="register-field">
                <label htmlFor="email">Email address</label>

                <div className="register-input-wrap">
                  <Mail size={18} />

                  <input
                    id="email"
                    type="email"
                    name="email"
                    placeholder="doctor@example.com"
                    value={formData.email}
                    onChange={handleChange}
                    autoComplete="email"
                    required
                  />
                </div>
              </div>

              <div className="register-field">
                <label htmlFor="specialization">
                  Specialization
                  <span className="register-optional">Optional</span>
                </label>

                <div className="register-input-wrap">
                  <Stethoscope size={18} />

                  <input
                    id="specialization"
                    type="text"
                    name="specialization"
                    placeholder="e.g. Radiology"
                    value={formData.specialization}
                    onChange={handleChange}
                    autoComplete="organization-title"
                  />
                </div>
              </div>

              <div className="register-field">
                <label htmlFor="password">Password</label>

                <div className="register-input-wrap">
                  <LockKeyhole size={18} />

                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    placeholder="Create a password"
                    value={formData.password}
                    onChange={handleChange}
                    autoComplete="new-password"
                    minLength={8}
                    required
                  />

                  <button
                    type="button"
                    className="register-password-toggle"
                    onClick={() =>
                      setShowPassword((previous) => !previous)
                    }
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <EyeOff size={18} />
                    ) : (
                      <Eye size={18} />
                    )}
                  </button>
                </div>

                <small className="register-field-hint">
                  Use at least 8 characters.
                </small>
              </div>

              <button
                type="submit"
                className="register-submit"
                disabled={loading}
              >
                <span>{loading ? 'Creating account...' : 'Create account'}</span>
                {!loading && <ArrowRight size={18} />}
              </button>
            </form>

            <p className="register-login-prompt">
              Already have an account? <Link to="/login">Sign in</Link>
            </p>

            <div className="register-security-note">
              <ShieldCheck size={16} />
              <span>Your account details are handled securely.</span>
            </div>
          </div>
        </section>
      </section>
    </main>
  )
}

export default Register