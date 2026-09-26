"""
MedExplain AI - FastAPI Application

Main entry point for the MedExplain AI backend.
"""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


# ============================================================
# Project Path
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# Storage Directories
# ============================================================

GENERATED_GRADCAM_DIR = (
    PROJECT_ROOT / "backend" / "generated_gradcam"
)

GENERATED_GRADCAM_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


UPLOADS_DIR = (
    PROJECT_ROOT / "backend" / "uploads"
)

UPLOADS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


GENERATED_REPORTS_DIR = (
    PROJECT_ROOT / "backend" / "generated_reports"
)

GENERATED_REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# API Router
# ============================================================

from app.api.router import api_router


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="MedExplain AI",
    description=(
        "Explainable AI system for brain tumor diagnosis "
        "using feature-level deep learning fusion."
    ),
    version="1.0.0",
)


# ============================================================
# CORS Configuration
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Static File Routes
# ============================================================

# Uploaded MRI images
app.mount(
    "/uploads",
    StaticFiles(
        directory=str(UPLOADS_DIR)
    ),
    name="uploads",
)


# Generated Grad-CAM visualizations
app.mount(
    "/generated-gradcam",
    StaticFiles(
        directory=str(GENERATED_GRADCAM_DIR)
    ),
    name="generated_gradcam",
)


# Generated clinical PDF reports
app.mount(
    "/generated-reports",
    StaticFiles(
        directory=str(GENERATED_REPORTS_DIR)
    ),
    name="generated_reports",
)


# ============================================================
# API Routes
# ============================================================

app.include_router(
    api_router,
    prefix="/api",
)


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    return {
        "success": True,
        "message": "MedExplain AI API is running.",
    }


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
        "service": "MedExplain AI",
    }