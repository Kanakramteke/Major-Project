
import {
  ArrowLeft,
  Brain,
  CheckCircle2,
  FileImage,
  LoaderCircle,
  UploadCloud,
  X,
} from 'lucide-react'
import { useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import apiClient from '../services/apiClient'
import { getPatient } from '../services/patientService'
import './Upload.css'

function Upload() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const fileInputRef = useRef(null)

  const patientId = searchParams.get('patientId')

  const [selectedFile, setSelectedFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  function validateFile(file) {
    if (!file) {
      return 'Please select an MRI image.'
    }

    const allowedTypes = ['image/jpeg', 'image/png']

    if (!allowedTypes.includes(file.type)) {
      return 'Only JPG, JPEG, and PNG images are supported.'
    }

    const maxSize = 10 * 1024 * 1024

    if (file.size > maxSize) {
      return 'The image size must be 10 MB or smaller.'
    }

    return ''
  }

  function handleFile(file) {
    setError('')
    setResult(null)

    const validationError = validateFile(file)

    if (validationError) {
      setSelectedFile(null)
      setError(validationError)
      return
    }

    setSelectedFile(file)
  }

  function handleFileInput(event) {
    const file = event.target.files?.[0]

    if (file) {
      handleFile(file)
    }

    event.target.value = ''
  }

  function handleDragOver(event) {
    event.preventDefault()
    event.stopPropagation()
    setDragActive(true)
  }

  function handleDragLeave(event) {
    event.preventDefault()
    event.stopPropagation()
    setDragActive(false)
  }

  function handleDrop(event) {
    event.preventDefault()
    event.stopPropagation()
    setDragActive(false)

    const file = event.dataTransfer.files?.[0]

    if (file) {
      handleFile(file)
    }
  }

  function removeFile() {
    setSelectedFile(null)
    setResult(null)
    setError('')
  }

  async function handleUpload() {
    if (!selectedFile) {
      setError('Please select an MRI image first.')
      return
    }

    if (!patientId) {
      setError(
        'No patient was selected. Please start the MRI analysis from a patient record.',
      )
      return
    }

    setError('')
    setResult(null)
    setUploading(true)

    const imagePreview = URL.createObjectURL(selectedFile)

    try {
      const patient = await getPatient(patientId)

      const formData = new FormData()

      formData.append(
        'patient_id',
        patientId,
      )

      formData.append(
        'file',
        selectedFile,
      )

      const response = await apiClient.post(
        '/predictions/predict',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        },
      )

      navigate('/results', {
        state: {
          result: response.data,
          patient,
          imagePreview,
        },
      })
    } catch (error) {
      URL.revokeObjectURL(imagePreview)

      if (error.response?.status === 401) {
        setError(
          'Your session has expired. Please log in again.',
        )
      } else if (error.response?.status === 404) {
        setError(
          error.response?.data?.detail ||
            'The selected patient could not be found.',
        )
      } else if (error.response?.status === 422) {
        setError(
          'The patient information or MRI file was not provided correctly.',
        )
      } else if (
        typeof error.response?.data?.detail === 'string'
      ) {
        setError(
          error.response.data.detail,
        )
      } else {
        setError(
          'Unable to analyze the MRI image. Please try again.',
        )
      }
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="upload-page">
      <button
        type="button"
        className="upload-back-button"
        onClick={() => {
          if (patientId) {
            navigate(`/patients/${patientId}`)
          } else {
            navigate('/dashboard')
          }
        }}
      >
        <ArrowLeft size={17} />
        Back
      </button>

      <section className="upload-header">
        <div className="upload-icon">
          <Brain size={25} />
        </div>

        <div>
          <p className="upload-eyebrow">
            MRI Analysis
          </p>

          <h1>
            Brain MRI Analysis
          </h1>

          <p>
            Upload a brain MRI image to begin AI-assisted
            tumor classification and explainability.
          </p>
        </div>
      </section>

      <section className="upload-card">
        <div className="upload-card-content">
          <div className="upload-section-heading">
            <div>
              <h2>
                Upload MRI Scan
              </h2>

              <p>
                {patientId
                  ? `Analysis for patient ID ${patientId}`
                  : 'Upload an MRI scan to begin the analysis.'}
              </p>
            </div>
          </div>

          {error && (
            <div
              className="upload-error"
              role="alert"
            >
              <X size={17} />
              <span>
                {error}
              </span>
            </div>
          )}

          {!selectedFile ? (
            <button
              type="button"
              className={`upload-dropzone ${
                dragActive
                  ? 'upload-dropzone-active'
                  : ''
              }`}
              onClick={() =>
                fileInputRef.current?.click()
              }
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              disabled={uploading}
            >
              <div className="upload-dropzone-icon">
                <UploadCloud size={30} />
              </div>

              <strong>
                {dragActive
                  ? 'Drop your MRI image here'
                  : 'Drag & drop your MRI image here'}
              </strong>

              <span>
                or click to browse from your computer
              </span>

              <small>
                Supported formats: JPG, JPEG, PNG · Maximum size: 10 MB
              </small>
            </button>
          ) : (
            <div className="upload-selected-file">
              <div className="upload-file-icon">
                <FileImage size={24} />
              </div>

              <div className="upload-file-details">
                <strong>
                  {selectedFile.name}
                </strong>

                <span>
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </span>
              </div>

              {!uploading && (
                <button
                  type="button"
                  className="upload-remove-button"
                  onClick={removeFile}
                  aria-label="Remove selected image"
                >
                  <X size={18} />
                </button>
              )}
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png,image/jpeg,image/png"
            onChange={handleFileInput}
            hidden
          />

          {selectedFile && !result && (
            <div className="upload-actions">
              <button
                type="button"
                className="upload-secondary-button"
                onClick={() =>
                  fileInputRef.current?.click()
                }
                disabled={uploading}
              >
                Choose Different Image
              </button>

              <button
                type="button"
                className="upload-primary-button"
                onClick={handleUpload}
                disabled={uploading}
              >
                {uploading ? (
                  <>
                    <LoaderCircle
                      size={17}
                      className="upload-spinner"
                    />
                    Analyzing MRI...
                  </>
                ) : (
                  <>
                    <Brain size={17} />
                    Analyze MRI
                  </>
                )}
              </button>
            </div>
          )}

          {uploading && (
            <div className="upload-processing">
              <LoaderCircle
                size={18}
                className="upload-spinner"
              />

              <div>
                <strong>
                  AI analysis in progress
                </strong>

                <span>
                  Running tumor classification and generating
                  explainability results.
                </span>
              </div>
            </div>
          )}

          {result && (
            <section className="upload-result">
              <div className="upload-result-header">
                <div className="upload-result-success">
                  <CheckCircle2 size={21} />
                </div>

                <div>
                  <h2>
                    Analysis Completed
                  </h2>

                  <p>
                    The MRI image was successfully processed by
                    the AI model.
                  </p>
                </div>
              </div>

              <div className="upload-result-grid">
                <div className="upload-result-item">
                  <span>
                    Predicted Class
                  </span>

                  <strong>
                    {result.prediction?.predicted_class ||
                      '—'}
                  </strong>
                </div>

                <div className="upload-result-item">
                  <span>
                    Confidence
                  </span>

                  <strong>
                    {result.prediction
                      ?.confidence_percent != null
                      ? `${result.prediction.confidence_percent}%`
                      : '—'}
                  </strong>
                </div>

                <div className="upload-result-item">
                  <span>
                    Model Device
                  </span>

                  <strong>
                    {result.prediction?.device ||
                      '—'}
                  </strong>
                </div>

                <div className="upload-result-item">
                  <span>
                    Feature Dimension
                  </span>

                  <strong>
                    {result.prediction
                      ?.feature_dimension ||
                      '—'}
                  </strong>
                </div>
              </div>

              {result.explainability?.explanation && (
                <div className="upload-explanation">
                  <span>
                    Explainability
                  </span>

                  <p>
                    {result.explainability.explanation}
                  </p>
                </div>
              )}

              <div className="upload-result-actions">
                <button
                  type="button"
                  className="upload-secondary-button"
                  onClick={removeFile}
                >
                  Analyze Another MRI
                </button>
              </div>
            </section>
          )}
        </div>
      </section>
    </div>
  )
}

export default Upload
