
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD DATASETS
# --------------------------------------------------

files = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}

data = {}

print("=" * 60)
print("LOADING DATASETS")
print("=" * 60)

for name, filename in files.items():
    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    data[name] = pd.read_csv(path)
    print(f"{name}: {data[name].shape[0]:,} rows loaded")

# --------------------------------------------------
# 3. CLEAN DATE COLUMNS
# --------------------------------------------------

orders = data["orders"].copy()

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

# --------------------------------------------------
# 4. FLAG DATE INCONSISTENCIES
# --------------------------------------------------

orders["flag_carrier_before_approval"] = (
    orders["order_delivered_carrier_date"]
    < orders["order_approved_at"]
)

orders["flag_customer_before_carrier"] = (
    orders["order_delivered_customer_date"]
    < orders["order_delivered_carrier_date"]
)

# --------------------------------------------------
# 5. CREATE DELIVERY ANALYSIS COLUMNS
# --------------------------------------------------

orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / 86400

orders["delay_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

# Negative delay = delivered early
# Zero delay = delivered on estimated date
# Positive delay = delivered late

# --------------------------------------------------
# 6. CHECK PRODUCT DATA
# --------------------------------------------------

products = data["products"].copy()

product_measurements = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

for column in product_measurements:
    products[f"flag_{column}_missing"] = products[column].isna()

    products[f"flag_{column}_zero"] = (
        products[column] == 0
    )

# Keep missing and zero measurements unchanged.
# Do not replace them with invented values.

# --------------------------------------------------
# 7. INVESTIGATE DUPLICATE REVIEW IDs
# --------------------------------------------------

reviews = data["reviews"].copy()

duplicate_review_mask = reviews["review_id"].duplicated(
    keep=False
)

duplicate_reviews = reviews[duplicate_review_mask].copy()

reviews["flag_duplicate_review_id"] = duplicate_review_mask

duplicate_reviews.to_csv(
    PROCESSED_DIR / "reviews_duplicate_ids_for_review.csv",
    index=False
)

# Keep all review records until duplicate IDs
# have been investigated.

# --------------------------------------------------
# 8. REMOVE EXACT GEOLOCATION DUPLICATES
# --------------------------------------------------

geolocation = data["geolocation"].copy()

geo_before = len(geolocation)

geolocation = geolocation.drop_duplicates()

geo_after = len(geolocation)

geo_removed = geo_before - geo_after

# Repeated postal codes are retained.
# Only completely identical rows are removed.

# --------------------------------------------------
# 9. SAVE PROCESSED DATASETS
# --------------------------------------------------

processed_data = {
    "orders": orders,
    "order_items": data["order_items"].copy(),
    "products": products,
    "customers": data["customers"].copy(),
    "sellers": data["sellers"].copy(),
    "reviews": reviews,
    "geolocation": geolocation,
    "payments": data["payments"].copy(),
    "category_translation": data["category_translation"].copy()
}

print("\n" + "=" * 60)
print("SAVING PROCESSED DATASETS")
print("=" * 60)

for name, df in processed_data.items():
    output_path = PROCESSED_DIR / f"cleaned_{name}.csv"

    df.to_csv(output_path, index=False)

    print(f"Saved: {output_path.name} | {len(df):,} rows")

# --------------------------------------------------
# 10. CREATE CLEANING SUMMARY REPORT
# --------------------------------------------------

report = []

report.append("LOGISTICS DATA CLEANING AND PREPROCESSING REPORT")
report.append("=" * 60)

report.append("\n1. DATE PROCESSING")
report.append("Five order date columns converted to datetime format.")
report.append(
    f"Carrier-before-approval flags: "
    f"{orders['flag_carrier_before_approval'].sum():,}"
)
report.append(
    f"Customer-before-carrier flags: "
    f"{orders['flag_customer_before_carrier'].sum():,}"
)

report.append("\n2. DELIVERY ANALYSIS COLUMNS")
report.append("Created delivery_days and delay_days.")
report.append(
    f"Orders with calculated delivery days: "
    f"{orders['delivery_days'].notna().sum():,}"
)

report.append("\n3. PRODUCT MEASUREMENTS")
for column in product_measurements:
    report.append(
        f"{column}: missing={products[column].isna().sum():,}, "
        f"zero={(products[column] == 0).sum():,}"
    )

report.append("\n4. REVIEW ID INVESTIGATION")
report.append(
    f"Rows with duplicated review IDs: "
    f"{duplicate_review_mask.sum():,}"
)
report.append(
    f"Distinct duplicated review IDs: "
    f"{reviews.loc[duplicate_review_mask, 'review_id'].nunique():,}"
)
report.append(
    "Duplicate review records exported separately for investigation."
)
report.append("No review records were deleted.")

report.append("\n5. GEOLOCATION PROCESSING")
report.append(f"Rows before exact duplicate removal: {geo_before:,}")
report.append(f"Exact duplicate rows removed: {geo_removed:,}")
report.append(f"Rows after removal: {geo_after:,}")
report.append("Repeated postal code records were retained.")

report.append("\n6. DATA PRESERVATION")
report.append("Original raw CSV files were not modified.")
report.append("Missing values were not filled with invented values.")
report.append("Date inconsistencies were flagged, not deleted.")
report.append("All processed datasets were saved separately.")

report.append("\nDATA CLEANING PROCESS COMPLETED.")

report_text = "\n".join(report)

report_path = (
    BASE_DIR / "report" / "cleaning_preprocessing_report.txt"
)

report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(report_text, encoding="utf-8")

print("\n" + report_text)
print(f"\nReport saved to: {report_path}")

