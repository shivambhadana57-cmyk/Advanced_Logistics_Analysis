
import pandas as pd
from pathlib import Path
from contextlib import redirect_stdout

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORT_DIR = PROJECT_DIR / "report"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

output_file = REPORT_DIR / "data_quality_assessment.txt"


def load_file(filename):
    return pd.read_csv(DATA_DIR / filename)


def section(title):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)


def inspect_data_quality():

    # Load the main datasets
    orders = load_file("olist_orders_dataset.csv")
    items = load_file("olist_order_items_dataset.csv")
    products = load_file("olist_products_dataset.csv")
    customers = load_file("olist_customers_dataset.csv")
    sellers = load_file("olist_sellers_dataset.csv")
    reviews = load_file("olist_order_reviews_dataset.csv")

    # 1. Order status analysis
    section("1. ORDER STATUS ANALYSIS")

    print(orders["order_status"].value_counts(dropna=False))

    print("\nMissing delivery dates by order status:")

    print(
        orders.groupby("order_status")[
            "order_delivered_customer_date"
        ].apply(lambda x: x.isna().sum())
    )

    # 2. Date quality analysis
    section("2. DATE QUALITY ANALYSIS")

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for col in date_columns:

        parsed = pd.to_datetime(orders[col], errors="coerce")

        invalid = orders[col].notna() & parsed.isna()

        print(f"\n{col}")
        print("Missing:", orders[col].isna().sum())
        print("Invalid non-empty dates:", invalid.sum())

        orders[col] = parsed

    # Check chronological event sequences
    section("3. ORDER DATE SEQUENCE CHECKS")

    date_pairs = [
        ("order_purchase_timestamp", "order_approved_at"),
        ("order_approved_at", "order_delivered_carrier_date"),
        ("order_delivered_carrier_date",
         "order_delivered_customer_date")
    ]

    for earlier, later in date_pairs:

        valid = orders[earlier].notna() & orders[later].notna()

        incorrect = (
            valid & (orders[later] < orders[earlier])
        ).sum()

        print(f"{later} before {earlier}: {incorrect}")

    # 4. Delivery performance
    section("4. DELIVERY PERFORMANCE")

    delivered = orders[
        (orders["order_status"] == "delivered")
        & orders["order_delivered_customer_date"].notna()
        & orders["order_estimated_delivery_date"].notna()
    ].copy()

    delivered["delivery_days"] = (
        delivered["order_delivered_customer_date"]
        - delivered["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    delivered["delay_days"] = (
        delivered["order_delivered_customer_date"]
        - delivered["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400

    print("Eligible delivered orders:", len(delivered))
    print("Average delivery days:",
          round(delivered["delivery_days"].mean(), 2))
    print("Median delivery days:",
          round(delivered["delivery_days"].median(), 2))
    print("Late orders:", (delivered["delay_days"] > 0).sum())
    print("On-time or early orders:",
          (delivered["delay_days"] <= 0).sum())
    print("Average delay days:",
          round(delivered["delay_days"].mean(), 2))

    # 5. Freight and price checks
    section("5. FREIGHT AND PRICE QUALITY")

    for col in ["price", "freight_value"]:

        print(f"\n{col}")
        print("Minimum:", items[col].min())
        print("Maximum:", items[col].max())
        print("Zero values:", (items[col] == 0).sum())
        print("Negative values:", (items[col] < 0).sum())

    # 6. Product quality
    section("6. PRODUCT DATA QUALITY")

    product_columns = [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    for col in product_columns:

        print(f"\n{col}")
        print("Missing:", products[col].isna().sum())
        print("Zero values:", (products[col] == 0).sum())
        print("Negative values:", (products[col] < 0).sum())

    # 7. Duplicate identifier checks
    section("7. DUPLICATE IDENTIFIER CHECKS")

    checks = {
        "Orders - order_id": (orders, ["order_id"]),
        "Customers - customer_id": (customers, ["customer_id"]),
        "Sellers - seller_id": (sellers, ["seller_id"]),
        "Products - product_id": (products, ["product_id"]),
        "Reviews - review_id": (reviews, ["review_id"]),
        "Order Items - order_id + item_id":
            (items, ["order_id", "order_item_id"])
    }

    for name, (df, columns) in checks.items():

        print(
            name + ":",
            df.duplicated(subset=columns).sum()
        )

    # 8. Relationship checks
    section("8. RELATIONSHIP / FOREIGN KEY CHECKS")

    order_ids = set(orders["order_id"])
    customer_ids = set(customers["customer_id"])
    seller_ids = set(sellers["seller_id"])
    product_ids = set(products["product_id"])

    print(
        "Items with unknown order IDs:",
        (~items["order_id"].isin(order_ids)).sum()
    )

    print(
        "Orders with unknown customer IDs:",
        (~orders["customer_id"].isin(customer_ids)).sum()
    )

    print(
        "Items with unknown seller IDs:",
        (~items["seller_id"].isin(seller_ids)).sum()
    )

    print(
        "Items with unknown product IDs:",
        (~items["product_id"].isin(product_ids)).sum()
    )

    # 9. Geolocation duplicate check
    section("9. GEOLOCATION DUPLICATE ANALYSIS")

    geo = load_file("olist_geolocation_dataset.csv")

    print("Total records:", len(geo))
    print("Exact duplicate rows:", geo.duplicated().sum())
    print(
        "Repeated postal code records:",
        geo["geolocation_zip_code_prefix"].duplicated().sum()
    )

    print("\nDATA QUALITY ASSESSMENT COMPLETED.")


with open(output_file, "w", encoding="utf-8") as report:

    with redirect_stdout(report):
        inspect_data_quality()

print("Assessment completed successfully!")
print("Saved report:", output_file)
print("\n" + output_file.read_text(encoding="utf-8"))
