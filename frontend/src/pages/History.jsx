import { useEffect, useMemo, useState } from 'react'
import {
  Brain,
  CalendarDays,
  FileText,
  LoaderCircle,
  Search,
  UserRound,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { getPatient } from '../services/patientService'
import {
  getDoctorHistory,
  getPrediction,
} from '../services/historyService'
import './History.css'

function History() {
  const navigate = useNavigate()

  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [viewingPredictionId, setViewingPredictionId] =
    useState(null)

  useEffect(() => {
    async function loadHistory() {
      try {
        setLoading(true)
        setError('')

        const data = await getDoctorHistory()
        setHistory(data)
      } catch (error) {
        if (error.response?.status === 401) {
          setError(
            'Your session has expired. Please log in again.',
          )
        } else {
          setError(
            'Unable to load MRI analysis history. Please try again.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadHistory()
  }, [])

  const filteredHistory = useMemo(() => {
    const searchValue = search.trim().toLowerCase()

    if (!searchValue) {
      return history
    }

    return history.filter((item) => {
      const searchableText = [
        item.patient_name,
        item.patient_code,
        item.original_filename,
        item.predicted_class,
        String(item.id),
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()

      return searchableText.includes(searchValue)
    })
  }, [history, search])

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

  async function handleViewAnalysis(item) {
    try {
      setViewingPredictionId(item.id)
      setError('')

      const [prediction, patient] = await Promise.all([
        getPrediction(item.id),
        getPatient(item.patient_id),
      ])

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
          id: prediction.id,
          predicted_class: prediction.predicted_class,
          confidence: prediction.confidence,
          confidence_percent: prediction.confidence_percent,
          class_probabilities: prediction.class_probabilities,
          feature_dimension: prediction.feature_dimension,
          device: prediction.device,
        },

        explainability: {
          explanation:
            prediction.explanation ||
            'No explanation was saved for this analysis.',

          visualization: {
            original: prediction.saved_filename
              ? `${apiBaseUrl}/uploads/${encodeURIComponent(
                  prediction.saved_filename,
                )}`
              : '',

            heatmap: heatmapFilename
              ? `${apiBaseUrl}/generated-gradcam/${encodeURIComponent(
                  heatmapFilename,
                )}`
              : '',

            overlay: overlayFilename
              ? `${apiBaseUrl}/generated-gradcam/${encodeURIComponent(
                  overlayFilename,
                )}`
              : '',
          },
        },

        image: {
          original_filename: prediction.original_filename,
          saved_filename: prediction.saved_filename,
          image_path: prediction.image_path,
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
        setError(
          'Your session has expired. Please log in again.',
        )
      } else if (error.response?.status === 404) {
        setError(
          'The selected MRI analysis or patient could not be found.',
        )
      } else {
        setError(
          'Unable to open this saved MRI analysis. Please try again.',
        )
      }
    } finally {
      setViewingPredictionId(null)
    }
  }

  return (
    <div className="history-page">
      <section className="history-header">
        <div>
          <p className="history-eyebrow">Patient records</p>
          <h1>MRI Analysis History</h1>
          <p>
            Review previous MRI analyses recorded for your active
            patients.
          </p>
        </div>

        <div className="history-total">
          <FileText size={20} />
          <div>
            <strong>{history.length}</strong>
            <span>Total analyses</span>
          </div>
        </div>
      </section>

      <section className="history-card">
        <div className="history-toolbar">
          <div>
            <h2>Previous Analyses</h2>
            <p>
              Search by patient, patient ID, MRI filename, or
              prediction.
            </p>
          </div>

          <label className="history-search">
            <Search size={17} />
            <input
              type="search"
              placeholder="Search history..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </label>
        </div>

        {loading ? (
          <div className="history-state">
            <LoaderCircle
              size={25}
              className="history-loading-icon"
            />
            <h3>Loading MRI history...</h3>
            <p>Fetching previous analyses from your workspace.</p>
          </div>
        ) : error ? (
          <div className="history-state history-state-error" role="alert">
            <h3>Unable to load history</h3>
            <p>{error}</p>
          </div>
        ) : history.length === 0 ? (
          <div className="history-state">
            <div className="history-state-icon">
              <FileText size={25} />
            </div>
            <h3>No MRI analyses yet</h3>
            <p>
              Completed MRI analyses for your patients will appear
              here.
            </p>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="history-state">
            <div className="history-state-icon">
              <Search size={25} />
            </div>
            <h3>No matching analyses</h3>
            <p>Try a different patient name, ID, or filename.</p>
          </div>
        ) : (
          <div className="history-table-wrapper">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Patient</th>
                  <th>MRI Scan</th>
                  <th>Prediction</th>
                  <th>Confidence</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {filteredHistory.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div className="history-patient">
                        <div className="history-patient-icon">
                          <UserRound size={17} />
                        </div>
                        <div>
                          <strong>{item.patient_name}</strong>
                          <span>{item.patient_code}</span>
                        </div>
                      </div>
                    </td>

                    <td>
                      <div className="history-mri">
                        <Brain size={16} />
                        <span>{item.original_filename}</span>
                      </div>
                    </td>

                    <td>
                      <span className="history-prediction">
                        {formatPredictionClass(item.predicted_class)}
                      </span>
                    </td>

                    <td>
                      <strong>
                        {Number(item.confidence_percent).toFixed(2)}%
                      </strong>
                    </td>

                    <td>
                      <div className="history-date">
                        <CalendarDays size={15} />
                        <span>{formatDate(item.created_at)}</span>
                      </div>
                    </td>

                    <td>
                      <button
                        type="button"
                        className="history-view-button"
                        onClick={() => handleViewAnalysis(item)}
                        disabled={viewingPredictionId === item.id}
                      >
                        {viewingPredictionId === item.id ? (
                          <>
                            <LoaderCircle
                              size={15}
                              className="history-loading-icon"
                            />
                            Opening...
                          </>
                        ) : (
                          <>
                            <FileText size={15} />
                            View Analysis
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

export default History