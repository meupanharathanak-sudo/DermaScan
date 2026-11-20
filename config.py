
from pathlib import Path

# Main DermaScan project directory
BASE_DIR = Path(__file__).resolve().parent

# Dataset directory
DATASET_DIR = BASE_DIR / "data" / "archive (5)"

# Metadata CSV file
METADATA_PATH = DATASET_DIR / "HAM10000_metadata.csv"

# Image directories
IMAGE_DIRS = [
    DATASET_DIR / "HAM10000_images_part_1",
    DATASET_DIR / "HAM10000_images_part_2",
]
