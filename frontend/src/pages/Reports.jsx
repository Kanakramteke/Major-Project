
import { useEffect, useState } from 'react'
import { FileText, RefreshCw, Search } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { getDoctorReports } from '../services/reportService'
import { getPatient } from '../services/patientService'
import { getPrediction } from '../services/historyService'
import './Reports.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function formatDate(dateValue) {
  if (!dateValue) return '—'

  return new Date(dateValue).toLocaleString()
}

// Extracts a filename from either a Windows or Unix file path.
function getFilename(filePath) {
  if (!filePath) return ''

  return filePath.split(/[\\/]/).pop()
}

// Converts a backend file path into a browser-accessible URL.
function getStaticFileUrl(filePath, folder) {
  const filename = getFilename(filePath)

  if (!filename) return ''

  return `${API_BASE_URL}/${folder}/${encodeURIComponent(filename)}`
}

function Reports() {
  const navigate = useNavigate()

  const [reports, setReports] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadReports() {
    try {
      setLoading(true)
      setError('')

      const data = await getDoctorReports()
      setReports(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          'Unable to load reports. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadReports()
  }, [])

  const filteredReports = reports.filter((report) => {
    const searchValue = searchTerm.trim().toLowerCase()

    if (!searchValue) return true

    return [
      report.report_title,
      report.report_text,
      report.prediction_id,
      report.id,
    ].some((value) =>
      String(value ?? '').toLowerCase().includes(searchValue),
    )
  })

  async function handleOpenReport(report) {
    try {
      setError('')

      const prediction = await getPrediction(report.prediction_id)
      const patient = await getPatient(prediction.patient_id)

      const originalImageUrl = getStaticFileUrl(
        prediction.saved_filename || prediction.image_path,
        'uploads',
      )

      const heatmapUrl = getStaticFileUrl(
        prediction.heatmap_visualization_path,
        'generated-gradcam',
      )

      const overlayUrl = getStaticFileUrl(
        prediction.overlay_visualization_path,
        'generated-gradcam',
      )

      const result = {
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
          explanation: prediction.explanation || '',
          visualization: {
            original: originalImageUrl,
            heatmap: heatmapUrl,
            overlay: overlayUrl,
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
          result,
          patient,
          imagePreview: null,
          fromHistory: true,
        },
      })
    } catch (err) {
      console.error('Unable to open report analysis:', err)

      setError(
        err.response?.data?.detail ||
          'Unable to open this report’s analysis.',
      )
    }
  }

  return (
    <section className="reports-page">
      <div className="reports-header">
        <div>
          <p className="reports-eyebrow">CLINICAL DOCUMENTS</p>
          <h1>Reports</h1>
          <p className="reports-subtitle">
            View reports generated from your patients’ MRI analyses.
          </p>
        </div>

        <button
          type="button"
          className="reports-refresh-button"
          onClick={loadReports}
          disabled={loading}
        >
          <RefreshCw size={17} />
          Refresh
        </button>
      </div>

      <div className="reports-toolbar">
        <div className="reports-search">
          <Search size={18} />
          <input
            type="search"
            placeholder="Search reports..."
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </div>

        <span className="reports-count">
          {filteredReports.length} report
          {filteredReports.length === 1 ? '' : 's'}
        </span>
      </div>

      {error && (
        <div className="reports-error" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <div className="reports-state">
          <span className="reports-spinner" />
          <p>Loading reports...</p>
        </div>
      ) : filteredReports.length === 0 ? (
        <div className="reports-empty">
          <div className="reports-empty-icon">
            <FileText size={28} />
          </div>

          <h2>{searchTerm ? 'No matching reports' : 'No reports yet'}</h2>

          <p>
            {searchTerm
              ? 'Try a different search term.'
              : 'Generate a clinical report from an MRI analysis to see it here.'}
          </p>
        </div>
      ) : (
        <div className="reports-table-wrapper">
          <table className="reports-table">
            <thead>
              <tr>
                <th>Report</th>
                <th>Prediction ID</th>
                <th>Generated</th>
                <th>PDF</th>
                <th />
              </tr>
            </thead>

            <tbody>
              {filteredReports.map((report) => (
                <tr key={report.id}>
                  <td>
                    <div className="reports-title-cell">
                      <span className="reports-file-icon">
                        <FileText size={18} />
                      </span>

                      <div>
                        <strong>{report.report_title}</strong>
                        <span>Report #{report.id}</span>
                      </div>
                    </div>
                  </td>

                  <td>#{report.prediction_id}</td>
                  <td>{formatDate(report.created_at)}</td>

                  <td>
                    <span
                      className={
                        report.pdf_path
                          ? 'reports-status reports-status-ready'
                          : 'reports-status'
                      }
                    >
                      {report.pdf_path ? 'Available' : 'Not available'}
                    </span>
                  </td>

                  <td>
                    <button
                      type="button"
                      className="reports-view-button"
                      onClick={() => handleOpenReport(report)}
                    >
                      View analysis
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default Reports