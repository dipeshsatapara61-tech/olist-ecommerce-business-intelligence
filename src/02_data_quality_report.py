
from pathlib import Path
import pandas as pd
import numpy as np

# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 100_000

# Candidate keys to validate
KEYS = {
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_orders_dataset.csv": ["order_id"],
    "olist_order_items_dataset.csv": ["order_id", "order_item_id"],
    "olist_order_payments_dataset.csv": ["order_id", "payment_sequential"],
    "olist_order_reviews_dataset.csv": ["review_id"],
    "olist_products_dataset.csv": ["product_id"],
    "olist_sellers_dataset.csv": ["seller_id"],
    "product_category_name_translation.csv": [
        "product_category_name"
    ]
}

# ==========================================
# 2. INITIALIZE REPORTS
# ==========================================

summary_report = []
column_report = []
key_report = []

csv_files = sorted(RAW_DIR.glob("*.csv"))

print("=" * 70)
print("OLIST COMPLETE DATA QUALITY ANALYSIS")
print("=" * 70)

# ==========================================
# 3. PROCESS EACH DATASET
# ==========================================

for file in csv_files:

    print(f"\nProcessing: {file.name}")

    row_count = 0
    total_duplicates = 0
    missing_counts = {}
    hash_chunks = []
    column_types = {}
    unique_counts = {}

    # --------------------------------------
    # Special processing for geolocation
    # --------------------------------------

    if file.name == "olist_geolocation_dataset.csv":

        for chunk in pd.read_csv(
            file,
            chunksize=CHUNK_SIZE,
            low_memory=False
        ):

            row_count += len(chunk)

            # Missing values
            for col, count in chunk.isnull().sum().items():
                missing_counts[col] = (
                    missing_counts.get(col, 0) + int(count)
                )

            # Hash rows to detect duplicates
            row_hashes = pd.util.hash_pandas_object(
                chunk,
                index=False
            )

            hash_chunks.append(row_hashes.to_numpy())

            column_types = {
                col: str(dtype)
                for col, dtype in chunk.dtypes.items()
            }

        # Check duplicate rows across all chunks
        all_hashes = np.concatenate(hash_chunks)

        total_duplicates = int(
            pd.Series(all_hashes).duplicated().sum()
        )

        del all_hashes
        del hash_chunks

        # Geolocation zip codes are NOT unique.
        # Do not treat them as primary keys.

    # --------------------------------------
    # Process remaining datasets
    # --------------------------------------

    else:

        df = pd.read_csv(file, low_memory=False)

        row_count = len(df)

        total_duplicates = int(df.duplicated().sum())

        missing_counts = {
            col: int(count)
            for col, count in df.isnull().sum().items()
        }

        column_types = {
            col: str(dtype)
            for col, dtype in df.dtypes.items()
        }

        unique_counts = {
            col: int(df[col].nunique(dropna=True))
            for col in df.columns
        }

        # Candidate key validation
        key_columns = KEYS.get(file.name)

        if key_columns:

            duplicate_keys = int(
                df.duplicated(subset=key_columns).sum()
            )

            key_report.append({
                "dataset": file.name,
                "candidate_key": ", ".join(key_columns),
                "duplicate_key_records": duplicate_keys
            })

        # Free memory
        del df

    # ======================================
    # 4. COLUMN LEVEL QUALITY REPORT
    # ======================================

    total_columns = len(column_types)

    total_missing = sum(missing_counts.values())

    for col, dtype in column_types.items():

        missing = missing_counts.get(col, 0)

        missing_percentage = (
            (missing / row_count) * 100
            if row_count > 0 else 0
        )

        column_report.append({
            "dataset": file.name,
            "column": col,
            "data_type": dtype,
            "missing_values": missing,
            "missing_percentage": round(
                missing_percentage, 2
            ),
            "unique_values": unique_counts.get(
                col, "Not calculated"
            )
        })

    # ======================================
    # 5. DATASET LEVEL SUMMARY
    # ======================================

    summary_report.append({
        "dataset": file.name,
        "total_rows": row_count,
        "total_columns": total_columns,
        "total_missing_values": total_missing,
        "duplicate_rows": total_duplicates,
        "file_size_MB": round(
            file.stat().st_size / (1024 * 1024), 2
        )
    })

    print("Rows:", row_count)
    print("Columns:", total_columns)
    print("Missing values:", total_missing)
    print("Duplicate rows:", total_duplicates)

# ==========================================
# 6. EXPORT REPORTS
# ==========================================

summary_df = pd.DataFrame(summary_report)

column_df = pd.DataFrame(column_report)

key_df = pd.DataFrame(key_report)

summary_df.to_csv(
    OUTPUT_DIR / "data_quality_summary.csv",
    index=False
)

column_df.to_csv(
    OUTPUT_DIR / "column_quality_report.csv",
    index=False
)

key_df.to_csv(
    OUTPUT_DIR / "primary_key_validation.csv",
    index=False
)

# ==========================================
# 7. FINAL RESULTS
# ==========================================

print("\n" + "=" * 70)
print("DATA QUALITY SUMMARY")
print("=" * 70)

print(summary_df.to_string(index=False))

print("\nREPORTS SAVED SUCCESSFULLY!")

print("1. data_quality_summary.csv")
print("2. column_quality_report.csv")
print("3. primary_key_validation.csv")

print("\nOUTPUT LOCATION:")
print(OUTPUT_DIR)

print("\nDATA QUALITY ANALYSIS COMPLETED!")
