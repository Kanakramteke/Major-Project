import { useState } from 'react'
import {
  ArrowLeft,
  Brain,
  CheckCircle2,
  FileText,
  Image as ImageIcon,
  Sparkles,
  ExternalLink,
} from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'
import { createReport } from '../services/reportService'
import './Results.css'

function Results() {
  const navigate = useNavigate()
  const location = useLocation()

  const result = location.state?.result
  const patient = location.state?.patient
  const imagePreview = location.state?.imagePreview
  const fromHistory = location.state?.fromHistory

  const [reportLoading, setReportLoading] = useState(false)
  const [reportError, setReportError] = useState('')
  const [reportUrl, setReportUrl] = useState('')

  if (!result) {
    return (
      <div className="results-page">
        <section className="results-empty">
          <div className="results-empty-icon">
            <FileText size={28} />
          </div>

          <h1>No analysis result found</h1>

          <p>
            Please upload an MRI scan and complete the analysis first.
          </p>

          <button
            type="button"
            className="results-primary-button"
            onClick={() => navigate('/upload')}
          >
            Go to MRI Analysis
          </button>
        </section>
      </div>
    )
  }

  const prediction = result.prediction
  const explainability = result.explainability
  const image = result.image

  const apiBaseUrl = 'http://127.0.0.1:8000'

  /*
   * ============================================================
   * ORIGINAL MRI URL
   * ============================================================
   *
   * New analysis:
   *     use the temporary browser preview.
   *
   * Historical analysis:
   *     use the saved filename from the database.
   */

  let originalImageUrl = ''

  if (fromHistory && result.image?.saved_filename) {
    originalImageUrl =
      `${apiBaseUrl}/uploads/${encodeURIComponent(
        result.image.saved_filename,
      )}`
  } else if (fromHistory && result.image?.image_path) {
    const savedFilename =
      result.image.image_path
        .split(/[\\/]/)
        .pop()

    originalImageUrl =
      `${apiBaseUrl}/uploads/${encodeURIComponent(
        savedFilename,
      )}`
  } else if (imagePreview) {
    originalImageUrl = imagePreview
  } else if (explainability.visualization.original) {
    originalImageUrl =
      explainability.visualization.original.startsWith('http')
        ? explainability.visualization.original
        : `${apiBaseUrl}${explainability.visualization.original}`
  }

  const heatmapUrl =
    explainability.visualization.heatmap
      ? explainability.visualization.heatmap.startsWith('http')
        ? explainability.visualization.heatmap
        : `${apiBaseUrl}${explainability.visualization.heatmap}`
      : ''

  const overlayUrl =
    explainability.visualization.overlay
      ? explainability.visualization.overlay.startsWith('http')
        ? explainability.visualization.overlay
        : `${apiBaseUrl}${explainability.visualization.overlay}`
      : ''

  const probabilityEntries = Object.entries(
    prediction.class_probabilities || {},
  )

  /*
   * ============================================================
   * CLINICAL REPORT
   * ============================================================
   */

  async function handleGenerateReport() {
    if (!prediction?.id) {
      setReportError(
        'Prediction ID is unavailable. Please run the MRI analysis again.',
      )
      return
    }

    setReportError('')
    setReportLoading(true)

    try {
      const report = await createReport(prediction.id)

      if (!report.pdf_path) {
        throw new Error(
          'The clinical report was created, but the PDF path was not returned.',
        )
      }

      const filename = report.pdf_path
        .split(/[\\/]/)
        .pop()

      const generatedReportUrl =
        `${apiBaseUrl}/generated-reports/${encodeURIComponent(
          filename,
        )}`

      setReportUrl(generatedReportUrl)

      window.open(
        generatedReportUrl,
        '_blank',
        'noopener,noreferrer',
      )
    } catch (error) {
      console.error('Clinical report generation failed:', error)

      const detail = error.response?.data?.detail

      if (typeof detail === 'string') {
        setReportError(detail)
      } else {
        setReportError(
          'Unable to generate the clinical report. Please try again.',
        )
      }
    } finally {
      setReportLoading(false)
    }
  }

  return (
    <div className="results-page">
      <div className="results-header">
        <button
          type="button"
          className="results-back-button"
          onClick={() => {
            if (fromHistory && patient?.id) {
              navigate(`/patients/${patient.id}`)
            } else {
              navigate('/upload')
            }
          }}
        >
          <ArrowLeft size={17} />

          {fromHistory
            ? 'Back to Patient'
            : 'Back to Analysis'}
        </button>

        <div className="results-title-section">
          <div>
            <p className="results-eyebrow">
              MRI analysis
            </p>

            <h1>Analysis Results</h1>

            <p>
              AI-assisted analysis of the uploaded brain MRI scan.
            </p>
          </div>

          <div className="results-status">
            <CheckCircle2 size={17} />
            Analysis completed
          </div>
        </div>
      </div>

      {patient && (
        <section className="results-patient-card">
          <div className="results-patient-icon">
            <Brain size={21} />
          </div>

          <div>
            <span>Patient</span>
            <strong>{patient.full_name}</strong>
          </div>

          <div>
            <span>Patient ID</span>
            <strong>{patient.patient_id}</strong>
          </div>

          <div>
            <span>Age</span>
            <strong>{patient.age}</strong>
          </div>

          <div>
            <span>Gender</span>
            <strong>
              {patient.gender
                ? patient.gender.charAt(0).toUpperCase() +
                  patient.gender.slice(1)
                : '—'}
            </strong>
          </div>
        </section>
      )}

      <section className="results-summary-grid">
        <div className="results-summary-card prediction-card">
          <div className="results-card-icon">
            <Brain size={20} />
          </div>

          <div>
            <span>Predicted Class</span>

            <strong>
              {prediction.predicted_class
                .replace('_', ' ')
                .replace(/\b\w/g, (letter) =>
                  letter.toUpperCase(),
                )}
            </strong>
          </div>
        </div>

        <div className="results-summary-card">
          <div className="results-card-icon">
            <Sparkles size={20} />
          </div>

          <div>
            <span>Confidence</span>

            <strong>
              {prediction.confidence_percent.toFixed(2)}%
            </strong>
          </div>
        </div>

        <div className="results-summary-card">
          <div className="results-card-icon">
            <Brain size={20} />
          </div>

          <div>
            <span>Model Device</span>

            <strong>
              {prediction.device.toUpperCase()}
            </strong>
          </div>
        </div>

        <div className="results-summary-card">
          <div className="results-card-icon">
            <Sparkles size={20} />
          </div>

          <div>
            <span>Feature Dimension</span>

            <strong>
              {prediction.feature_dimension}
            </strong>
          </div>
        </div>
      </section>

      <section className="results-section">
        <div className="results-section-heading">
          <div>
            <p className="results-eyebrow">
              Model output
            </p>

            <h2>Class Probabilities</h2>
          </div>
        </div>

        <div className="probability-list">
          {probabilityEntries.map(
            ([className, probability]) => {
              const percentage = probability * 100

              return (
                <div
                  className="probability-row"
                  key={className}
                >
                  <div className="probability-label">
                    <span>
                      {className
                        .replace('_', ' ')
                        .replace(
                          /\b\w/g,
                          (letter) =>
                            letter.toUpperCase(),
                        )}
                    </span>

                    <strong>
                      {percentage.toFixed(2)}%
                    </strong>
                  </div>

                  <div className="probability-track">
                    <div
                      className="probability-fill"
                      style={{
                        width: `${percentage}%`,
                      }}
                    />
                  </div>
                </div>
              )
            },
          )}
        </div>
      </section>

      <section className="results-section">
        <div className="results-section-heading">
          <div>
            <p className="results-eyebrow">
              Explainable AI
            </p>

            <h2>Grad-CAM Visualization</h2>

            <p>
              These visualizations show the image regions that
              contributed most strongly to the model's prediction.
            </p>
          </div>
        </div>

        <div className="gradcam-grid">
          <div className="gradcam-card">
            <div className="gradcam-card-header">
              <ImageIcon size={17} />
              <span>Original MRI</span>
            </div>

            <div className="gradcam-image-wrapper">
              {originalImageUrl ? (
                <img
                  src={originalImageUrl}
                  alt="Original brain MRI"
                  onError={(event) => {
                    event.currentTarget.style.display = 'none'
                  }}
                />
              ) : (
                <div
                  style={{
                    padding: '30px',
                    textAlign: 'center',
                    color: '#64748b',
                  }}
                >
                  Original MRI image is unavailable.
                </div>
              )}
            </div>
          </div>

          <div className="gradcam-card">
            <div className="gradcam-card-header">
              <Sparkles size={17} />
              <span>Grad-CAM Heatmap</span>
            </div>

            <div className="gradcam-image-wrapper">
              {heatmapUrl && (
                <img
                  src={heatmapUrl}
                  alt="Grad-CAM heatmap"
                />
              )}
            </div>
          </div>

          <div className="gradcam-card gradcam-overlay-card">
            <div className="gradcam-card-header">
              <Brain size={17} />
              <span>Grad-CAM Overlay</span>
            </div>

            <div className="gradcam-image-wrapper">
              {overlayUrl && (
                <img
                  src={overlayUrl}
                  alt="Grad-CAM overlay showing model attention"
                />
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="results-explanation">
        <div className="results-explanation-icon">
          <Sparkles size={21} />
        </div>

        <div>
          <p className="results-eyebrow">
            AI explanation
          </p>

          <h2>
            Why did the model make this prediction?
          </h2>

          <p>
            {explainability.explanation}
          </p>
        </div>
      </section>

      <section className="results-file-card">
        <div>
          <span>Analyzed MRI</span>

          <strong>
            {image?.original_filename || 'MRI image'}
          </strong>
        </div>

        <div>
          <span>Analysis status</span>

          <strong className="results-completed">
            <CheckCircle2 size={15} />
            Completed
          </strong>
        </div>

        <button
          type="button"
          className="results-report-button"
          onClick={handleGenerateReport}
          disabled={reportLoading}
        >
          <FileText size={17} />

          {reportLoading
            ? 'Generating Report...'
            : 'Generate Clinical Report'}
        </button>
      </section>

      {reportError && (
        <div
          className="results-report-error"
          role="alert"
        >
          {reportError}
        </div>
      )}

      {reportUrl && (
        <section className="results-report-success">
          <div>
            <div className="results-report-success-icon">
              <CheckCircle2 size={20} />
            </div>

            <div>
              <p className="results-eyebrow">
                Clinical report
              </p>

              <h2>Report ready</h2>

              <p>
                The professional clinical report has been
                generated successfully.
              </p>
            </div>
          </div>

          <button
            type="button"
            className="results-report-view-button"
            onClick={() =>
              window.open(
                reportUrl,
                '_blank',
                'noopener,noreferrer',
              )
            }
          >
            <ExternalLink size={17} />
            View Clinical Report
          </button>
        </section>
      )}

      <div className="results-disclaimer">
        <strong>Important:</strong> This AI-generated analysis is
        intended as clinical decision-support information. Grad-CAM
        highlights indicate regions that influenced the model and do
        not represent an exact tumor boundary or constitute a medical
        diagnosis.
      </div>
    </div>
  )
}

export default Results