
import streamlit as st
import plotly.express as px
import pandas as pd
from PIL import Image
from html import escape

from data_loader import load_metadata, find_image


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="DermaScan | Skin Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

is_dark = st.get_option("theme.base") == "dark"

# =========================================================
# DISEASE INFORMATION
# =========================================================

DISEASE_NAMES = {
    "akiec": "Actinic Keratoses",
    "bcc": "Basal Cell Carcinoma",
    "bkl": "Benign Keratosis-like Lesions",
    "df": "Dermatofibroma",
    "mel": "Melanoma",
    "nv": "Melanocytic Nevi",
    "vasc": "Vascular Lesions"
}

DISEASE_COLORS = {
    "akiec": "#8B9FE8",
    "bcc": "#E69A83",
    "bkl": "#E8BD70",
    "df": "#77B9A5",
    "mel": "#D87991",
    "nv": "#4E9CCB",
    "vasc": "#A58ACD"
}


# =========================================================
# GLOBAL STYLING
# =========================================================

st.html("""
<style>
    .stApp {
        background:
            radial-gradient(ellipse at 10% 0%, rgba(45, 116, 230, 0.07), transparent 32%),
            var(--background-color);
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(120, 150, 190, 0.16);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    [data-testid="stMetric"] {
        display: none;
    }

    div[data-testid="stRadio"] label {
        padding: 8px 12px;
        border-radius: 10px;
    }

    div[data-testid="stFileUploader"] {
        border-radius: 16px;
    }

    .brand-area {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 0 22px 0;
    }

    .brand-icon {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #2563EB, #38BDF8);
        color: white;
        font-size: 23px;
        box-shadow: 0 7px 20px rgba(37, 99, 235, .25);
    }

    .brand-name {
        font-size: 21px;
        font-weight: 800;
        letter-spacing: -0.7px;
        color: var(--text-color);
    }

    .brand-subtitle {
        font-size: 9px;
        letter-spacing: 1.8px;
        color: #6B9BE8;
        font-weight: 800;
        margin-top: 2px;
    }

    .sidebar-caption {
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.6px;
        color: #8B9BB3;
        margin: 12px 0 10px 0;
    }

    .sidebar-status {
        margin-top: 25px;
        padding: 15px;
        border-radius: 15px;
        background: linear-gradient(135deg, rgba(37,99,235,.12), rgba(56,189,248,.06));
        border: 1px solid rgba(59,130,246,.22);
    }

    .sidebar-status-title {
        font-size: 12px;
        font-weight: 750;
        margin-bottom: 5px;
        color: var(--text-color);
    }

    .sidebar-status-text {
        font-size: 11px;
        color: var(--text-color);
        opacity: .65;
        line-height: 1.5;
    }

    .sidebar-footer {
        font-size: 10px;
        color: #8B9BB3;
        margin-top: 25px;
        line-height: 1.7;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 35px 38px;
        border-radius: 25px;
        color: white;
        background: linear-gradient(115deg, #102B59 0%, #1557B8 52%, #168FCB 100%);
        box-shadow: 0 15px 38px rgba(21, 87, 184, .20);
        margin-bottom: 25px;
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 330px;
        height: 330px;
        right: -80px;
        top: -170px;
        border-radius: 50%;
        border: 1px solid rgba(255,255,255,.15);
        box-shadow:
            0 0 0 35px rgba(255,255,255,.035),
            0 0 0 75px rgba(255,255,255,.025);
    }

    .hero-tag {
        display: inline-block;
        padding: 6px 11px;
        border-radius: 30px;
        background: rgba(255,255,255,.13);
        border: 1px solid rgba(255,255,255,.22);
        color: #D9EDFF;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-bottom: 17px;
    }

    .hero-title {
        font-size: clamp(27px, 3.2vw, 40px);
        font-weight: 850;
        letter-spacing: -1.4px;
        line-height: 1.15;
        margin: 0 0 12px 0;
        color: white;
    }

    .hero-description {
        color: #D8E9FF;
        font-size: 13px;
        line-height: 1.8;
        max-width: 600px;
        margin: 0;
    }

    .hero-bottom {
        display: flex;
        align-items: center;
        gap: 9px;
        margin-top: 23px;
        font-size: 11px;
        color: #E3F2FF;
    }

    .live-dot {
        width: 8px;
        height: 8px;
        background: #55E6B1;
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(85,230,177,.7);
    }

    .section-heading {
        font-size: 18px;
        font-weight: 800;
        letter-spacing: -.5px;
        color: var(--text-color);
        margin: 8px 0 4px 0;
    }

    .section-description {
        font-size: 11px;
        color: var(--text-color);
        opacity: .58;
        margin-bottom: 17px;
    }

    .metric-card {
        position: relative;
        overflow: hidden;
        padding: 21px;
        min-height: 145px;
        border-radius: 19px;
        background: var(--secondary-background-color);
        border: 1px solid rgba(120,150,190,.17);
        box-shadow: 0 5px 18px rgba(20,50,90,.045);
    }

    .metric-card:before {
        content: "";
        position: absolute;
        height: 3px;
        top: 0;
        left: 0;
        right: 0;
        background: var(--accent);
    }

    .metric-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .metric-label {
        font-size: 11px;
        font-weight: 700;
        color: var(--text-color);
        opacity: .62;
    }

    .metric-icon {
        width: 36px;
        height: 36px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--icon-bg);
        font-size: 17px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 850;
        letter-spacing: -1px;
        color: var(--text-color);
        margin-top: 13px;
        line-height: 1.1;
    }

    .metric-description {
        font-size: 10px;
        color: var(--text-color);
        opacity: .53;
        margin-top: 7px;
    }

    .panel {
        background: var(--secondary-background-color);
        border: 1px solid rgba(120,150,190,.17);
        border-radius: 19px;
        padding: 20px;
        box-shadow: 0 5px 18px rgba(20,50,90,.035);
    }

    .panel-title {
        font-size: 15px;
        font-weight: 800;
        color: var(--text-color);
        margin-bottom: 4px;
    }

    .panel-subtitle {
        font-size: 10px;
        color: var(--text-color);
        opacity: .55;
        margin-bottom: 17px;
    }

    .category-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 13px 0;
    }

    .category-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .category-info {
        flex: 1;
        min-width: 0;
    }

    .category-name {
        font-size: 11px;
        font-weight: 700;
        color: var(--text-color);
    }

    .category-code {
        font-size: 9px;
        color: var(--text-color);
        opacity: .48;
        margin-top: 2px;
    }

    .category-number {
        font-size: 12px;
        font-weight: 800;
        color: var(--text-color);
        text-align: right;
    }

    .category-percent {
        font-size: 9px;
        color: var(--text-color);
        opacity: .55;
        text-align: right;
        margin-top: 2px;
    }

    .progress-track {
        height: 5px;
        border-radius: 10px;
        background: rgba(130,150,180,.16);
        margin-top: 7px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        border-radius: 10px;
    }

    .model-panel {
        border-radius: 20px;
        padding: 22px;
        background: linear-gradient(120deg, rgba(37,99,235,.13), rgba(56,189,248,.07));
        border: 1px solid rgba(59,130,246,.22);
    }

    .model-heading {
        font-size: 15px;
        font-weight: 800;
        color: var(--text-color);
    }

    .model-copy {
        font-size: 11px;
        line-height: 1.7;
        color: var(--text-color);
        opacity: .68;
        margin-top: 7px;
    }

    .model-badge {
        display: inline-block;
        font-size: 9px;
        font-weight: 800;
        letter-spacing: .8px;
        padding: 6px 10px;
        border-radius: 20px;
        color: #2563EB;
        background: rgba(59,130,246,.13);
        margin-bottom: 12px;
    }

    .page-eyebrow {
        color: #4388E8;
        font-size: 10px;
        font-weight: 850;
        letter-spacing: 1.7px;
        margin-bottom: 7px;
    }

    .page-title {
        font-size: 30px;
        font-weight: 850;
        letter-spacing: -1px;
        color: var(--text-color);
        margin: 0 0 7px 0;
    }

    .page-description {
        font-size: 12px;
        line-height: 1.7;
        color: var(--text-color);
        opacity: .62;
        margin-bottom: 25px;
    }

    .info-card {
        padding: 19px;
        border-radius: 17px;
        background: var(--secondary-background-color);
        border: 1px solid rgba(120,150,190,.17);
        height: 100%;
    }

    .info-card-icon {
        font-size: 22px;
        margin-bottom: 12px;
    }

    .info-card-title {
        font-size: 13px;
        font-weight: 800;
        color: var(--text-color);
        margin-bottom: 6px;
    }

    .info-card-text {
        font-size: 11px;
        line-height: 1.7;
        color: var(--text-color);
        opacity: .62;
    }

    .image-label {
        font-size: 11px;
        font-weight: 700;
        margin-top: 7px;
        color: var(--text-color);
    }

    .muted {
        color: var(--text-color);
        opacity: .58;
        font-size: 11px;
    }

    @media (max-width: 700px) {
        .hero {
            padding: 25px 22px;
        }
        .metric-card {
            min-height: 125px;
        }
    }
</style>
""")


# =========================================================
# DATA
# =========================================================

@st.cache_data
def get_data():
    return load_metadata()


try:
    df = get_data()
except Exception as error:
    st.error(f"Dataset loading failed: {error}")
    st.stop()


total_images = len(df)
total_classes = df["dx"].nunique()
total_lesions = df["lesion_id"].nunique()


# =========================================================
# REUSABLE COMPONENTS
# =========================================================

def page_header(eyebrow, title, description):
    st.html(f"""
        <div class="page-eyebrow">{escape(eyebrow)}</div>
        <div class="page-title">{escape(title)}</div>
        <div class="page-description">{escape(description)}</div>
    """)


def metric_card(title, value, description, icon, accent, icon_bg):
    st.html(f"""
        <div class="metric-card" style="--accent:{accent}; --icon-bg:{icon_bg};">
            <div class="metric-top">
                <div class="metric-label">{escape(title)}</div>
                <div class="metric-icon">{icon}</div>
            </div>
            <div class="metric-value">{escape(str(value))}</div>
            <div class="metric-description">{escape(description)}</div>
        </div>
    """)
 

def section_heading(title, description=""):
    st.html(f"""
        <div class="section-heading">{escape(title)}</div>
        <div class="section-description">{escape(description)}</div>
    """)


def info_card(icon, title, description):
    st.html(f"""
        <div class="info-card">
            <div class="info-card-icon">{icon}</div>
            <div class="info-card-title">{escape(title)}</div>
            <div class="info-card-text">{escape(description)}</div>
        </div>
    """)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.html("""
        <div class="brand-area">
            <div class="brand-icon">✳</div>
            <div>
                <div class="brand-name">DermaScan</div>
                <div class="brand-subtitle">SKIN INTELLIGENCE</div>
            </div>
        </div>
        <div class="sidebar-caption">WORKSPACE</div>
    """)

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Skin Analysis",
            "Dataset Explorer",
            "Disease Information",
            "About Model"
        ],
        label_visibility="collapsed"
    )

    st.html("""
        <div class="sidebar-status">
            <div class="sidebar-status-title">🧠 AI Model Status</div>
            <div class="sidebar-status-text">
                Vision Transformer model integration is currently in development.
            </div>
        </div>
        <div class="sidebar-footer">
            DermaScan © 2026<br>
            Educational Research Project
        </div>
    """)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.html("""
        <div class="hero">
            <div class="hero-tag">✦ SKIN INTELLIGENCE PLATFORM</div>
            <div class="hero-title">Understand Skin.<br>Explore with Intelligence.</div>
            <p class="hero-description">
                An AI-powered skin lesion classification research project.
                Explore the HAM10000 dataset and discover the technology
                behind intelligent skin image analysis.
            </p>
    """)

    section_heading(
        "Platform Overview"
    )

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        metric_card(
            "TOTAL IMAGES",
            f"{total_images:,}",
            "Images available in the dataset",
            "▧",
            "#3B82F6",
            "rgba(59,130,246,.13)"
        )

    with c2:
        metric_card(
            "DISEASE CLASSES",
            total_classes,
            "Different diagnosis categories",
            "✳",
            "#8B5CF6",
            "rgba(139,92,246,.13)"
        )

    with c3:
        metric_card(
            "UNIQUE LESIONS",
            f"{total_lesions:,}",
            "Unique lesion identifiers",
            "◎",
            "#10B981",
            "rgba(16,185,129,.13)"
        )

    st.write("")

    # Dataset distribution
    counts = (
        df["dx"]
        .value_counts()
        .rename_axis("Diagnosis")
        .reset_index(name="Images")
    )

    counts["Disease"] = counts["Diagnosis"].map(DISEASE_NAMES)

    left, right = st.columns([1.65, 1], gap="large")

    with left:
        st.html("""
            <div class="panel-title">Disease Distribution</div>
            <div class="panel-subtitle">
                Image count across the seven dataset categories
            </div>
        """)

        fig = px.bar(
            counts.sort_values("Images", ascending=True),
            x="Images",
            y="Disease",
            color="Diagnosis",
            orientation="h",
            color_discrete_map=DISEASE_COLORS,
            text="Images"
        )

        fig.update_traces(
            textposition="outside",
            textfont_size=10,
            marker_line_width=0,
            cliponaxis=False
        )

        fig.update_layout(
            template="plotly_dark" if is_dark else "plotly_white",
            height=390,
            margin=dict(l=5, r=35, t=10, b=10),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="Arial",
                size=10,
                color="#A8B5C7" if is_dark else "#64748B"
            ),
            xaxis=dict(
                title=None,
                showgrid=True,
                gridcolor="rgba(140,160,190,.15)",
                zeroline=False
            ),
            yaxis=dict(
                title=None,
                showgrid=False,
                automargin=True
            ),
            bargap=0.38
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    with right:
        st.html("""
            <div class="panel-title">Category Breakdown</div>
            <div class="panel-subtitle">
                Dataset composition by diagnosis
            </div>
        """)

        for code, count in df["dx"].value_counts().items():

            name = DISEASE_NAMES.get(code, code)
            color = DISEASE_COLORS.get(code, "#64748B")
            percentage = count / total_images * 100

            st.html(f"""
                <div class="category-row">
                    <div class="category-dot" style="background:{color}"></div>
                    <div class="category-info">
                        <div class="category-name">{escape(name)}</div>
                        <div class="category-code">{escape(code.upper())}</div>
                        <div class="progress-track">
                            <div class="progress-fill"
                                style="width:{percentage}%; background:{color}">
                            </div>
                        </div>
                    </div>
                    <div>
                        <div class="category-number">{count:,}</div>
                        <div class="category-percent">{percentage:.1f}%</div>
                    </div>
                </div>
            """)

    st.write("")

    # Model status panel
    st.html("""
        <div class="model-panel">
            <div class="model-badge">MODEL DEVELOPMENT</div>
            <div class="model-heading">Vision Transformer (ViT)</div>
            <div class="model-copy">
                DermaScan is being developed with a Vision Transformer
                approach for skin lesion image classification.
                The frontend and dataset exploration features are available.
                Model integration and prediction functionality are still
                under development.
            </div>
        </div>
    """)


# =========================================================
# SKIN ANALYSIS
# =========================================================

elif page == "Skin Analysis":

    page_header(
        "IMAGE WORKSPACE",
        "Skin Analysis",
        "Upload a skin image to preview it in the DermaScan workspace."
    )

    st.html("""
        <div class="panel">
            <div class="panel-title">Upload Skin Image</div>
            <div class="panel-subtitle">
                Supported formats: JPG, JPEG and PNG
            </div>
        </div>
    """)

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:

        try:
            image = Image.open(uploaded_file).convert("RGB")

            left, right = st.columns([1.2, 1], gap="large")

            with left:
                st.image(
                    image,
                    caption="Uploaded Skin Image",
                    use_container_width=True
                )

            with right:
                section_heading("Image Details", "Information about your uploaded file.")

                metric_card(
                    "IMAGE WIDTH",
                    f"{image.width}px",
                    "Image horizontal resolution",
                    "↔",
                    "#3B82F6",
                    "rgba(59,130,246,.13)"
                )

                st.write("")

                metric_card(
                    "IMAGE HEIGHT",
                    f"{image.height}px",
                    "Image vertical resolution",
                    "↕",
                    "#8B5CF6",
                    "rgba(139,92,246,.13)"
                )

                st.write("")
                st.html(f"""
                    <div class="panel">
                        <div class="panel-title">File Information</div>
                        <p class="muted">Filename: {escape(uploaded_file.name)}</p>
                        <p class="muted">Format: {escape(str(uploaded_file.type))}</p>
                    </div>
                """)

            st.warning(
                "The AI prediction model is not yet integrated. "
                "This page currently provides image preview only. "
                "It does not provide a medical diagnosis."
            )

        except Exception as error:
            st.error(f"Could not open image: {error}")

    else:
        st.info("Upload a skin image to see its preview here.")


# =========================================================
# DATASET EXPLORER
# =========================================================

elif page == "Dataset Explorer":

    page_header(
        "DATA MANAGEMENT",
        "Dataset Explorer",
        "Explore and preview skin lesion images from the HAM10000 dataset."
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_disease = st.selectbox(
            "Filter by disease category",
            ["All"] + sorted(df["dx"].unique().tolist()),
            format_func=lambda x: (
                "All Categories"
                if x == "All"
                else f"{DISEASE_NAMES.get(x, x)} ({x.upper()})"
            )
        )

    with col2:
        preview_count = st.selectbox(
            "Images to preview",
            [8, 12, 16, 24],
            index=0
        )

    filtered_df = df.copy()

    if selected_disease != "All":
        filtered_df = filtered_df[
            filtered_df["dx"] == selected_disease
        ]

    st.caption(f"{len(filtered_df):,} images found")

    if not filtered_df.empty:

        preview_df = filtered_df.sample(
            n=min(preview_count, len(filtered_df)),
            random_state=42
        )

        columns = st.columns(4)

        for index, (_, row) in enumerate(preview_df.iterrows()):

            image_path = find_image(row["image_id"])

            with columns[index % 4]:

                if image_path:
                    try:
                        st.image(
                            str(image_path),
                            use_container_width=True
                        )
                    except Exception:
                        st.warning("Unable to load image.")
                else:
                    st.warning("Image not found.")

                disease_name = DISEASE_NAMES.get(
                    row["dx"],
                    row["dx"]
                )

                st.html(f"""
                    <div class="image-label">{escape(disease_name)}</div>
                    <div class="muted">{escape(str(row["image_id"]))}</div>
                """)

    else:
        st.info("No images found for this category.")


# =========================================================
# DISEASE INFORMATION
# =========================================================

elif page == "Disease Information":

    page_header(
        "MEDICAL KNOWLEDGE",
        "Disease Information",
        "Learn about the seven diagnostic categories represented in HAM10000."
    )

    descriptions = {
        "akiec": (
            "Actinic Keratoses",
            "A rough, scaly skin lesion commonly associated with long-term "
            "sun exposure. Some lesions can develop into skin cancer."
        ),
        "bcc": (
            "Basal Cell Carcinoma",
            "A common type of skin cancer that develops in basal cells. "
            "It often appears on areas exposed to sunlight."
        ),
        "bkl": (
            "Benign Keratosis-like Lesions",
            "A group of benign skin growths, including seborrheic "
            "keratoses and related lesions."
        ),
        "df": (
            "Dermatofibroma",
            "A common benign skin nodule that often appears as a small, "
            "firm bump."
        ),
        "mel": (
            "Melanoma",
            "A serious type of skin cancer that develops from pigment-"
            "producing cells called melanocytes."
        ),
        "nv": (
            "Melanocytic Nevi",
            "Commonly known as moles, these are usually benign growths "
            "of melanocytes."
        ),
        "vasc": (
            "Vascular Lesions",
            "Skin lesions involving blood vessels, including several "
            "types of benign vascular growths."
        )
    }

    for code, (name, description) in descriptions.items():

        count = int((df["dx"] == code).sum())
        color = DISEASE_COLORS[code]

        with st.expander(f"{name}  ·  {count:,} images"):

            st.html(f"""
                <div style="
                    border-left:4px solid {color};
                    padding:12px 16px;
                    background:rgba(120,150,190,.07);
                    border-radius:0 12px 12px 0;
                    margin:5px 0 10px 0;
                ">
                    <div style="
                        font-weight:800;
                        font-size:14px;
                        color:var(--text-color);
                    ">{escape(name)}</div>
                    <p style="
                        font-size:12px;
                        line-height:1.8;
                        color:var(--text-color);
                        opacity:.72;
                        margin-bottom:0;
                    ">{escape(description)}</p>
                </div>
            """)

    st.warning(
        "This information is provided for educational purposes only. "
        "Dataset labels and descriptions should not be used as a "
        "substitute for professional medical advice."
    )


# =========================================================
# ABOUT MODEL
# =========================================================

elif page == "About Model":

    page_header(
        "PROJECT INFORMATION",
        "About DermaScan",
        "Learn about the technology, dataset and development direction."
    )

    st.html("""
        <div class="hero">
            <div class="hero-tag">ABOUT THE PROJECT</div>
            <div class="hero-title">AI for Skin Image<br>Classification Research</div>
            <p class="hero-description">
                DermaScan is an educational AI project exploring how
                deep learning and computer vision can be applied
                to skin lesion image classification.
            </p>
        </div>
    """)

    section_heading(
        "Technology Stack",
        "The main technologies used in this project."
    )

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        info_card(
            "🐍",
            "Python",
            "The primary programming language used for data processing "
            "and machine learning development."
        )

    with c2:
        info_card(
            "📊",
            "HAM10000",
            "A publicly available dataset containing dermatoscopic images "
            "across seven diagnostic categories."
        )

    with c3:
        info_card(
            "🧠",
            "Vision Transformer",
            "The selected deep learning architecture being explored "
            "for image classification."
        )

    st.write("")
    section_heading(
        "Development Status",
        "Current project components."
    )

    status_items = [
        ("Frontend dashboard", "Available", "success"),
        ("Dataset integration", "Available", "success"),
        ("Image preview", "Available", "success"),
        ("ViT model training", "In development", "pending"),
        ("Model integration", "In development", "pending"),
        ("Prediction interface", "Not yet available", "pending")
    ]

    for item, status, state in status_items:

        color = "#10B981" if state == "success" else "#E5A43B"
        symbol = "●" if state == "success" else "◷"

        st.html(f"""
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:13px 15px;
                margin:7px 0;
                border-radius:12px;
                background:var(--secondary-background-color);
                border:1px solid rgba(120,150,190,.15);
            ">
                <div style="
                    font-size:12px;
                    font-weight:700;
                    color:var(--text-color);
                ">{escape(item)}</div>
                <div style="
                    font-size:10px;
                    font-weight:800;
                    color:{color};
                ">{symbol} &nbsp; {escape(status)}</div>
            </div>
        """)

    st.write("")

    st.info(
        "DermaScan is an educational research prototype, not a "
        "clinically validated medical diagnostic system."
    )
