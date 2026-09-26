import {
  ArrowLeft,
  CalendarDays,
  FileText,
  LoaderCircle,
  Phone,
  Save,
  UserRound,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  createPatient,
  getPatient,
} from '../services/patientService'
import {
  getPatientHistory,
  getPrediction,
} from '../services/historyService'
import './PatientDetails.css'

function PatientDetails() {
  const navigate = useNavigate()
  const { patientId } = useParams()

  const isNewPatient = !patientId

  const [patient, setPatient] = useState(null)
  const [loading, setLoading] = useState(!isNewPatient)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState('')

  const [viewingPredictionId, setViewingPredictionId] =
    useState(null)

  const [formData, setFormData] = useState({
    patient_id: '',
    full_name: '',
    age: '',
    gender: '',
    contact: '',
    medical_history: '',
  })

  useEffect(() => {
    async function loadPatient() {
      if (isNewPatient) {
        return
      }

      try {
        setLoading(true)
        setError('')

        const data = await getPatient(patientId)

        setPatient(data)
      } catch (error) {
        if (error.response?.status === 404) {
          setError('Patient not found.')
        } else if (error.response?.status === 401) {
          setError(
            'Your session has expired. Please log in again.',
          )
        } else {
          setError('Unable to load patient details.')
        }
      } finally {
        setLoading(false)
      }
    }

    loadPatient()
  }, [isNewPatient, patientId])

  useEffect(() => {
    async function loadHistory() {
      if (isNewPatient || !patientId) {
        return
      }

      try {
        setHistoryLoading(true)
        setHistoryError('')

        const data = await getPatientHistory(patientId)

        setHistory(data)
      } catch (error) {
        if (error.response?.status === 401) {
          setHistoryError(
            'Your session has expired. Please log in again.',
          )
        } else if (error.response?.status === 404) {
          setHistoryError(
            'Patient history could not be found.',
          )
        } else {
          setHistoryError(
            'Unable to load MRI analysis history.',
          )
        }
      } finally {
        setHistoryLoading(false)
      }
    }

    loadHistory()
  }, [isNewPatient, patientId])

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
    setSaving(true)

    try {
      await createPatient({
        patient_id: formData.patient_id.trim(),
        full_name: formData.full_name.trim(),
        age: Number(formData.age),
        gender: formData.gender,
        contact: formData.contact.trim() || null,
        medical_history:
          formData.medical_history.trim() || null,
      })

      navigate('/patients')
    } catch (error) {
      const detail = error.response?.data?.detail

      if (typeof detail === 'string') {
        setError(detail)
      } else if (error.response?.status === 401) {
        setError(
          'Your session has expired. Please log in again.',
        )
      } else {
        setError(
          'Unable to save patient. Please try again.',
        )
      }
    } finally {
      setSaving(false)
    }
  }

  async function handleViewAnalysis(predictionId) {
    try {
      setViewingPredictionId(predictionId)
      setHistoryError('')

      const prediction = await getPrediction(predictionId)

      const apiBaseUrl = 'http://127.0.0.1:8000'

      const heatmapFilename =
        prediction.heatmap_visualization_path
          ? prediction.heatmap_visualization_path
              .split(/[\\/]/)
              .pop()
          : null

      const overlayFilename =
        prediction.overlay_visualization_path
          ? prediction.overlay_visualization_path
              .split(/[\\/]/)
              .pop()
          : null

      const historicalResult = {
        prediction: {
          predicted_class:
            prediction.predicted_class,

          confidence:
            prediction.confidence,

          confidence_percent:
            prediction.confidence_percent,

          class_probabilities:
            prediction.class_probabilities,

          feature_dimension:
            prediction.feature_dimension,

          device:
            prediction.device,
        },

        explainability: {
          explanation:
            prediction.explanation ||
            'No explanation was saved for this analysis.',

          visualization: {
            original:
              `${apiBaseUrl}/uploads/${prediction.saved_filename}`,

            heatmap: heatmapFilename
              ? `${apiBaseUrl}/generated-gradcam/${heatmapFilename}`
              : '',

            overlay: overlayFilename
              ? `${apiBaseUrl}/generated-gradcam/${overlayFilename}`
              : '',
          },
        },

        image: {
          original_filename:
            prediction.original_filename,

          saved_filename:
            prediction.saved_filename,

          image_path:
            prediction.image_path,
        },
      }

      navigate('/results', {
        state: {
          result: historicalResult,
          patient,
          imagePreview: null,
          fromHistory: true,
        },
      })
    } catch (error) {
      if (error.response?.status === 401) {
        setHistoryError(
          'Your session has expired. Please log in again.',
        )
      } else if (error.response?.status === 404) {
        setHistoryError(
          'The selected MRI analysis could not be found.',
        )
      } else {
        setHistoryError(
          'Unable to open the saved MRI analysis.',
        )
      }
    } finally {
      setViewingPredictionId(null)
    }
  }

  function formatPredictionClass(predictedClass) {
    if (!predictedClass) {
      return '—'
    }

    if (predictedClass === 'notumor') {
      return 'No Tumor'
    }

    return predictedClass
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (character) =>
        character.toUpperCase(),
      )
  }

  function formatDate(dateValue) {
    if (!dateValue) {
      return '—'
    }

    return new Date(dateValue).toLocaleString()
  }

  if (isNewPatient) {
    return (
      <div className="patient-details-page">
        <button
          type="button"
          className="patient-back-button"
          onClick={() => navigate('/patients')}
        >
          <ArrowLeft size={17} />
          Back to Patients
        </button>

        <section className="patient-form-header">
          <div className="patient-form-icon">
            <UserRound size={24} />
          </div>

          <div>
            <p className="patient-form-eyebrow">
              Patient management
            </p>

            <h1>Add New Patient</h1>

            <p>
              Create a patient record before starting an MRI analysis.
            </p>
          </div>
        </section>

        <section className="patient-form-card">
          {error && (
            <div
              style={{
                marginBottom: '20px',
                padding: '12px 14px',
                borderRadius: '9px',
                background: '#fef2f2',
                color: '#991b1b',
                fontSize: '13px',
                lineHeight: 1.5,
              }}
              role="alert"
            >
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="patient-form-section">
              <h2>Patient Information</h2>

              <p>
                Enter the basic information required for the patient
                record.
              </p>
            </div>

            <div className="patient-form-grid">
              <div className="patient-form-field">
                <label htmlFor="full_name">
                  Full Name
                </label>

                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  placeholder="Enter patient's full name"
                  value={formData.full_name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="patient-form-field">
                <label htmlFor="patient_id">
                  Patient ID
                </label>

                <input
                  id="patient_id"
                  name="patient_id"
                  type="text"
                  placeholder="e.g. PAT-001"
                  value={formData.patient_id}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="patient-form-field">
                <label htmlFor="age">
                  Age
                </label>

                <input
                  id="age"
                  name="age"
                  type="number"
                  min="0"
                  max="120"
                  placeholder="Enter age"
                  value={formData.age}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="patient-form-field">
                <label htmlFor="gender">
                  Gender
                </label>

                <select
                  id="gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  required
                >
                  <option value="" disabled>
                    Select gender
                  </option>

                  <option value="male">
                    Male
                  </option>

                  <option value="female">
                    Female
                  </option>

                  <option value="other">
                    Other
                  </option>
                </select>
              </div>

              <div className="patient-form-field patient-form-field-full">
                <label htmlFor="contact">
                  Contact Number
                </label>

                <input
                  id="contact"
                  name="contact"
                  type="tel"
                  placeholder="Enter contact number"
                  value={formData.contact}
                  onChange={handleChange}
                />
              </div>

              <div className="patient-form-field patient-form-field-full">
                <label htmlFor="medical_history">
                  Medical History
                </label>

                <textarea
                  id="medical_history"
                  name="medical_history"
                  rows="4"
                  placeholder="Enter relevant medical history, if available"
                  value={formData.medical_history}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="patient-form-actions">
              <button
                type="button"
                className="patient-cancel-button"
                onClick={() => navigate('/patients')}
                disabled={saving}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="patient-save-button"
                disabled={saving}
              >
                <Save size={17} />

                {saving
                  ? 'Saving Patient...'
                  : 'Save Patient'}
              </button>
            </div>
          </form>
        </section>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="patient-details-page">
        <button
          type="button"
          className="patient-back-button"
          onClick={() => navigate('/patients')}
        >
          <ArrowLeft size={17} />
          Back to Patients
        </button>

        <section className="patient-details-loading">
          <LoaderCircle
            size={24}
            className="patient-loading-icon"
          />

          <h2>
            Loading patient details...
          </h2>

          <p>
            Fetching the patient record from your workspace.
          </p>
        </section>
      </div>
    )
  }

  if (error || !patient) {
    return (
      <div className="patient-details-page">
        <button
          type="button"
          className="patient-back-button"
          onClick={() => navigate('/patients')}
        >
          <ArrowLeft size={17} />
          Back to Patients
        </button>

        <section className="patient-details-error">
          <div className="patient-form-icon">
            <UserRound size={24} />
          </div>

          <h2>
            {error || 'Patient not found.'}
          </h2>

          <p>
            The requested patient record could not be loaded.
          </p>
        </section>
      </div>
    )
  }

  return (
    <div className="patient-details-page">
      <button
        type="button"
        className="patient-back-button"
        onClick={() => navigate('/patients')}
      >
        <ArrowLeft size={17} />
        Back to Patients
      </button>

      <section className="patient-form-header">
        <div className="patient-form-icon">
          <UserRound size={24} />
        </div>

        <div>
          <p className="patient-form-eyebrow">
            Patient profile
          </p>

          <h1>
            {patient.full_name}
          </h1>

          <p>
            Patient ID: {patient.patient_id}
          </p>
        </div>
      </section>

      <section className="patient-form-card">
        <div className="patient-form-section">
          <h2>
            Patient Information
          </h2>

          <p>
            Review the patient's registered information before
            starting an MRI analysis.
          </p>
        </div>

        <div className="patient-info-grid">
          <div className="patient-info-item">
            <span>
              Patient ID
            </span>

            <strong>
              {patient.patient_id}
            </strong>
          </div>

          <div className="patient-info-item">
            <span>
              Full Name
            </span>

            <strong>
              {patient.full_name}
            </strong>
          </div>

          <div className="patient-info-item">
            <span>
              Age
            </span>

            <strong>
              {patient.age} years
            </strong>
          </div>

          <div className="patient-info-item">
            <span>
              Gender
            </span>

            <strong>
              {patient.gender.charAt(0).toUpperCase() +
                patient.gender.slice(1)}
            </strong>
          </div>

          <div className="patient-info-item">
            <span>
              <Phone size={14} />
              Contact
            </span>

            <strong>
              {patient.contact || 'Not provided'}
            </strong>
          </div>

          <div className="patient-info-item">
            <span>
              <CalendarDays size={14} />
              Registered
            </span>

            <strong>
              {new Date(
                patient.created_at,
              ).toLocaleDateString()}
            </strong>
          </div>

          <div className="patient-info-item patient-info-item-full">
            <span>
              <FileText size={14} />
              Medical History
            </span>

            <strong>
              {patient.medical_history ||
                'No medical history provided.'}
            </strong>
          </div>
        </div>

        <div className="patient-details-actions">
          <button
            type="button"
            className="patient-analysis-button"
            onClick={() =>
              navigate(
                `/upload?patientId=${patient.id}`,
              )
            }
          >
            Start MRI Analysis
          </button>
        </div>
      </section>

      {/* =====================================================
          MRI ANALYSIS HISTORY
      ===================================================== */}

      <section className="patient-form-card patient-history-card">
        <div className="patient-form-section">
          <h2>
            MRI Analysis History
          </h2>

          <p>
            Previous MRI analyses recorded for this patient.
          </p>
        </div>

        {historyLoading ? (
          <div className="patient-history-loading">
            <LoaderCircle
              size={22}
              className="patient-loading-icon"
            />

            <span>
              Loading MRI analysis history...
            </span>
          </div>
        ) : historyError ? (
          <div
            className="patient-history-error"
            role="alert"
          >
            {historyError}
          </div>
        ) : history.length === 0 ? (
          <div className="patient-history-empty">
            <div className="patient-history-empty-icon">
              <FileText size={22} />
            </div>

            <div>
              <h3>
                No MRI analyses yet
              </h3>

              <p>
                Start an MRI analysis for this patient to
                create the first history record.
              </p>
            </div>
          </div>
        ) : (
          <div className="patient-history-list">
            {history.map((prediction) => (
              <article
                key={prediction.id}
                className="patient-history-item"
              >
                <div className="patient-history-item-main">
                  <div className="patient-history-item-icon">
                    <FileText size={20} />
                  </div>

                  <div className="patient-history-item-content">
                    <div className="patient-history-item-heading">
                      <h3>
                        {formatPredictionClass(
                          prediction.predicted_class,
                        )}
                      </h3>

                      <span>
                        {formatDate(
                          prediction.created_at,
                        )}
                      </span>
                    </div>

                    <div className="patient-history-item-details">
                      <div>
                        <span>
                          Confidence
                        </span>

                        <strong>
                          {prediction.confidence_percent}%
                        </strong>
                      </div>

                      <div>
                        <span>
                          Model
                        </span>

                        <strong>
                          Feature Fusion
                        </strong>
                      </div>

                      <div>
                        <span>
                          Device
                        </span>

                        <strong>
                          {prediction.device}
                        </strong>
                      </div>
                    </div>

                    <p className="patient-history-filename">
                      MRI: {prediction.original_filename}
                    </p>

                    <div className="patient-history-actions">
                      <button
                        type="button"
                        className="patient-analysis-button"
                        onClick={() =>
                          handleViewAnalysis(
                            prediction.id,
                          )
                        }
                        disabled={
                          viewingPredictionId ===
                          prediction.id
                        }
                      >
                        {viewingPredictionId ===
                        prediction.id ? (
                          <>
                            <LoaderCircle
                              size={15}
                              className="patient-loading-icon"
                            />
                            Opening Analysis...
                          </>
                        ) : (
                          <>
                            <FileText size={15} />
                            View Analysis
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

export default PatientDetails