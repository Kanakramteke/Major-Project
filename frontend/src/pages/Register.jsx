import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { registerDoctor } from '../services/authService'
import './Register.css'

function Register() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    specialization: '',
  })

  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

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
      await registerDoctor(formData)

      navigate('/login', {
        state: {
          message: 'Registration successful. Please log in.',
        },
      })
    } catch (error) {
      const detail = error.response?.data?.detail

      if (typeof detail === 'string') {
        setError(detail)
      } else {
        setError('Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="register-page">
      <section className="register-card">
        <div className="register-header">
          <p className="register-eyebrow">MedExplain AI</p>
          <h1>Create Doctor Account</h1>
          <p>
            Register to access the MedExplain AI clinical platform.
          </p>
        </div>

        {error && (
          <div className="register-error" role="alert">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="register-form">
          <div className="register-field">
            <label htmlFor="full_name">Full Name</label>
            <input
              id="full_name"
              name="full_name"
              type="text"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="Dr. John Doe"
              required
            />
          </div>

          <div className="register-field">
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

          <div className="register-field">
            <label htmlFor="specialization">Specialization</label>
            <input
              id="specialization"
              name="specialization"
              type="text"
              value={formData.specialization}
              onChange={handleChange}
              placeholder="Neurology"
            />
          </div>

          <div className="register-field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter a secure password"
              required
              minLength={8}
            />
          </div>

          <button
            type="submit"
            className="register-submit"
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="register-footer">
          Already have an account?{' '}
          <Link to="/login">Sign in</Link>
        </p>
      </section>
    </main>
  )
}

export default Register