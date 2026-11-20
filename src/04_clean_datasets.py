
from pathlib import Path
import pandas as pd

# ============================================
# 1. PROJECT CONFIGURATION
# ============================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
CLEAN_DIR = PROCESSED_DIR / "cleaned"

CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# 2. DATE COLUMNS
# ============================================

DATE_COLUMNS = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ],

    "olist_order_items_dataset.csv": [
        "shipping_limit_date"
    ],

    "olist_order_reviews_dataset.csv": [
        "review_creation_date",
        "review_answer_timestamp"
    ]
}

# ============================================
# 3. CATEGORICAL COLUMNS TO TRIM
# ============================================

TEXT_COLUMNS = {
    "olist_customers_dataset.csv": [
        "customer_city",
        "customer_state"
    ],

    "olist_geolocation_dataset.csv": [
        "geolocation_city",
        "geolocation_state"
    ],

    "olist_orders_dataset.csv": [
        "order_status"
    ],

    "olist_order_payments_dataset.csv": [
        "payment_type"
    ],

    "olist_products_dataset.csv": [
        "product_category_name"
    ],

    "olist_sellers_dataset.csv": [
        "seller_city",
        "seller_state"
    ],

    "product_category_name_translation.csv": [
        "product_category_name",
        "product_category_name_english"
    ]
}

# Preserve ZIP code prefixes as text
ZIP_DTYPES = {
    "olist_customers_dataset.csv": {
        "customer_zip_code_prefix": "string"
    },

    "olist_sellers_dataset.csv": {
        "seller_zip_code_prefix": "string"
    },

    "olist_geolocation_dataset.csv": {
        "geolocation_zip_code_prefix": "string"
    }
}

# ============================================
# 4. DATA QUALITY SUMMARY
# ============================================

cleaning_summary = []

csv_files = sorted(RAW_DIR.glob("*.csv"))

print("=" * 70)
print("OLIST DATA CLEANING PROCESS")
print("=" * 70)

# ============================================
# 5. PROCESS ALL DATASETS
# ============================================

for file in csv_files:

    print(f"\nProcessing: {file.name}")

    # Read original CSV
    dtype_config = ZIP_DTYPES.get(file.name, {})

    df = pd.read_csv(
        file,
        dtype=dtype_config,
        low_memory=False
    )

    original_rows = len(df)

    # ----------------------------------------
    # STEP A: Remove exact duplicate rows
    # ----------------------------------------

    duplicates_before = int(df.duplicated().sum())

    # Only geolocation has confirmed exact duplicates
    if file.name == "olist_geolocation_dataset.csv":

        df = df.drop_duplicates(
            keep="first"
        ).copy()

    duplicates_removed = original_rows - len(df)

    # ----------------------------------------
    # STEP B: Trim categorical whitespace
    # ----------------------------------------

    for col in TEXT_COLUMNS.get(file.name, []):

        if col in df.columns:

            df[col] = df[col].str.strip()

    # ----------------------------------------
    # STEP C: Convert dates
    # ----------------------------------------

    for col in DATE_COLUMNS.get(file.name, []):

        if col in df.columns:

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )

    # ----------------------------------------
    # STEP D: Validate candidate keys
    # ----------------------------------------

    key_columns = {
        "olist_customers_dataset.csv": [
            "customer_id"
        ],

        "olist_orders_dataset.csv": [
            "order_id"
        ],

        "olist_order_items_dataset.csv": [
            "order_id",
            "order_item_id"
        ],

        "olist_order_payments_dataset.csv": [
            "order_id",
            "payment_sequential"
        ],

        "olist_order_reviews_dataset.csv": [
            "review_id",
            "order_id"
        ],

        "olist_products_dataset.csv": [
            "product_id"
        ],

        "olist_sellers_dataset.csv": [
            "seller_id"
        ],

        "product_category_name_translation.csv": [
            "product_category_name"
        ]
    }

    keys = key_columns.get(file.name)

    duplicate_keys = None

    if keys:

        duplicate_keys = int(
            df.duplicated(subset=keys).sum()
        )

    # ----------------------------------------
    # STEP E: Save cleaned dataset
    # ----------------------------------------

    output_path = CLEAN_DIR / file.name

    df.to_csv(
        output_path,
        index=False,
        date_format="%Y-%m-%d %H:%M:%S"
    )

    # ----------------------------------------
    # STEP F: Record cleaning results
    # ----------------------------------------

    cleaning_summary.append({
        "dataset": file.name,
        "original_rows": original_rows,
        "cleaned_rows": len(df),
        "exact_duplicates_found": duplicates_before,
        "duplicates_removed": duplicates_removed,
        "missing_values_remaining": int(
            df.isnull().sum().sum()
        ),
        "duplicate_candidate_keys": duplicate_keys
    })

    print("Original rows:", original_rows)
    print("Cleaned rows:", len(df))
    print("Duplicates removed:", duplicates_removed)
    print(
        "Missing values preserved:",
        int(df.isnull().sum().sum())
    )

    if keys:
        print("Duplicate candidate keys:", duplicate_keys)

    print("Saved:", output_path)

    del df

# ============================================
# 6. EXPORT CLEANING SUMMARY
# ============================================

summary_df = pd.DataFrame(cleaning_summary)

summary_path = PROCESSED_DIR / "cleaning_summary.csv"

summary_df.to_csv(
    summary_path,
    index=False
)

print("\n" + "=" * 70)
print("CLEANING SUMMARY")
print("=" * 70)

print(summary_df.to_string(index=False))

print("\nCLEANING COMPLETED SUCCESSFULLY!")
print("Cleaned datasets:", CLEAN_DIR)
print("Summary report:", summary_path)
