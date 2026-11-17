import os
import requests
import streamlit as st
from PIL import Image

# -----------------------------------------------------------------------------
# 1. Configuration & Backend Connection
# -----------------------------------------------------------------------------
# os.getenv allows dynamic backend URL configuration without modifying code
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# layout="wide" enables the dual-column layout (Input on left, Results on right)
st.set_page_config(
    page_title="Potato Leaf Disease Classifier",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# 2. Custom Styling (CSS Injection)
# -----------------------------------------------------------------------------
# We style Streamlit's native `st.container(border=True)` wrapper directly.
# This prevents empty floating tags and ensures all widgets stay INSIDE the card.
st.markdown(
    """
    <style>
    /* Global warm ivory background */
    .stApp {
        background-color: #F8F6F0;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        color: #2D3748;
    }

    /* Reduce default top padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Header styling */
    .header-container {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 0.4rem;
    }
    .header-icon {
        font-size: 2.2rem;
        background: #E8F5E9;
        border-radius: 12px;
        padding: 6px 10px;
        border: 1px solid #C8E6C9;
    }
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1A3026;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.8rem;
    }

    /* CARD CONTAINER FIX:
       We style Streamlit's native bordered containers directly.
       This wraps all widgets, inputs, and images cleanly inside the card. */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E8E2D9 !important;
        border-radius: 16px !important;
        padding: 1.25rem !important;
        box-shadow: 0 4px 16px rgba(140, 109, 83, 0.05) !important;
        margin-bottom: 1.2rem !important;
    }

    /* Card header titles */
    .card-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 0.8rem;
    }

    /* Drop-zone style for the file uploader */
    [data-testid="stFileUploader"] {
        background-color: #FAF8F5;
        border: 2px dashed #D6CCC2;
        border-radius: 12px;
        padding: 0.6rem;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #16A34A;
    }

    /* Diagnosis badges */
    .badge-healthy {
        background-color: #ECFDF5;
        color: #15803D;
        border: 1px solid #A7F3D0;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .badge-blight {
        background-color: #FEF3C7;
        color: #B45309;
        border: 1px solid #FDE68A;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .badge-confused {
        background-color: #F1F5F9;
        color: #475569;
        border: 1px solid #CBD5E1;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Circular gauge container */
    .gauge-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    /* Custom horizontal probability bars */
    .prob-row {
        margin-bottom: 0.85rem;
    }
    .prob-label-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.92rem;
        font-weight: 500;
        color: #334155;
        margin-bottom: 0.35rem;
    }
    .prob-track {
        background: #F1ECE6;
        height: 10px;
        border-radius: 9999px;
        overflow: hidden;
    }
    .prob-fill {
        height: 100%;
        border-radius: 9999px;
    }

    /* Agronomy recommendation callout box */
    .rec-box {
        background-color: #FAF8F5;
        border-left: 4px solid #16A34A;
        border-radius: 0 12px 12px 0;
        padding: 1rem;
        font-size: 0.93rem;
        line-height: 1.5;
        color: #4A5568;
    }
    .rec-box-blight {
        border-left-color: #8C6D53;
    }
    .rec-box-confused {
        border-left-color: #CBD5E1;
    }

    /* Rounded corner styling for the image */
    [data-testid="stImage"] img {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 3. Header
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-container">
        <div class="header-icon">🌱</div>
        <h1 class="header-title">Potato Leaf Disease Classifier</h1>
    </div>
    <div class="header-subtitle">
        Upload a potato leaf photo to inspect and predict disease conditions.
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 4. Main Two-Column Layout
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([5, 7], gap="large")

with col_left:
    # Card 1: File Uploader
    with st.container(border=True):
        st.markdown('<div class="card-title">Upload Leaf Image</div>', unsafe_allow_html=True)
        file = st.file_uploader(
            "Choose a potato leaf image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )

    # Card 2: Uploaded Leaf Photo (Appears only after file selection)
    if file is not None:
        with st.container(border=True):
            st.markdown('<div class="card-title">Inspected Leaf Photo</div>', unsafe_allow_html=True)
            image = Image.open(file)
            st.image(image, use_container_width=True)

with col_right:
    # State A: Empty state before an image is selected
    if file is None:
        with st.container(border=True):
            st.markdown(
                """
                <div style="text-align: center; padding: 3rem 1.5rem;">
                    <div style="font-size: 3rem; margin-bottom: 0.8rem;">📸</div>
                    <div style="font-size: 1.15rem; font-weight: 600; color: #1E293B; margin-bottom: 0.4rem;">
                        Awaiting Leaf Sample
                    </div>
                    <div style="color: #64748B; font-size: 0.95rem; max-width: 380px; margin: 0 auto;">
                        Select or drag-and-drop a photo of a potato leaf on the left panel to run disease classification.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # State B: Process image & display diagnostics
    else:
        with st.spinner("Analyzing leaf with CNN..."):
            try:
                resp = requests.post(
                    f"{API_URL}/predict",
                    files={"file": (file.name, file.getvalue(), file.type)},
                    timeout=30,
                )
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the backend. Is `uvicorn` running on port 8000?")
                st.stop()

        if resp.status_code != 200:
            st.error(resp.json().get("detail", "Prediction service returned an error."))
            st.stop()

        result = resp.json()
        label = result["label"]
        score = float(result["score"])
        score_pct = score * 100
        probabilities = result.get("probabilities", {})

        is_confused = score < 0.70
        is_healthy = "healthy" in label.lower()

        # ---------------------------------------------------------------------
        # Card 3: Model Diagnosis & Circular Confidence Ring
        # ---------------------------------------------------------------------
        with st.container(border=True):
            if is_confused:
                badge_html = f'<div class="badge-confused">⚠️ Inconclusive ({label})</div>'
                ring_color = "#94A3B8"
            elif is_healthy:
                badge_html = f'<div class="badge-healthy">✓ Diagnosis: {label}</div>'
                ring_color = "#16A34A"
            else:
                badge_html = f'<div class="badge-blight">⚠️ Diagnosis: {label}</div>'
                ring_color = "#8C6D53"

            diag_col1, diag_col2 = st.columns([1.5, 1])
            with diag_col1:
                st.markdown('<div class="card-title">Model Diagnosis</div>', unsafe_allow_html=True)
                st.markdown(badge_html, unsafe_allow_html=True)
                st.markdown(
                    """
                    <div style="color: #64748B; font-size: 0.88rem; margin-top: 0.8rem;">
                        Top classification based on trained convolutional feature extraction.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with diag_col2:
                # Conic-gradient confidence ring
                st.markdown(
                    f"""
                    <div class="gauge-wrapper">
                        <div style="
                            width: 98px;
                            height: 98px;
                            border-radius: 50%;
                            background: conic-gradient({ring_color} {score_pct:.1f}%, #E8E2D9 0%);
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                        ">
                            <div style="
                                width: 76px;
                                height: 76px;
                                border-radius: 50%;
                                background: #FFFFFF;
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                justify-content: center;
                            ">
                                <span style="font-weight: 700; font-size: 1.05rem; color: #1E293B;">{score_pct:.1f}%</span>
                                <span style="font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.5px; color: #64748B;">Confidence</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ---------------------------------------------------------------------
        # Card 4: Class Probabilities
        # ---------------------------------------------------------------------
        with st.container(border=True):
            st.markdown('<div class="card-title">Class Probabilities</div>', unsafe_allow_html=True)

            # Build all progress bars into one HTML string so it renders in a single block
            bars_html = ""
            for class_name, p in probabilities.items():
                prob_val = float(p) * 100
                if "healthy" in class_name.lower():
                    bar_color = "#16A34A"  # Botanical green
                elif "late" in class_name.lower():
                    bar_color = "#8C6D53"  # Earthy brown
                else:
                    bar_color = "#D97706"  # Warm amber

                bars_html += f"""
                <div class="prob-row">
                    <div class="prob-label-row">
                        <span>{class_name}</span>
                        <span style="font-weight: 600;">{prob_val:.2f}%</span>
                    </div>
                    <div class="prob-track">
                        <div class="prob-fill" style="width: {prob_val}%; background-color: {bar_color};"></div>
                    </div>
                </div>
                """
            st.markdown(bars_html, unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # Card 5: Agronomy Recommendations (Hardcoded if/elif/else)
        # ---------------------------------------------------------------------
        if is_confused:
            rec_title = "⚠️ Inconclusive / Confused Prediction"
            rec_class = "rec-box rec-box-confused"
            rec_message = (
                "The model is confused and cannot reliably classify the given image. "
                "The leaf may be out of focus, poorly lit, obscured, or not a potato leaf. "
                "Please upload a clearer, well-lit photo of a single potato leaf."
            )
        elif is_healthy:
            rec_title = "🌿 Healthy Crop Status"
            rec_class = "rec-box"
            rec_message = (
                "The leaf exhibits strong cellular vigor and optimal chlorophyll distribution with no foliar lesions detected. "
                "Maintain standard drip irrigation and balanced fertilization schedules, and continue routine field scouting."
            )
        else:
            rec_title = f"🍂 Blight Management ({label})"
            rec_class = "rec-box rec-box-blight"
            rec_message = (
                f"Foliar symptoms consistent with {label} detected. Inspect neighboring potato plants for water-soaked "
                "or dark necrotic rings. Consider targeted copper or systemic fungicide application, avoid overhead watering, "
                "and ensure adequate air circulation between rows."
            )

        with st.container(border=True):
            st.markdown('<div class="card-title">Agronomy Recommendations</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="{rec_class}">
                    <div style="font-weight: 600; color: #1E293B; margin-bottom: 0.35rem;">{rec_title}</div>
                    <div>{rec_message}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )