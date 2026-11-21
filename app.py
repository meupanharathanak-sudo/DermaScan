import streamlit as st
import plotly.express as px
import pandas as pd
from PIL import Image
from html import escape

from data_loader import load_metadata, find_image


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="DermaScan | Skin Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

is_dark = st.get_option("theme.base") == "dark"


# =========================================================
# 2. DISEASE INFORMATION
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
# 3. GLOBAL DESIGN
# =========================================================

st.html("""
<style>
    .stApp {
        background:
            radial-gradient(
                ellipse at 10% 0%,
                rgba(45,116,230,.07),
                transparent 32%
            ),
            var(--background-color);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(120,150,190,.16);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    /* Sidebar brand */

    .brand-area {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 22px;
    }

    .brand-icon {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg,#2563EB,#38BDF8);
        color: white;
        font-size: 23px;
    }

    .brand-name {
        font-size: 21px;
        font-weight: 800;
        color: var(--text-color);
    }

    .brand-subtitle {
        font-size: 9px;
        letter-spacing: 1.8px;
        color: #6B9BE8;
        font-weight: 800;
    }

    .sidebar-caption {
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.6px;
        color: #8B9BB3;
        margin-bottom: 10px;
    }

    /* Hero section */

    .hero {
        padding: 35px 38px;
        border-radius: 25px;
        color: white;
        background: linear-gradient(
            115deg,
            #102B59 0%,
            #1557B8 52%,
            #168FCB 100%
        );
        box-shadow: 0 15px 38px rgba(21,87,184,.20);
        margin-bottom: 25px;
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
        font-size: clamp(27px,3.2vw,40px);
        font-weight: 850;
        letter-spacing: -1.4px;
        line-height: 1.15;
        margin-bottom: 12px;
        color: white;
    }

    .hero-description {
        color: #D8E9FF;
        font-size: 13px;
        line-height: 1.8;
        max-width: 600px;
        margin: 0;
    }

    /* Page headings */

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
        margin-bottom: 7px;
    }

    .page-description {
        font-size: 12px;
        line-height: 1.7;
        color: var(--text-color);
        opacity: .65;
        margin-bottom: 25px;
    }

    /* Native metric cards */

    [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid rgba(120,150,190,.17);
        border-radius: 17px;
        padding: 18px;
        box-shadow: 0 5px 18px rgba(20,50,90,.045);
    }

    [data-testid="stMetricLabel"] {
        font-size: 12px;
        font-weight: 700;
    }

    [data-testid="stMetricValue"] {
        font-weight: 850;
    }

    /* Native containers */

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 17px;
    }

    /* Sidebar status */

    .sidebar-status {
        margin-top: 25px;
        padding: 15px;
        border-radius: 15px;
        background: linear-gradient(
            135deg,
            rgba(37,99,235,.12),
            rgba(56,189,248,.06)
        );
        border: 1px solid rgba(59,130,246,.22);
    }

    .sidebar-status-title {
        font-size: 12px;
        font-weight: 750;
        color: var(--text-color);
    }

    .sidebar-status-text {
        font-size: 11px;
        color: var(--text-color);
        opacity: .65;
        line-height: 1.5;
        margin-top: 5px;
    }

    .sidebar-footer {
        font-size: 10px;
        color: #8B9BB3;
        margin-top: 25px;
        line-height: 1.7;
    }

    @media (max-width: 700px) {
        .hero {
            padding: 25px 22px;
        }
    }
</style>
""")


# =========================================================
# 4. LOAD DATASET
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
# 5. REUSABLE FUNCTIONS
# =========================================================

def page_header(eyebrow, title, description):
    st.markdown(
        f"""
        <div class="page-eyebrow">{escape(eyebrow)}</div>
        <div class="page-title">{escape(title)}</div>
        <div class="page-description">
            {escape(description)}
        </div>
        """,
        unsafe_allow_html=True
    )


def hero_section(tag, title, description):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-tag">{escape(tag)}</div>
            <div class="hero-title">{title}</div>
            <p class="hero-description">
                {escape(description)}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_heading(title, description=None):
    st.subheader(title)

    if description:
        st.caption(description)


def metric_card(label, value, help_text=None):
    st.metric(
        label=label,
        value=value,
        help=help_text
    )


# =========================================================
# 6. SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:

    st.markdown("""
        <div class="brand-area">
            <div class="brand-icon">✳</div>
            <div>
                <div class="brand-name">DermaScan</div>
                <div class="brand-subtitle">SKIN INTELLIGENCE</div>
            </div>
        </div>
        <div class="sidebar-caption">WORKSPACE</div>
    """, unsafe_allow_html=True)

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

    st.markdown("""
        <div class="sidebar-status">
            <div class="sidebar-status-title">
                🧠 AI Model Status
            </div>
            <div class="sidebar-status-text">
                Vision Transformer model integration is currently
                in development.
            </div>
        </div>

        <div class="sidebar-footer">
            DermaScan © 2026<br>
            Educational Research Project
        </div>
    """, unsafe_allow_html=True)


# =========================================================
# 7. DASHBOARD
# =========================================================

if page == "Dashboard":

    hero_section(
        "✦ SKIN INTELLIGENCE PLATFORM",
        "Understand Skin.<br>Explore with Intelligence.",
        "An AI-powered skin lesion classification research project. "
        "Explore the HAM10000 dataset and discover the technology "
        "behind intelligent skin image analysis."
    )

    section_heading("Platform Overview")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "▧ Total Images",
            f"{total_images:,}",
            "Images available in the dataset"
        )

    with c2:
        metric_card(
            "✳ Disease Classes",
            total_classes,
            "Different diagnostic categories"
        )

    with c3:
        metric_card(
            "◎ Unique Lesions",
            f"{total_lesions:,}",
            "Unique lesion identifiers"
        )

    st.write("")

    # Prepare chart data

    counts = (
        df["dx"]
        .value_counts()
        .rename_axis("Diagnosis")
        .reset_index(name="Images")
    )

    counts["Disease"] = counts["Diagnosis"].map(DISEASE_NAMES)

    left, right = st.columns([1.65, 1], gap="large")

    with left:

        with st.container(border=True):

            st.subheader("Disease Distribution")
            st.caption(
                "Image count across the seven dataset categories"
            )

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

        with st.container(border=True):

            st.subheader("Category Breakdown")
            st.caption("Dataset composition by diagnosis")

            for code, count in df["dx"].value_counts().items():

                name = DISEASE_NAMES.get(code, code)
                percentage = count / total_images

                st.markdown(f"**{name}**")
                st.caption(
                    f"{code.upper()} · {count:,} images · "
                    f"{percentage:.1%}"
                )

                st.progress(percentage)

    st.write("")

    with st.container(border=True):

        st.markdown("### 🧠 Vision Transformer (ViT)")
        st.caption("MODEL DEVELOPMENT")

        st.write(
            "DermaScan is being developed with a Vision Transformer "
            "approach for skin lesion image classification. "
            "The frontend and dataset exploration features are available. "
            "Model integration and prediction functionality are still "
            "under development."
        )


# =========================================================
# 8. SKIN ANALYSIS
# =========================================================

elif page == "Skin Analysis":

    page_header(
        "IMAGE WORKSPACE",
        "Skin Analysis",
        "Upload a skin image to preview it in the DermaScan workspace."
    )

    with st.container(border=True):
        st.subheader("Upload Skin Image")
        st.caption("Supported formats: JPG, JPEG and PNG")

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

                section_heading(
                    "Image Details",
                    "Information about your uploaded file."
                )

                metric_card(
                    "Image Width",
                    f"{image.width}px"
                )

                metric_card(
                    "Image Height",
                    f"{image.height}px"
                )

                with st.container(border=True):
                    st.subheader("File Information")
                    st.write("Filename:", uploaded_file.name)
                    st.write("Format:", uploaded_file.type)

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
# 9. DATASET EXPLORER
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

                st.markdown(f"**{disease_name}**")
                st.caption(str(row["image_id"]))

    else:
        st.info("No images found for this category.")


# =========================================================
# 10. DISEASE INFORMATION
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

        with st.expander(f"{name} · {count:,} images"):

            st.markdown(f"**{name}**")
            st.write(description)

    st.warning(
        "This information is provided for educational purposes only. "
        "Dataset labels and descriptions should not be used as a "
        "substitute for professional medical advice."
    )


# =========================================================
# 11. ABOUT MODEL
# =========================================================

elif page == "About Model":

    page_header(
        "PROJECT INFORMATION",
        "About DermaScan",
        "Learn about the technology, dataset and development direction."
    )

    hero_section(
        "ABOUT THE PROJECT",
        "AI for Skin Image<br>Classification Research",
        "DermaScan is an educational AI project exploring how "
        "deep learning and computer vision can be applied "
        "to skin lesion image classification."
    )

    section_heading(
        "Technology Stack",
        "The main technologies used in this project."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown("## 🐍")
            st.subheader("Python")
            st.write(
                "The primary programming language used for data "
                "processing and machine learning development."
            )

    with c2:
        with st.container(border=True):
            st.markdown("## 📊")
            st.subheader("HAM10000")
            st.write(
                "A publicly available dataset containing dermatoscopic "
                "images across seven diagnostic categories."
            )

    with c3:
        with st.container(border=True):
            st.markdown("## 🧠")
            st.subheader("Vision Transformer")
            st.write(
                "The selected deep learning architecture being explored "
                "for image classification."
            )

    st.write("")

    section_heading(
        "Development Status",
        "Current project components."
    )

    status_items = [
        ("Frontend dashboard", "Available"),
        ("Dataset integration", "Available"),
        ("Image preview", "Available"),
        ("ViT model training", "In development"),
        ("Model integration", "In development"),
        ("Prediction interface", "Not yet available")
    ]

    for item, status in status_items:

        left, right = st.columns([3, 1])

        with left:
            st.write(f"**{item}**")

        with right:
            if status == "Available":
                st.success(status)
            else:
                st.warning(status)

    st.write("")

    st.info(
        "DermaScan is an educational research prototype, not a "
        "clinically validated medical diagnostic system."
    )
