
import pandas as pd
from config import DATA_DIR, METADATA_PATH, IMAGE_DIRS

print("Checking HAM10000 dataset...")

print("Dataset folder:", DATA_DIR.exists())
print("Metadata file:", METADATA_PATH.exists())

df = pd.read_csv(METADATA_PATH)

print("\nTotal images:", len(df))
print("\nDisease distribution:")
print(df["dx"].value_counts())

print("\nImage folders:")
for folder in IMAGE_DIRS:
    print(folder.name, folder.exists())
