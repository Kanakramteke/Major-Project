"""
MedExplain AI - Professional Clinical PDF Generator

Generates a professional AI-assisted brain MRI report PDF
containing patient information, doctor information, AI
classification, MRI visualizations, Grad-CAM explanation,
and clinical disclaimer.
"""

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

GENERATED_REPORTS_DIR = (
    PROJECT_ROOT / "backend" / "generated_reports"
)

GENERATED_REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CONSTANTS
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4

LEFT_MARGIN = 16 * mm
RIGHT_MARGIN = 16 * mm
TOP_MARGIN = 15 * mm
BOTTOM_MARGIN = 15 * mm

TEXT_COLOR = colors.HexColor("#243047")
MUTED_COLOR = colors.HexColor("#667085")
BORDER_COLOR = colors.HexColor("#D9DEE8")
LIGHT_BACKGROUND = colors.HexColor("#F7F8FB")
SECTION_BACKGROUND = colors.HexColor("#EEF1F7")
ACCENT_COLOR = colors.HexColor("#374375")
SUCCESS_COLOR = colors.HexColor("#287D5A")
WARNING_COLOR = colors.HexColor("#9A6700")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_text(value, fallback="Not provided"):
    """
    Convert a value to displayable text.
    """
    if value is None:
        return fallback

    text = str(value).strip()

    if not text:
        return fallback

    return text


def format_prediction_class(predicted_class):
    """
    Convert database class names into report-friendly labels.
    """

    if not predicted_class:
        return "Not available"

    if predicted_class == "notumor":
        return "No Tumor Detected"

    return (
        predicted_class
        .replace("_", " ")
        .title()
    )


def format_gender(gender):
    """
    Format patient gender for display.
    """

    if not gender:
        return "Not provided"

    return str(gender).strip().title()


def format_datetime(value):
    """
    Format a datetime value for the report.
    """

    if not value:
        return "Not available"

    if isinstance(value, datetime):
        return value.strftime(
            "%d %b %Y, %I:%M %p"
        )

    return str(value)


def get_probability(probabilities, class_name):
    """
    Return a class probability as a percentage.
    """

    if not probabilities:
        return 0.0

    value = probabilities.get(
        class_name,
        0,
    )

    return float(value) * 100


def build_image_path(path_value):
    """
    Convert a stored path into a usable local Path.

    The prediction database stores absolute Windows paths.
    """

    if not path_value:
        return None

    path = Path(path_value)

    if path.exists():
        return path

    # Handle paths stored using Windows separators even
    # when accessed from another environment.
    normalized = str(path_value).replace(
        "\\",
        "/",
    )

    path = Path(normalized)

    if path.exists():
        return path

    return None


def create_report_id(report_id, created_at):
    """
    Generate a readable MedExplain report identifier.
    """

    if created_at:
        date_part = created_at.strftime(
            "%Y%m%d"
        )
    else:
        date_part = datetime.now().strftime(
            "%Y%m%d"
        )

    return (
        f"MX-{date_part}-{int(report_id):03d}"
    )


# ============================================================
# STYLES
# ============================================================

def build_styles():
    """
    Build ReportLab paragraph styles.
    """

    styles = getSampleStyleSheet()

    return {
        "header_brand": ParagraphStyle(
            "HeaderBrand",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=22,
            textColor=ACCENT_COLOR,
            alignment=TA_LEFT,
            spaceAfter=3,
        ),

        "header_title": ParagraphStyle(
            "HeaderTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            textColor=TEXT_COLOR,
            alignment=TA_LEFT,
        ),

        "header_meta": ParagraphStyle(
            "HeaderMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=10,
            textColor=MUTED_COLOR,
            alignment=TA_RIGHT,
        ),

        "section_title": ParagraphStyle(
            "SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=ACCENT_COLOR,
            spaceBefore=1,
            spaceAfter=5,
        ),

        "label": ParagraphStyle(
            "Label",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=8,
            textColor=MUTED_COLOR,
            spaceAfter=2,
        ),

        "value": ParagraphStyle(
            "Value",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=11,
            textColor=TEXT_COLOR,
        ),

        "value_bold": ParagraphStyle(
            "ValueBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=TEXT_COLOR,
        ),

        "classification": ParagraphStyle(
            "Classification",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=ACCENT_COLOR,
            alignment=TA_CENTER,
        ),

        "confidence": ParagraphStyle(
            "Confidence",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=SUCCESS_COLOR,
            alignment=TA_CENTER,
        ),

        "body": ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=13,
            textColor=TEXT_COLOR,
        ),

        "body_small": ParagraphStyle(
            "BodySmall",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=11,
            textColor=MUTED_COLOR,
        ),

        "image_label": ParagraphStyle(
            "ImageLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9,
            textColor=TEXT_COLOR,
            alignment=TA_CENTER,
        ),

        "disclaimer": ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=10.5,
            textColor=MUTED_COLOR,
        ),

        "signature": ParagraphStyle(
            "Signature",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=TEXT_COLOR,
        ),
    }


# ============================================================
# HEADER / FOOTER
# ============================================================

def draw_page_header_footer(
    canvas,
    doc,
):
    """
    Draw consistent page header and footer.
    """

    canvas.saveState()

    # Top line
    canvas.setStrokeColor(BORDER_COLOR)
    canvas.setLineWidth(0.6)

    canvas.line(
        LEFT_MARGIN,
        PAGE_HEIGHT - 11 * mm,
        PAGE_WIDTH - RIGHT_MARGIN,
        PAGE_HEIGHT - 11 * mm,
    )

    # Footer
    canvas.setFont(
        "Helvetica",
        6.8,
    )

    canvas.setFillColor(
        MUTED_COLOR
    )

    canvas.drawString(
        LEFT_MARGIN,
        8 * mm,
        "MedExplain AI - AI-assisted report. "
        "Not a substitute for clinical judgement.",
    )

    canvas.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        8 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


# ============================================================
# INFORMATION SECTION
# ============================================================

def create_information_table(
    title,
    rows,
    styles,
):
    """
    Create a two-column information section.
    """

    content = []

    for label, value in rows:
        content.append(
            [
                Paragraph(
                    str(label).upper(),
                    styles["label"],
                ),
                Paragraph(
                    safe_text(value),
                    styles["value"],
                ),
            ]
        )

    table = Table(
        content,
        colWidths=[
            34 * mm,
            137 * mm,
        ],
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_BACKGROUND,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    BORDER_COLOR,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    BORDER_COLOR,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    return [
        Paragraph(
            title.upper(),
            styles["section_title"],
        ),
        table,
        Spacer(1, 5 * mm),
    ]


# ============================================================
# IMAGE SECTION
# ============================================================

def create_visualization_card(
    label,
    image_path,
    styles,
):
    """
    Create one MRI/Grad-CAM image card.
    """

    if image_path is None:
        image_content = Paragraph(
            "Visualization unavailable",
            styles["body_small"],
        )
    else:
        try:
            image = Image(
                str(image_path),
                width=50 * mm,
                height=47 * mm,
                kind="proportional",
            )

            image_content = image

        except Exception:
            image_content = Paragraph(
                "Unable to load visualization",
                styles["body_small"],
            )

    table = Table(
        [
            [
                Paragraph(
                    label,
                    styles["image_label"],
                )
            ],
            [image_content],
        ],
        colWidths=[55 * mm],
        rowHeights=[8 * mm, 49 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    BORDER_COLOR,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    SECTION_BACKGROUND,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    return table


# ============================================================
# MAIN PDF GENERATOR
# ============================================================

def generate_clinical_report_pdf(
    report_id,
    prediction,
    patient,
    doctor,
    output_path=None,
):
    """
    Generate a professional MedExplain AI clinical report PDF.

    Parameters
    ----------
    report_id:
        Database report ID.

    prediction:
        Prediction SQLAlchemy object.

    patient:
        Patient SQLAlchemy object.

    doctor:
        Doctor SQLAlchemy object.

    output_path:
        Optional custom PDF path.

    Returns
    -------
    Path
        Path to the generated PDF.
    """

    if output_path is None:
        filename = (
            f"report_{report_id}_"
            f"prediction_{prediction.id}.pdf"
        )

        output_path = (
            GENERATED_REPORTS_DIR / filename
        )

    else:
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    output_path = Path(output_path)

    styles = build_styles()

    report_identifier = create_report_id(
        report_id=report_id,
        created_at=prediction.created_at,
    )

    predicted_label = format_prediction_class(
        prediction.predicted_class
    )

    confidence = float(
        prediction.confidence_percent or 0
    )

    probabilities = (
        prediction.class_probabilities
        or {}
    )

    # --------------------------------------------------------
    # Stored visualization paths
    # --------------------------------------------------------

    original_path = build_image_path(
        prediction.image_path
    )

    overlay_path = build_image_path(
        prediction.overlay_visualization_path
    )

    heatmap_path = build_image_path(
        prediction.heatmap_visualization_path
    )

    # --------------------------------------------------------
    # Document
    # --------------------------------------------------------

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=18 * mm,
        bottomMargin=BOTTOM_MARGIN,
        title=(
            f"MedExplain AI - "
            f"{patient.patient_id}"
        ),
        author="MedExplain AI",
        subject="Brain Tumor MRI Analysis Report",
    )

    story = []

    # ========================================================
    # HEADER
    # ========================================================

    header_left = [
        Paragraph(
            "MedExplain AI",
            styles["header_brand"],
        ),
        Paragraph(
            "Brain Tumor MRI Analysis Report",
            styles["header_title"],
        ),
    ]

    header_right = [
        Paragraph(
            f"Generated: "
            f"{format_datetime(datetime.now())}",
            styles["header_meta"],
        ),
        Paragraph(
            f"Report ID: {report_identifier}",
            styles["header_meta"],
        ),
    ]

    header_table = Table(
        [
            [
                header_left,
                header_right,
            ]
        ],
        colWidths=[
            100 * mm,
            71 * mm,
        ],
    )

    header_table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, 0),
                    "RIGHT",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    story.append(header_table)

    story.append(
        Spacer(1, 4 * mm)
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=ACCENT_COLOR,
        )
    )

    story.append(
        Spacer(1, 5 * mm)
    )

    # ========================================================
    # PATIENT DETAILS
    # ========================================================

    patient_rows = [
        (
            "Patient Name",
            patient.full_name,
        ),
        (
            "Patient ID",
            patient.patient_id,
        ),
        (
            "Age",
            f"{patient.age} years",
        ),
        (
            "Gender",
            format_gender(patient.gender),
        ),
        (
            "Contact No.",
            patient.contact,
        ),
        (
            "Medical History",
            patient.medical_history,
        ),
    ]

    story.extend(
        create_information_table(
            "Patient Details",
            patient_rows,
            styles,
        )
    )

    # ========================================================
    # DOCTOR DETAILS
    # ========================================================

    doctor_rows = [
        (
            "Doctor Name",
            doctor.full_name,
        ),
        (
            "Doctor ID",
            f"DOC-{doctor.id:04d}",
        ),
        (
            "Email",
            doctor.email,
        ),
        (
            "Specialization",
            doctor.specialization,
        ),
    ]

    story.extend(
        create_information_table(
            "Doctor Details",
            doctor_rows,
            styles,
        )
    )

    # ========================================================
    # AI CLASSIFICATION
    # ========================================================

    classification_data = [
        [
            Paragraph(
                "TUMOR CLASSIFICATION",
                styles["label"],
            ),
            Paragraph(
                "CONFIDENCE",
                styles["label"],
            ),
        ],
        [
            Paragraph(
                predicted_label,
                styles["classification"],
            ),
            Paragraph(
                f"{confidence:.2f}%",
                styles["confidence"],
            ),
        ],
    ]

    classification_table = Table(
        classification_data,
        colWidths=[
            110 * mm,
            61 * mm,
        ],
        rowHeights=[
            8 * mm,
            18 * mm,
        ],
    )

    classification_table.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    BORDER_COLOR,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    BORDER_COLOR,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    SECTION_BACKGROUND,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    story.append(
        Paragraph(
            "AI CLASSIFICATION",
            styles["section_title"],
        )
    )

    story.append(
        classification_table
    )

    story.append(
        Spacer(1, 5 * mm)
    )

    # ========================================================
    # MRI ANALYSIS DETAILS
    # ========================================================

    analysis_rows = [
        (
            "Original MRI",
            prediction.original_filename,
        ),
        (
            "Analysis Date",
            format_datetime(
                prediction.created_at
            ),
        ),
        (
            "Model Device",
            str(
                prediction.device
                or "Unknown"
            ).upper(),
        ),
        (
            "Feature Vector",
            f"{prediction.feature_dimension} dimensions",
        ),
    ]

    story.extend(
        create_information_table(
            "MRI Analysis",
            analysis_rows,
            styles,
        )
    )

    # ========================================================
    # VISUAL EXPLANATION
    # ========================================================

    story.append(
        Paragraph(
            "IMAGING & VISUAL EXPLANATION",
            styles["section_title"],
        )
    )

    visualizations = Table(
        [
            [
                create_visualization_card(
                    "ORIGINAL MRI",
                    original_path,
                    styles,
                ),
                create_visualization_card(
                    "GRAD-CAM OVERLAY",
                    overlay_path,
                    styles,
                ),
                create_visualization_card(
                    "HEATMAP",
                    heatmap_path,
                    styles,
                ),
            ]
        ],
        colWidths=[
            57 * mm,
            57 * mm,
            57 * mm,
        ],
    )

    visualizations.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    story.append(
        visualizations
    )

    story.append(
        Spacer(1, 5 * mm)
    )

    # ========================================================
    # EXPLANATION
    # ========================================================

    explanation = safe_text(
        prediction.explanation,
        "No explainability information was saved.",
    )

    explanation_text = (
        f"<b>The model classified the MRI scan as "
        f"{predicted_label} with "
        f"{confidence:.2f}% confidence.</b><br/><br/>"
        f"{explanation}<br/><br/>"
        "The Grad-CAM visualization highlights image "
        "regions that contributed to the model's "
        "prediction. These highlighted regions represent "
        "model attention and should not be interpreted "
        "as an exact tumor boundary or segmentation result."
    )

    story.append(
        Paragraph(
            "EXPLANATION",
            styles["section_title"],
        )
    )

    explanation_table = Table(
        [
            [
                Paragraph(
                    explanation_text,
                    styles["body"],
                )
            ]
        ],
        colWidths=[171 * mm],
    )

    explanation_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_BACKGROUND,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    BORDER_COLOR,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(
        explanation_table
    )

    story.append(
        Spacer(1, 5 * mm)
    )

    # ========================================================
    # CLASS PROBABILITIES
    # ========================================================

    story.append(
        Paragraph(
            "CLASS PROBABILITIES",
            styles["section_title"],
        )
    )

    probability_rows = [
        [
            Paragraph(
                "CLASS",
                styles["label"],
            ),
            Paragraph(
                "PROBABILITY",
                styles["label"],
            ),
        ],
        [
            Paragraph(
                "Glioma",
                styles["value"],
            ),
            Paragraph(
                f"{get_probability(probabilities, 'glioma'):.2f}%",
                styles["value_bold"],
            ),
        ],
        [
            Paragraph(
                "Meningioma",
                styles["value"],
            ),
            Paragraph(
                f"{get_probability(probabilities, 'meningioma'):.2f}%",
                styles["value_bold"],
            ),
        ],
        [
            Paragraph(
                "Pituitary",
                styles["value"],
            ),
            Paragraph(
                f"{get_probability(probabilities, 'pituitary'):.2f}%",
                styles["value_bold"],
            ),
        ],
        [
            Paragraph(
                "No Tumor",
                styles["value"],
            ),
            Paragraph(
                f"{get_probability(probabilities, 'notumor'):.2f}%",
                styles["value_bold"],
            ),
        ],
    ]

    probability_table = Table(
        probability_rows,
        colWidths=[
            130 * mm,
            41 * mm,
        ],
    )

    probability_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    SECTION_BACKGROUND,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    BORDER_COLOR,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    BORDER_COLOR,
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(
        probability_table
    )

    story.append(
        Spacer(1, 7 * mm)
    )

    # ========================================================
    # SIGNATURE
    # ========================================================

    signature_data = [
        [
            Paragraph(
                "Reviewed / Generated For",
                styles["label"],
            )
        ],
        [
            Paragraph(
                safe_text(
                    doctor.full_name,
                    "Doctor",
                ),
                styles["signature"],
            )
        ],
        [
            Paragraph(
                f"ID: DOC-{doctor.id:04d}",
                styles["body_small"],
            )
        ],
    ]

    signature_table = Table(
        signature_data,
        colWidths=[80 * mm],
    )

    signature_table.setStyle(
        TableStyle(
            [
                (
                    "LINEABOVE",
                    (0, 0),
                    (0, 0),
                    0.7,
                    BORDER_COLOR,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
            ]
        )
    )

    story.append(
        signature_table
    )

    story.append(
        Spacer(1, 5 * mm)
    )

    # ========================================================
    # DISCLAIMER
    # ========================================================

    disclaimer_text = (
        "<b>Disclaimer:</b> This report is generated "
        "with AI assistance to support, not replace, "
        "the judgement of a qualified medical professional. "
        "Findings must be confirmed through clinical "
        "evaluation and further diagnostic testing."
    )

    disclaimer_table = Table(
        [
            [
                Paragraph(
                    disclaimer_text,
                    styles["disclaimer"],
                )
            ]
        ],
        colWidths=[171 * mm],
    )

    disclaimer_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#FFF9E8"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#E8D9A7"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(
        disclaimer_table
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story,
        onFirstPage=draw_page_header_footer,
        onLaterPages=draw_page_header_footer,
    )

    return output_path