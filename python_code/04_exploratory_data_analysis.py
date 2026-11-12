
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "report"
OUTPUT_DIR = BASE_DIR / "visualizations" / "eda_data"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_csv(filename):
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing processed file: {path}")
    return pd.read_csv(path)

# --------------------------------------------------
# 2. LOAD PROCESSED DATA
# --------------------------------------------------

print("Loading processed datasets...")

orders = load_csv("cleaned_orders.csv")
items = load_csv("cleaned_order_items.csv")
products = load_csv("cleaned_products.csv")
customers = load_csv("cleaned_customers.csv")
reviews = load_csv("cleaned_reviews.csv")
payments = load_csv("cleaned_payments.csv")
translations = load_csv("cleaned_category_translation.csv")

# Convert date columns
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"], errors="coerce"
)
orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"], errors="coerce"
)
orders["order_estimated_delivery_date"] = pd.to_datetime(
    orders["order_estimated_delivery_date"], errors="coerce"
)

# --------------------------------------------------
# 3. ORDER-LEVEL SUMMARY
# --------------------------------------------------

item_summary = items.groupby("order_id").agg(
    item_count=("order_item_id", "count"),
    product_value=("price", "sum"),
    freight_value=("freight_value", "sum")
).reset_index()

payment_summary = payments.groupby("order_id").agg(
    payment_total=("payment_value", "sum")
).reset_index()

review_summary = reviews.groupby("order_id").agg(
    average_review_score=("review_score", "mean"),
    review_count=("review_score", "count")
).reset_index()

analysis = orders.merge(item_summary, on="order_id", how="left")
analysis = analysis.merge(payment_summary, on="order_id", how="left")
analysis = analysis.merge(review_summary, on="order_id", how="left")
analysis = analysis.merge(
    customers[["customer_id", "customer_state"]],
    on="customer_id",
    how="left"
)

analysis["purchase_month"] = (
    analysis["order_purchase_timestamp"].dt.to_period("M").astype(str)
)

analysis["delivery_days"] = (
    analysis["order_delivered_customer_date"]
    - analysis["order_purchase_timestamp"]
).dt.total_seconds() / 86400

analysis["delay_days"] = (
    analysis["order_delivered_customer_date"]
    - analysis["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

delivered = analysis[
    (analysis["order_status"] == "delivered")
    & analysis["order_delivered_customer_date"].notna()
    & analysis["order_estimated_delivery_date"].notna()
].copy()

delivered["delivery_late"] = delivered["delay_days"] > 0

# --------------------------------------------------
# 4. MONTHLY ORDER TREND
# --------------------------------------------------

monthly_orders = (
    analysis.groupby("purchase_month")
    .agg(
        total_orders=("order_id", "nunique"),
        delivered_orders=("order_status", lambda x: (x == "delivered").sum())
    )
    .reset_index()
)

monthly_orders.to_csv(
    OUTPUT_DIR / "monthly_order_trend.csv", index=False
)

# --------------------------------------------------
# 5. DELIVERY PERFORMANCE BY STATE
# --------------------------------------------------

state_delivery = (
    delivered.groupby("customer_state")
    .agg(
        delivered_orders=("order_id", "nunique"),
        average_delivery_days=("delivery_days", "mean"),
        average_delay_days=("delay_days", "mean"),
        late_orders=("delivery_late", "sum")
    )
    .reset_index()
)

state_delivery["late_delivery_percentage"] = (
    state_delivery["late_orders"]
    / state_delivery["delivered_orders"] * 100
)

state_delivery = state_delivery.sort_values(
    "average_delivery_days", ascending=False
)

state_delivery.to_csv(
    OUTPUT_DIR / "delivery_performance_by_state.csv", index=False
)

# --------------------------------------------------
# 6. FREIGHT AND ORDER VALUE ANALYSIS
# --------------------------------------------------

freight_analysis = analysis[
    analysis["order_status"] == "delivered"
].copy()

freight_summary = freight_analysis[
    ["product_value", "freight_value", "payment_total"]
].describe()

freight_summary.to_csv(
    OUTPUT_DIR / "freight_and_payment_summary.csv"
)

# --------------------------------------------------
# 7. PRODUCT CATEGORY ANALYSIS
# --------------------------------------------------

items_products = items.merge(
    products[["product_id", "product_category_name"]],
    on="product_id",
    how="left"
)

items_products = items_products.merge(
    translations,
    on="product_category_name",
    how="left"
)

items_products["category"] = (
    items_products["product_category_name_english"]
    .fillna(items_products["product_category_name"])
    .fillna("Unknown")
)

category_summary = (
    items_products.groupby("category")
    .agg(
        items_sold=("order_item_id", "count"),
        product_revenue=("price", "sum"),
        freight_charges=("freight_value", "sum")
    )
    .reset_index()
    .sort_values("product_revenue", ascending=False)
)

category_summary.to_csv(
    OUTPUT_DIR / "product_category_analysis.csv", index=False
)

# --------------------------------------------------
# 8. REVIEW SCORE ANALYSIS
# --------------------------------------------------

review_scores = (
    reviews.groupby("review_score")
    .size()
    .reset_index(name="review_count")
    .sort_values("review_score")
)

review_scores.to_csv(
    OUTPUT_DIR / "review_score_distribution.csv", index=False
)

# Review scores by delivery status
review_delivery = analysis[
    analysis["average_review_score"].notna()
].groupby("order_status").agg(
    average_review_score=("average_review_score", "mean"),
    orders_with_reviews=("order_id", "nunique")
).reset_index()

review_delivery.to_csv(
    OUTPUT_DIR / "review_scores_by_order_status.csv", index=False
)

# --------------------------------------------------
# 9. WRITE EDA REPORT
# --------------------------------------------------

report = []

report.append("EXPLORATORY DATA ANALYSIS REPORT")
report.append("=" * 65)

report.append("\n1. OVERALL ORDER SUMMARY")
report.append(f"Total unique orders: {analysis['order_id'].nunique():,}")
report.append(f"Delivered orders: {(analysis['order_status'] == 'delivered').sum():,}")
report.append(f"Total order items: {len(items):,}")
report.append(f"Customer states represented: {analysis['customer_state'].nunique()}")

report.append("\n2. MONTHLY ORDER TREND")
report.append(f"Months covered: {monthly_orders['purchase_month'].nunique()}")
report.append(
    f"Highest-order month: "
    f"{monthly_orders.loc[monthly_orders['total_orders'].idxmax(), 'purchase_month']}"
)
report.append(
    f"Orders in highest month: {monthly_orders['total_orders'].max():,}"
)

report.append("\n3. DELIVERY PERFORMANCE")
report.append(f"Delivered orders eligible for delay analysis: {len(delivered):,}")
report.append(
    f"Average delivery days: {delivered['delivery_days'].mean():.2f}"
)
report.append(
    f"Median delivery days: {delivered['delivery_days'].median():.2f}"
)
report.append(
    f"Late deliveries: {delivered['delivery_late'].sum():,}"
)
report.append(
    f"On-time or early deliveries: {(~delivered['delivery_late']).sum():,}"
)
report.append(
    f"Late delivery percentage: {delivered['delivery_late'].mean() * 100:.2f}%"
)
report.append(
    f"Average delay days: {delivered['delay_days'].mean():.2f}"
)

report.append("\n4. FREIGHT AND PAYMENT")
report.append(
    f"Average freight charge per delivered order: "
    f"{freight_analysis['freight_value'].mean():.2f}"
)
report.append(
    f"Total recorded freight charges: "
    f"{freight_analysis['freight_value'].sum():,.2f}"
)
report.append(
    f"Total recorded payment value for delivered orders: "
    f"{freight_analysis['payment_total'].sum():,.2f}"
)

report.append("\n5. PRODUCT CATEGORY")
top_category = category_summary.iloc[0]
report.append(f"Top category by product revenue: {top_category['category']}")
report.append(f"Category product revenue: {top_category['product_revenue']:,.2f}")

report.append("\n6. REVIEW SCORES")
report.append(
    f"Average review score: {reviews['review_score'].mean():.2f}"
)
report.append(
    f"Most common review score: "
    f"{reviews['review_score'].mode().iloc[0]}"
)

report.append("\n7. STATE DELIVERY PERFORMANCE")
slowest_state = state_delivery.iloc[0]
fastest_state = state_delivery.loc[
    state_delivery["average_delivery_days"].idxmin()
]
report.append(
    f"Highest average delivery time: {slowest_state['customer_state']} "
    f"({slowest_state['average_delivery_days']:.2f} days)"
)
report.append(
    f"Lowest average delivery time: {fastest_state['customer_state']} "
    f"({fastest_state['average_delivery_days']:.2f} days)"
)

report.append("\n8. INTERPRETATION NOTES")
report.append(
    "Freight value represents the freight charge recorded in the dataset, "
    "not the logistics company's actual internal transportation cost."
)
report.append(
    "Delivery performance is calculated only for delivered orders with "
    "both actual and estimated delivery timestamps."
)
report.append(
    "Category revenue is the sum of recorded item prices, not company profit."
)

report.append("\nEDA COMPLETED.")

report_text = "\n".join(report)

report_path = REPORT_DIR / "exploratory_data_analysis_report.txt"
report_path.write_text(report_text, encoding="utf-8")

print("\n" + report_text)
print("\nEDA output files saved in:", OUTPUT_DIR)
print("EDA report saved in:", report_path)

