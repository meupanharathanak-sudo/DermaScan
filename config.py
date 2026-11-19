from pathlib import Path

# Main dataset directory
DATASET_DIR = Path(
    r"D:\Skin_Disease_Classificaton\data\raw\archive (5)"
)

# Metadata
METADATA_PATH = DATASET_DIR / "HAM10000_metadata.csv"

# Image folders
IMAGE_DIRS = [
    DATASET_DIR / "HAM10000_images_part_1",
    DATASET_DIR / "HAM10000_images_part_2",
]

# DermaScan project directory
BASE_DIR = Path(__file__).resolve().parent