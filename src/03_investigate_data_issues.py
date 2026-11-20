
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ======================================
# TASK 1: INVESTIGATE REVIEW DUPLICATES
# ======================================

print("\n1. REVIEW DATASET INVESTIGATION")

reviews = pd.read_csv(
    RAW_DIR / "olist_order_reviews_dataset.csv"
)

print("\nTotal review records:", len(reviews))

print("Unique review IDs:", reviews["review_id"].nunique())

print("Unique order IDs:", reviews["order_id"].nunique())

print(
    "Duplicate review IDs:",
    reviews.duplicated(subset=["review_id"]).sum()
)

# Inspect duplicate review IDs
duplicate_reviews = reviews[
    reviews.duplicated(
        subset=["review_id"],
        keep=False
    )
].sort_values("review_id")

print("\nDuplicate review records:")
print(duplicate_reviews.head(20).to_string(index=False))

# Test composite key
print(
    "\nDuplicate review_id + order_id combinations:",
    reviews.duplicated(
        subset=["review_id", "order_id"]
    ).sum()
)

duplicate_reviews.to_csv(
    OUTPUT_DIR / "duplicate_reviews_investigation.csv",
    index=False
)

# ======================================
# TASK 2: INVESTIGATE GEOLOCATION
# ======================================

print("\n\n2. GEOLOCATION INVESTIGATION")

geo = pd.read_csv(
    RAW_DIR / "olist_geolocation_dataset.csv"
)

print("\nTotal geolocation records:", len(geo))

print(
    "Duplicate complete rows:",
    geo.duplicated().sum()
)

print(
    "Unique ZIP codes:",
    geo["geolocation_zip_code_prefix"].nunique()
)

# Count ZIP codes occurring more than once
zip_counts = (
    geo.groupby("geolocation_zip_code_prefix")
    .size()
    .reset_index(name="record_count")
)

repeated_zips = zip_counts[
    zip_counts["record_count"] > 1
]

print(
    "ZIP codes with multiple records:",
    len(repeated_zips)
)

repeated_zips.to_csv(
    OUTPUT_DIR / "repeated_geolocation_zip_codes.csv",
    index=False
)

# ======================================
# TASK 3: INVESTIGATE ORDER STATUSES
# ======================================

print("\n\n3. ORDER STATUS INVESTIGATION")

orders = pd.read_csv(
    RAW_DIR / "olist_orders_dataset.csv"
)

print("\nOrder status counts:")

print(
    orders["order_status"]
    .value_counts(dropna=False)
)

# Missing delivery dates by order status
print("\nMissing dates by order status:")

date_columns = [
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date"
]

status_report = (
    orders.groupby("order_status")[date_columns]
    .agg(lambda col: col.isna().sum())
)

print(status_report)

status_report.to_csv(
    OUTPUT_DIR / "order_status_missing_dates.csv"
)

# ======================================
# TASK 4: INVESTIGATE PRODUCTS
# ======================================

print("\n\n4. PRODUCT DATA INVESTIGATION")

products = pd.read_csv(
    RAW_DIR / "olist_products_dataset.csv"
)

print("\nMissing product values:")

print(products.isnull().sum())

print(
    "\nProducts with missing categories:",
    products["product_category_name"].isna().sum()
)

print(
    "Duplicate product IDs:",
    products["product_id"].duplicated().sum()
)

print("\nINVESTIGATION COMPLETED")

print("Check the generated CSV files inside:")
print(OUTPUT_DIR)
