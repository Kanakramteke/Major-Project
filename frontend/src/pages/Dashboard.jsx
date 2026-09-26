import {
  Activity,
  Brain,
  FileText,
  Plus,
  ShieldCheck,
  Users,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import './Dashboard.css'

function Dashboard() {
  const navigate = useNavigate()

  const statistics = [
    {
      label: 'Total Patients',
      value: '0',
      icon: Users,
    },
    {
      label: 'MRI Analyses',
      value: '0',
      icon: Brain,
    },
    {
      label: 'Reports Generated',
      value: '0',
      icon: FileText,
    },
  ]

  return (
    <div className="dashboard-page">
      <section className="dashboard-welcome">
        <div>
          <p className="dashboard-eyebrow">Clinical workspace</p>

          <h1>Welcome to MedExplain AI</h1>

          <p>
            Analyze brain MRI scans, understand AI predictions,
            and generate structured clinical reports from one
            workspace.
          </p>
        </div>

        <button
          type="button"
          className="dashboard-primary-button"
          onClick={() => navigate('/upload')}
        >
          <Plus size={18} />
          New MRI Analysis
        </button>
      </section>

      <section className="dashboard-statistics">
        {statistics.map((statistic) => {
          const Icon = statistic.icon

          return (
            <article
              className="dashboard-stat-card"
              key={statistic.label}
            >
              <div className="dashboard-stat-icon">
                <Icon size={20} />
              </div>

              <div>
                <span>{statistic.label}</span>
                <strong>{statistic.value}</strong>
              </div>
            </article>
          )
        })}
      </section>

      <section className="dashboard-grid">
        <article className="dashboard-analysis-card">
          <div className="dashboard-card-heading">
            <div>
              <p className="dashboard-card-eyebrow">
                MRI Analysis
              </p>

              <h2>Start a new analysis</h2>
            </div>

            <div className="dashboard-card-icon">
              <Brain size={22} />
            </div>
          </div>

          <p>
            Upload a brain MRI image to receive a four-class
            tumor prediction, confidence scores, and a combined
            Grad-CAM explanation.
          </p>

          <button
            type="button"
            className="dashboard-secondary-button"
            onClick={() => navigate('/upload')}
          >
            Analyze MRI
          </button>
        </article>

        <article className="dashboard-info-card">
          <div className="dashboard-card-heading">
            <div>
              <p className="dashboard-card-eyebrow">
                Explainability
              </p>

              <h2>Understand the prediction</h2>
            </div>

            <div className="dashboard-card-icon">
              <ShieldCheck size={22} />
            </div>
          </div>

          <p>
            MedExplain AI combines multiple deep learning
            backbones through feature-level fusion and uses
            Grad-CAM to highlight image regions that influenced
            the prediction.
          </p>

          <div className="dashboard-model-status">
            <Activity size={16} />
            <span>Fusion model ready</span>
          </div>
        </article>
      </section>

      <section className="dashboard-recent">
        <div className="dashboard-section-heading">
          <div>
            <p className="dashboard-card-eyebrow">Activity</p>
            <h2>Recent analyses</h2>
          </div>

          <button
            type="button"
            className="dashboard-text-button"
            onClick={() => navigate('/history')}
          >
            View history
          </button>
        </div>

        <div className="dashboard-empty-state">
          <div className="dashboard-empty-icon">
            <FileText size={22} />
          </div>

          <h3>No analyses yet</h3>

          <p>
            Your recent MRI analyses will appear here after you
            complete your first prediction.
          </p>

          <button
            type="button"
            className="dashboard-secondary-button"
            onClick={() => navigate('/upload')}
          >
            Start your first analysis
          </button>
        </div>
      </section>
    </div>
  )
}

export default Dashboard