import { ArrowRight, Brain, FileText, ScanSearch, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'
import './Home.css'

function Home() {
  return (
    <main className="home-page">
      <nav className="home-navbar">
        <Link to="/" className="brand">
          <div className="brand-icon">
            <Brain size={24} strokeWidth={2} />
          </div>

          <div className="brand-text">
            <span className="brand-name">MedExplain AI</span>
            <span className="brand-tagline">Explainable Brain MRI Analysis</span>
          </div>
        </Link>

        <div className="nav-actions">
          <Link to="/login" className="nav-login">
            Doctor Login
          </Link>

          <Link to="/register" className="nav-register">
            Get Started
            <ArrowRight size={17} />
          </Link>
        </div>
      </nav>

      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <ShieldCheck size={16} />
            <span>AI-assisted clinical decision support</span>
          </div>

          <h1>
            Understand brain MRI
            <span> beyond the prediction.</span>
          </h1>

          <p className="hero-description">
            MedExplain AI combines deep learning-based brain tumor
            classification with visual explanations and automated clinical
            reporting to help doctors understand what influenced an AI
            prediction.
          </p>

          <div className="hero-actions">
            <Link to="/register" className="primary-button">
              Start Analysis
              <ArrowRight size={18} />
            </Link>

            <a href="#how-it-works" className="secondary-button">
              See How It Works
            </a>
          </div>

          <div className="hero-note">
            <span className="status-dot" />
            <span>Four-class brain MRI classification</span>
          </div>
        </div>

        <div className="hero-visual">
          <div className="scan-card">
            <div className="scan-header">
              <div>
                <span className="scan-label">MRI ANALYSIS</span>
                <span className="scan-id">MED-EXPLAIN / AI</span>
              </div>

              <div className="scan-status">
                <span className="status-dot" />
                Ready
              </div>
            </div>

            <div className="brain-visual">
              <div className="brain-ring ring-one" />
              <div className="brain-ring ring-two" />
              <div className="brain-core">
                <Brain size={100} strokeWidth={0.8} />
              </div>

              <div className="scan-crosshair horizontal" />
              <div className="scan-crosshair vertical" />

              <div className="scan-point point-one" />
              <div className="scan-point point-two" />
              <div className="scan-point point-three" />
            </div>

            <div className="scan-footer">
              <div>
                <span className="footer-label">MODEL</span>
                <strong>Fusion Network</strong>
              </div>

              <div>
                <span className="footer-label">XAI</span>
                <strong>Grad-CAM</strong>
              </div>

              <div>
                <span className="footer-label">CLASSES</span>
                <strong>04</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="feature-section" id="how-it-works">
        <div className="section-heading">
          <span>THE WORKFLOW</span>
          <h2>From MRI image to explainable insight.</h2>
          <p>
            A unified workflow designed around prediction, interpretation,
            and clinical reporting.
          </p>
        </div>

        <div className="feature-grid">
          <article className="feature-card">
            <div className="feature-icon">
              <ScanSearch size={23} />
            </div>

            <span className="feature-number">01</span>

            <h3>AI Diagnosis</h3>

            <p>
              Analyze a brain MRI using a feature-level fusion model built
              from multiple deep learning architectures.
            </p>
          </article>

          <article className="feature-card">
            <div className="feature-icon">
              <Brain size={23} />
            </div>

            <span className="feature-number">02</span>

            <h3>Visual Explanation</h3>

            <p>
              Generate a combined Grad-CAM visualization showing the image
              regions that influenced the model's prediction.
            </p>
          </article>

          <article className="feature-card">
            <div className="feature-icon">
              <FileText size={23} />
            </div>

            <span className="feature-number">03</span>

            <h3>Clinical Report</h3>

            <p>
              Transform the prediction and explainability information into
              a structured clinical report for review.
            </p>
          </article>
        </div>
      </section>

      <footer className="home-footer">
        <div>
          <strong>MedExplain AI</strong>
          <span>Explainable AI for Brain Tumor Diagnosis</span>
        </div>

        <span>AI-assisted analysis · For clinical review</span>
      </footer>
    </main>
  )
}

export default Home