
import streamlit as st
import plotly.express as px
import pandas as pd
from PIL import Image

from data_loader import load_metadata, find_image


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="DermaScan | Skin Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DESIGN SYSTEM
# =========================================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background: #F4F7FB;
    color: #1E293B;
}

/* Main container */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E6ECF3;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #334155;
}

/* Main headings */
h1 {
    color: #123B65 !important;
    font-size: 32px !important;
    font-weight: 750 !important;
}

h2 {
    color: #174A78 !important;
    font-size: 23px !important;
    font-weight: 700 !important;
}

h3 {
    color: #174A78 !important;
    font-size: 18px !important;
    font-weight: 650 !important;
}

/* Body text */
.stApp p,
.stApp li {
    color: #475569;
}

/* Metric cards */
.metric-card {
    background: #FFFFFF;
    padding: 22px;
    border: 1px solid #E5EAF1;
    border-radius: 15px;
    min-height: 125px;
    box-shadow: 0 3px 12px rgba(15, 45, 75, 0.035);
}

.metric-title {
    color: #64748B;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 12px;
}

.metric-number {
    color: #123B65;
    font-size: 30px;
    font-weight: 750;
}

.metric-description {
    color: #94A3B8;
    font-size: 12px;
    margin-top: 5px;
}

/* Section cards */
.content-card {
    background: #FFFFFF;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #E5EAF1;
    margin-bottom: 15px;
}

/* Brand */
.brand-name {
    font-size: 25px;
    font-weight: 800;
    color: #1769AA;
    letter-spacing: -0.8px;
}

.brand-subtitle {
    font-size: 11px;
    color: #94A3B8;
    margin-top: -4px;
}

/* Status pill */
.status-pill {
    display: inline-block;
    padding: 6px 12px;
    background: #FFF7E6;
    color: #A16207;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 650;
}

/* Image styling */
[data-testid="stImage"] img {
    border-radius: 12px;
}

/* Buttons */
.stButton > button {
    background: #1769AA;
    color: white !important;
    border: none;
    border-radius: 9px;
    font-weight: 600;
}

.stButton > button:hover {
    background: #12558C;
    color: white !important;
    border: none;
}

/* Upload area */
[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #B7CBE0;
    border-radius: 13px;
    padding: 12px;
}

/* Select boxes */
[data-testid="stSelectbox"] {
    background: transparent;
}

/* Expander */
[data-testid="stExpander"] {
    background: white;
    border: 1px solid #E5EAF1;
    border-radius: 12px;
}

/* Divider */
hr {
    border-color: #E5EAF1;
}

/* Footer */
.custom-footer {
    text-align: center;
    color: #94A3B8;
    font-size: 12px;
    padding-top: 30px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA AND DISEASE LABELS
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


@st.cache_data
def get_data():
    return load_metadata()


try:
    df = get_data()
except Exception as error:
    st.error(f"Dataset loading failed: {error}")
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="brand-name">🔬 DermaScan</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand-subtitle">SKIN INTELLIGENCE PLATFORM</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.caption("MAIN MENU")

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

    st.divider()

    st.markdown(
        '<div class="status-pill">● Model in development</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="custom-footer">DermaScan © 2026<br>Educational Research Project</div>',
        unsafe_allow_html=True
    )


# =========================================================
# REUSABLE METRIC CARD
# =========================================================

def metric_card(title, value, description):

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-number">{value}</div>
            <div class="metric-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title("Dashboard")

    st.write(
        "Welcome to DermaScan. Explore skin lesion data "
        "and monitor the development of the classification system."
    )

    st.markdown(
        '<div class="status-pill">● Research prototype | Model not integrated</div>',
        unsafe_allow_html=True
    )

    st.write("")

    # Statistics
    total_images = len(df)
    total_classes = df["dx"].nunique()
    total_lesions = df["lesion_id"].nunique()

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card(
            "TOTAL IMAGES",
            f"{total_images:,}",
            "HAM10000 image records"
        )

    with col2:
        metric_card(
            "DISEASE CATEGORIES",
            str(total_classes),
            "Classification categories"
        )

    with col3:
        metric_card(
            "UNIQUE LESIONS",
            f"{total_lesions:,}",
            "Unique lesion identifiers"
        )

    st.write("")
    st.divider()

    # Distribution
    st.subheader("Dataset Overview")

    chart_col, info_col = st.columns([1.65, 1])

    counts = (
        df["dx"]
        .value_counts()
        .rename_axis("Diagnosis")
        .reset_index(name="Images")
    )

    counts["Disease"] = counts["Diagnosis"].map(DISEASE_NAMES)

    with chart_col:

        st.markdown("**Disease Distribution**")

        fig = px.bar(
            counts.sort_values("Images"),
            x="Images",
            y="Disease",
            orientation="h",
            color="Diagnosis",
            color_discrete_map=DISEASE_COLORS,
            text="Images"
        )

        fig.update_traces(
            textposition="outside",
            textfont=dict(
                color="#334155",
                size=12
            ),
            cliponaxis=False
        )

        fig.update_layout(
            height=390,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            showlegend=False,
            font=dict(
                color="#334155",
                size=12
            ),
            xaxis_title="Number of Images",
            yaxis_title="",
            margin=dict(l=5, r=40, t=15, b=10)
        )

        fig.update_xaxes(
            gridcolor="#EDF1F6",
            tickfont=dict(color="#64748B")
        )

        fig.update_yaxes(
            tickfont=dict(color="#334155")
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with info_col:

        st.markdown("**Category Summary**")

        for code, name in DISEASE_NAMES.items():

            count = int((df["dx"] == code).sum())
            percentage = count / total_images * 100

            st.markdown(
                f"""
                <div style="
                    background:white;
                    border:1px solid #E5EAF1;
                    border-radius:10px;
                    padding:10px 12px;
                    margin-bottom:8px;
                ">
                    <div style="
                        display:flex;
                        justify-content:space-between;
                        gap:8px;
                        color:#334155;
                        font-size:12px;
                        font-weight:600;
                    ">
                        <span>{name}</span>
                        <span>{count:,}</span>
                    </div>
                    <div style="
                        background:#EDF2F7;
                        height:6px;
                        border-radius:10px;
                        margin-top:8px;
                    ">
                        <div style="
                            background:{DISEASE_COLORS[code]};
                            width:{percentage}%;
                            height:6px;
                            border-radius:10px;
                        "></div>
                    </div>
                    <div style="
                        color:#94A3B8;
                        font-size:10px;
                        margin-top:4px;
                    ">{percentage:.1f}% of dataset</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    # Model status
    st.subheader("Model Development")

    status_col1, status_col2 = st.columns([2, 1])

    with status_col1:

        st.markdown(
            """
            <div class="content-card">
                <h3>Vision Transformer (ViT)</h3>
                <p>
                    DermaScan is being developed as an educational
                    skin lesion classification system using a
                    Vision Transformer architecture.
                </p>
                <p style="color:#D97706;font-weight:600;">
                    Current status: Model integration in progress
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    

# =========================================================
# SKIN ANALYSIS
# =========================================================

elif page == "Skin Analysis":

    st.title("Skin Analysis")

    st.write(
        "Upload a dermatoscopic image for image preview."
    )

    st.markdown(
        """
        <div class="content-card">
            <h3>Image Upload</h3>
            <p>
                Supported formats: JPG, JPEG, PNG.
                The uploaded image will be displayed for preview.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Choose a skin lesion image",
        type=["jpg", "jpeg", "png"],
        key="skin_upload"
    )

    if uploaded_file:

        try:

            image = Image.open(uploaded_file).convert("RGB")

            col1, col2 = st.columns([1.2, 1])

            with col1:

                st.image(
                    image,
                    caption="Uploaded Image",
                    use_container_width=True
                )

            with col2:

                st.subheader("Image Details")

                st.write(f"**Filename:** {uploaded_file.name}")

                st.write(
                    f"**Image width:** {image.width} pixels"
                )

                st.write(
                    f"**Image height:** {image.height} pixels"
                )

                st.write(
                    f"**Image format:** {uploaded_file.type}"
                )

                st.success("Image uploaded successfully.")

                st.warning(
                    "The ViT model has not yet been integrated. "
                    "No diagnostic prediction is available."
                )

        except Exception:

            st.error("Unable to read the uploaded image.")

    else:

        st.info(
            "Upload an image to see its preview and image details."
        )


# =========================================================
# DATASET EXPLORER
# =========================================================

elif page == "Dataset Explorer":

    st.title("Dataset Explorer")

    st.write(
        "Browse and explore the real HAM10000 skin lesion images."
    )

    filter_col, sort_col = st.columns([2, 1])

    with filter_col:

        selected_class = st.selectbox(
            "Select disease category",
            ["All"] + sorted(df["dx"].unique().tolist()),
            format_func=lambda x: (
                "All Categories"
                if x == "All"
                else f"{DISEASE_NAMES.get(x, x)} ({x.upper()})"
            )
        )

    with sort_col:

        preview_count = st.selectbox(
            "Images to display",
            [8, 12, 16, 24],
            index=0
        )

    filtered_df = df.copy()

    if selected_class != "All":

        filtered_df = filtered_df[
            filtered_df["dx"] == selected_class
        ]

    st.divider()

    st.markdown(
        f"**{len(filtered_df):,} images available in this selection**"
    )

    # Random sample provides variety on each selection
    sample_df = filtered_df.sample(
        n=min(200, len(filtered_df)),
        random_state=42
    )

    image_columns = st.columns(4)

    displayed = 0

    for _, row in sample_df.iterrows():

        if displayed >= preview_count:
            break

        image_path = find_image(row["image_id"])

        if image_path is None:
            continue

        with image_columns[displayed % 4]:

            st.image(
                str(image_path),
                use_container_width=True
            )

            st.markdown(
                f"**{DISEASE_NAMES.get(row['dx'], row['dx'])}**"
            )

            st.caption(
                f"Image ID: {row['image_id']}"
            )

        displayed += 1

    if displayed == 0:

        st.warning(
            "No image files were found for this selection."
        )

    st.divider()

    st.caption(
        "Images displayed are samples from the HAM10000 dataset."
    )


# =========================================================
# DISEASE INFORMATION
# =========================================================

elif page == "Disease Information":

    st.title("Disease Information")

    st.write(
        "Overview of the seven diagnostic categories "
        "represented in the HAM10000 dataset."
    )

    for code, name in DISEASE_NAMES.items():

        count = int((df["dx"] == code).sum())

        with st.expander(
            f"{name} ({code.upper()})"
        ):

            st.write(f"**Dataset category:** {code.upper()}")

            st.write(f"**Number of images:** {count:,}")

            st.write(
                "This category is included in the HAM10000 "
                "skin lesion dataset. Detailed educational "
                "information will be added in a future update."
            )

    st.info(
        "This page provides dataset information only. "
        "It is not intended for medical diagnosis."
    )


# =========================================================
# ABOUT MODEL
# =========================================================

elif page == "About Model":

    st.title("About DermaScan")

    st.write(
        "An educational AI project focused on skin lesion "
        "image classification."
    )

    st.divider()

    st.subheader("Project Overview")

    st.write(
        """
        DermaScan aims to develop a skin lesion classification
        system using deep learning and the Vision Transformer
        (ViT) architecture.

        The project uses the HAM10000 dataset, containing
        10,015 dermatoscopic image records across seven
        diagnostic categories.
        """
    )

    st.subheader("Technology Stack")

    tech1, tech2, tech3 = st.columns(3)

    with tech1:
        metric_card("FRONTEND", "Streamlit", "Interactive web application")

    with tech2:
        metric_card("DATASET", "HAM10000", "Skin lesion image dataset")

    with tech3:
        metric_card("MODEL", "ViT", "Vision Transformer architecture")

    st.divider()

    st.subheader("Development Progress")

    st.write("✅ Dataset connected")
    st.write("✅ Metadata loading")
    st.write("✅ Dashboard interface")
    st.write("✅ Dataset image explorer")
    st.write("✅ Image upload and preview")
    st.write("🔄 ViT model development")
    st.write("🔄 Model integration")

    st.divider()

    st.warning(
        "DermaScan is an educational research prototype. "
        "It is not a medical diagnostic device and should "
        "not replace professional medical advice."
    )

