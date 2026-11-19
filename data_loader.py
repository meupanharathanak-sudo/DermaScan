
import pandas as pd
import streamlit as st

from config import METADATA_PATH, IMAGE_DIRS


@st.cache_data
def load_metadata():
    """Load HAM10000 metadata."""
    return pd.read_csv(METADATA_PATH)


def find_image(image_id):
    """Find an image in either HAM10000 image folder."""
    for folder in IMAGE_DIRS:
        image_path = folder / f"{image_id}.jpg"

        if image_path.exists():
            return image_path

    return None


def get_class_counts(df):
    """Return the number of images in each diagnosis class."""
    return df["dx"].value_counts()
