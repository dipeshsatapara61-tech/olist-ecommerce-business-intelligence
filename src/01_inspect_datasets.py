
from pathlib import Path
import pandas as pd

# Project directory
PROJECT_DIR = Path(__file__).resolve().parents[1]

# Raw dataset directory
DATA_DIR = PROJECT_DIR / "data" / "raw"

print("=" * 70)
print("OLIST E-COMMERCE DATASET INSPECTION")
print("=" * 70)

# Check whether the folder exists
if not DATA_DIR.exists():
    raise FileNotFoundError(f"Dataset folder not found: {DATA_DIR}")

# Find CSV files
csv_files = sorted(DATA_DIR.glob("*.csv"))

print(f"\nTotal CSV files found: {len(csv_files)}")

if not csv_files:
    raise FileNotFoundError("No CSV files found inside data/raw")

# Inspect every CSV file
for file in csv_files:

    print("\n" + "=" * 70)
    print(f"FILE NAME: {file.name}")
    print("=" * 70)

    # File size
    size_mb = file.stat().st_size / (1024 * 1024)
    print(f"File Size: {size_mb:.2f} MB")

    try:
        # Read sample records only
        df = pd.read_csv(file, nrows=5)

        print("\nColumns:")
        print(df.columns.tolist())

        print("\nData Types:")
        print(df.dtypes)

        print("\nSample Records:")
        print(df.head())

        print("\nMissing Values in Sample:")
        print(df.isnull().sum())

        print("\nInspection completed.")

    except Exception as error:
        print(f"ERROR: {error}")

print("\n" + "=" * 70)
print("DATASET INSPECTION FINISHED")
print("=" * 70)
