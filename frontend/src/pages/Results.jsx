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
   * NORMALIZE PREDICTED CLASS
   * ============================================================
   */

  const normalizedPredictedClass = String(
    prediction?.predicted_class || '',
  )
    .toLowerCase()
    .replace(/[\s_-]/g, '')

  const isNoTumorPrediction =
    normalizedPredictedClass === 'notumor'

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
  } else if (explainability?.visualization?.original) {
    originalImageUrl =
      explainability.visualization.original.startsWith('http')
        ? explainability.visualization.original
        : `${apiBaseUrl}${explainability.visualization.original}`
  }

  /*
   * ============================================================
   * GRAD-CAM IMAGE URLS
   * ============================================================
   */

  const heatmapPath =
    explainability?.visualization?.heatmap || ''

  const heatmapUrl = heatmapPath
    ? heatmapPath.startsWith('http')
      ? heatmapPath
      : `${apiBaseUrl}${heatmapPath}`
    : ''

  const overlayPath =
    explainability?.visualization?.overlay || ''

  const overlayUrl = overlayPath
    ? overlayPath.startsWith('http')
      ? overlayPath
      : `${apiBaseUrl}${overlayPath}`
    : ''

  /*
   * ============================================================
   * CLASS PROBABILITIES
   * ============================================================
   */

  const probabilityEntries = Object.entries(
    prediction.class_probabilities || {},
  )

  /*
   * Display small nonzero probabilities as "<0.0001%"
   * instead of rounding them to 0.0000%.
   */
  function formatProbability(probability) {
    const percentage = Number(probability) * 100

    if (!Number.isFinite(percentage)) {
      return '—'
    }

    if (percentage > 0 && percentage < 0.0001) {
      return '<0.0001%'
    }

    return `${percentage.toFixed(4)}%`
  }

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
      console.error(
        'Clinical report generation failed:',
        error,
      )

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

  /*
   * ============================================================
   * PAGE
   * ============================================================
   */

  return (
    <div className="results-page">
      {/* ======================================================
          HEADER
      ====================================================== */}

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

      {/* ======================================================
          PATIENT DETAILS
      ====================================================== */}

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

      {/* ======================================================
          PREDICTION SUMMARY
      ====================================================== */}

      <section className="results-summary-grid">
        <div className="results-summary-card prediction-card">
          <div className="results-card-icon">
            <Brain size={20} />
          </div>

          <div>
            <span>Predicted Class</span>

            <strong>
              {String(prediction.predicted_class || '')
                .replace(/[_-]/g, ' ')
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
              {Number(
                prediction.confidence_percent || 0,
              ).toFixed(2)}
              %
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
              {String(prediction.device || '—').toUpperCase()}
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
              {prediction.feature_dimension ?? '—'}
            </strong>
          </div>
        </div>
      </section>

      {/* ======================================================
          CLASS PROBABILITIES
      ====================================================== */}

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
              const numericProbability =
                Number(probability)

              const percentage =
                Number.isFinite(numericProbability)
                  ? Math.min(
                      100,
                      Math.max(
                        0,
                        numericProbability * 100,
                      ),
                    )
                  : 0

              const displayClassName = className
                .replace(/[_-]/g, ' ')
                .replace(/\b\w/g, (letter) =>
                  letter.toUpperCase(),
                )

              return (
                <div
                  className="probability-row"
                  key={className}
                >
                  <div className="probability-label">
                    <span>{displayClassName}</span>

                    <strong>
                      {formatProbability(probability)}
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

      {/* ======================================================
          GRAD-CAM VISUALIZATION
      ====================================================== */}

      <section className="results-section">
        <div className="results-section-heading">
          <div>
            <p className="results-eyebrow">
              Explainable AI
            </p>

            <h2>Grad-CAM Visualization</h2>

            <p>
              {isNoTumorPrediction
                ? 'The model predicted No Tumor. Tumor localization is not displayed for this class.'
                : 'These visualizations show image regions that influenced the model’s prediction. They do not identify an exact tumor boundary.'}
            </p>
          </div>
        </div>

        <div className="gradcam-grid">
          {/* ORIGINAL MRI — SHOWN FOR EVERY PREDICTION */}

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

          {/* NO TUMOR MESSAGE OR TUMOR GRAD-CAM */}

          {isNoTumorPrediction ? (
            <div
              className="gradcam-card gradcam-no-tumor-notice"
              role="note"
              style={{
                minHeight: '280px',
                padding: '32px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                background: '#f8f9fd',
              }}
            >
              <div
                style={{
                  width: '52px',
                  height: '52px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                  borderRadius: '14px',
                  background: '#e9ecfa',
                  color: '#374375',
                }}
              >
                <Brain size={24} />
              </div>

              <h3
                style={{
                  margin: '0 0 10px',
                  color: '#26345f',
                  fontSize: '18px',
                }}
              >
                No Tumor Predicted
              </h3>

              <p
                style={{
                  maxWidth: '420px',
                  margin: 0,
                  color: '#64708a',
                  lineHeight: 1.7,
                }}
              >
                Tumor localization is not displayed for this
                prediction. Grad-CAM highlights model attention
                for a selected class; it does not confirm the
                presence or absence of a tumor.
              </p>
            </div>
          ) : (
            <>
              {/* GRAD-CAM HEATMAP */}

              <div className="gradcam-card">
                <div className="gradcam-card-header">
                  <Sparkles size={17} />
                  <span>Grad-CAM Heatmap</span>
                </div>

                <div className="gradcam-image-wrapper">
                  {heatmapUrl ? (
                    <img
                      src={heatmapUrl}
                      alt="Grad-CAM heatmap showing model attention"
                    />
                  ) : (
                    <div
                      style={{
                        padding: '30px',
                        textAlign: 'center',
                        color: '#64748b',
                      }}
                    >
                      Grad-CAM heatmap is unavailable.
                    </div>
                  )}
                </div>
              </div>

              {/* GRAD-CAM OVERLAY */}

              <div className="gradcam-card gradcam-overlay-card">
                <div className="gradcam-card-header">
                  <Brain size={17} />
                  <span>Grad-CAM Overlay</span>
                </div>

                <div className="gradcam-image-wrapper">
                  {overlayUrl ? (
                    <img
                      src={overlayUrl}
                      alt="Grad-CAM overlay showing model attention"
                    />
                  ) : (
                    <div
                      style={{
                        padding: '30px',
                        textAlign: 'center',
                        color: '#64748b',
                      }}
                    >
                      Grad-CAM overlay is unavailable.
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </section>

      {/* ======================================================
          AI EXPLANATION
      ====================================================== */}

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
            {explainability?.explanation ||
              'No explanation was provided for this prediction.'}
          </p>
        </div>
      </section>

      {/* ======================================================
          ANALYZED FILE AND REPORT
      ====================================================== */}

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

      {/* REPORT ERROR */}

      {reportError && (
        <div
          className="results-report-error"
          role="alert"
        >
          {reportError}
        </div>
      )}

      {/* REPORT SUCCESS */}

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

      {/* ======================================================
          DISCLAIMER
      ====================================================== */}

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