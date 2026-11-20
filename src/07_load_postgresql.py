
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ==========================================
# 1. CONFIGURATION
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_DIR / "data" / "processed" / "cleaned"

load_dotenv(PROJECT_DIR / ".env")

connection_url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME")
)

engine = create_engine(connection_url)

# ==========================================
# 2. DATASET LOADING ORDER
# ==========================================

datasets = [
    ("olist_customers_dataset.csv", "customers"),
    ("olist_products_dataset.csv", "products"),
    ("olist_sellers_dataset.csv", "sellers"),
    ("product_category_name_translation.csv", "category_translation"),
    ("olist_geolocation_dataset.csv", "geolocation"),
    ("olist_orders_dataset.csv", "orders"),
    ("olist_order_items_dataset.csv", "order_items"),
    ("olist_order_payments_dataset.csv", "payments"),
    ("olist_order_reviews_dataset.csv", "reviews")
]

# ==========================================
# 3. COLUMN MAPPING
# ==========================================

COLUMN_MAPPING = {
    "customers": {
        "customer_id": "customer_id",
        "customer_unique_id": "customer_unique_id",
        "customer_zip_code_prefix": "customer_zip_code_prefix",
        "customer_city": "customer_city",
        "customer_state": "customer_state"
    },

    "products": {
        "product_id": "product_id",
        "product_category_name": "product_category_name",
        "product_name_lenght": "product_name_lenght",
        "product_description_lenght": "product_description_lenght",
        "product_photos_qty": "product_photos_qty",
        "product_weight_g": "product_weight_g",
        "product_length_cm": "product_length_cm",
        "product_height_cm": "product_height_cm",
        "product_width_cm": "product_width_cm"
    },

    "sellers": {
        "seller_id": "seller_id",
        "seller_zip_code_prefix": "seller_zip_code_prefix",
        "seller_city": "seller_city",
        "seller_state": "seller_state"
    },

    "category_translation": {
        "product_category_name": "product_category_name",
        "product_category_name_english": "product_category_name_english"
    },

    "geolocation": {
        "geolocation_zip_code_prefix": "geolocation_zip_code_prefix",
        "geolocation_lat": "geolocation_lat",
        "geolocation_lng": "geolocation_lng",
        "geolocation_city": "geolocation_city",
        "geolocation_state": "geolocation_state"
    },

    "orders": {
        "order_id": "order_id",
        "customer_id": "customer_id",
        "order_status": "order_status",
        "order_purchase_timestamp": "order_purchase_timestamp",
        "order_approved_at": "order_approved_at",
        "order_delivered_carrier_date": "order_delivered_carrier_date",
        "order_delivered_customer_date": "order_delivered_customer_date",
        "order_estimated_delivery_date": "order_estimated_delivery_date"
    },

    "order_items": {
        "order_id": "order_id",
        "order_item_id": "order_item_id",
        "product_id": "product_id",
        "seller_id": "seller_id",
        "shipping_limit_date": "shipping_limit_date",
        "price": "price",
        "freight_value": "freight_value"
    },

    "payments": {
        "order_id": "order_id",
        "payment_sequential": "payment_sequential",
        "payment_type": "payment_type",
        "payment_installments": "payment_installments",
        "payment_value": "payment_value"
    },

    "reviews": {
        "review_id": "review_id",
        "order_id": "order_id",
        "review_score": "review_score",
        "review_comment_title": "review_comment_title",
        "review_comment_message": "review_comment_message",
        "review_creation_date": "review_creation_date",
        "review_answer_timestamp": "review_answer_timestamp"
    }
}

# ==========================================
# 4. CHECK DATABASE TABLES ARE EMPTY
# ==========================================

print("=" * 65)
print("OLIST POSTGRESQL ETL PIPELINE")
print("=" * 65)

with engine.connect() as connection:

    for _, table in datasets:

        count = connection.execute(
            text(f'SELECT COUNT(*) FROM public."{table}"')
        ).scalar_one()

        if count != 0:
            raise RuntimeError(
                f"Table {table} is not empty ({count} rows). "
                "Stop loading to avoid duplicates."
            )

# ==========================================
# 5. LOAD DATASETS
# ==========================================

load_summary = []

try:

    for filename, table in datasets:

        file_path = RAW_DIR / filename

        print("\n" + "-" * 65)
        print("Loading:", filename)
        print("Target table:", table)

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        total_loaded = 0

        # Load large geolocation dataset in chunks
        if table == "geolocation":

            chunks = pd.read_csv(
                file_path,
                chunksize=50000,
                low_memory=False
            )

            for chunk in chunks:

                chunk = chunk.rename(
                    columns=COLUMN_MAPPING[table]
                )

                # Each chunk is committed together
                with engine.begin() as connection:

                    chunk.to_sql(
                        name=table,
                        con=connection,
                        schema="public",
                        if_exists="append",
                        index=False,
                        chunksize=5000,
                        method="multi"
                    )

                total_loaded += len(chunk)

                print(
                    f"Loaded: {total_loaded:,} records"
                )

        else:

            df = pd.read_csv(
                file_path,
                low_memory=False
            )

            df = df.rename(
                columns=COLUMN_MAPPING[table]
            )

            with engine.begin() as connection:

                df.to_sql(
                    name=table,
                    con=connection,
                    schema="public",
                    if_exists="append",
                    index=False,
                    chunksize=5000,
                    method="multi"
                )

            total_loaded = len(df)

            del df

        load_summary.append({
            "table": table,
            "records_loaded": total_loaded,
            "status": "SUCCESS"
        })

        print("Successfully loaded:", total_loaded)

    print("\nALL DATASETS LOADED SUCCESSFULLY!")

except Exception as error:

    print("\nETL PIPELINE FAILED")
    print("Error:", error)

    raise

finally:

    engine.dispose()

# ==========================================
# 6. EXPORT LOADING SUMMARY
# ==========================================

summary = pd.DataFrame(load_summary)

summary_path = (
    PROJECT_DIR / "data" / "processed"
    / "postgresql_load_summary.csv"
)

summary.to_csv(summary_path, index=False)

print("\nLOADING SUMMARY")
print(summary.to_string(index=False))

print("\nSaved:", summary_path)
