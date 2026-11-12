
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
EDA_DIR = BASE_DIR / "visualizations" / "eda_data"
REPORT_DIR = BASE_DIR / "report"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD ANALYSIS FILES
# --------------------------------------------------

orders = pd.read_csv(DATA_DIR / "cleaned_orders.csv")
monthly = pd.read_csv(EDA_DIR / "monthly_order_trend.csv")
states = pd.read_csv(EDA_DIR / "delivery_performance_by_state.csv")
categories = pd.read_csv(EDA_DIR / "product_category_analysis.csv")
reviews = pd.read_csv(EDA_DIR / "review_score_distribution.csv")

# --------------------------------------------------
# 3. DELIVERY PERFORMANCE
# --------------------------------------------------

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"], errors="coerce"
)

orders["order_estimated_delivery_date"] = pd.to_datetime(
    orders["order_estimated_delivery_date"], errors="coerce"
)

delivered = orders[
    (orders["order_status"] == "delivered")
    & orders["order_delivered_customer_date"].notna()
    & orders["order_estimated_delivery_date"].notna()
].copy()

delivered["delivery_days"] = (
    delivered["order_delivered_customer_date"]
    - pd.to_datetime(delivered["order_purchase_timestamp"])
).dt.total_seconds() / 86400

delivered["delay_days"] = (
    delivered["order_delivered_customer_date"]
    - delivered["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

late_orders = delivered[delivered["delay_days"] > 0]
on_time_early = delivered[delivered["delay_days"] <= 0]

late_percentage = len(late_orders) / len(delivered) * 100

# --------------------------------------------------
# 4. MONTHLY ORDER TREND
# --------------------------------------------------

peak_month = monthly.loc[monthly["total_orders"].idxmax()]
first_month = monthly.iloc[0]
last_month = monthly.iloc[-1]

# --------------------------------------------------
# 5. STATE DELIVERY COMPARISON
# --------------------------------------------------

eligible_states = states[states["delivered_orders"] >= 100].copy()

slowest_state = eligible_states.loc[
    eligible_states["average_delivery_days"].idxmax()
]

fastest_state = eligible_states.loc[
    eligible_states["average_delivery_days"].idxmin()
]

# --------------------------------------------------
# 6. PRODUCT CATEGORY
# --------------------------------------------------

top_category = categories.loc[
    categories["product_revenue"].idxmax()
]

second_category = categories.nlargest(2, "product_revenue").iloc[1]

# --------------------------------------------------
# 7. REVIEW SCORES
# --------------------------------------------------

total_reviews = reviews["review_count"].sum()

five_star = reviews.loc[
    reviews["review_score"] == 5, "review_count"
].sum()

one_star = reviews.loc[
    reviews["review_score"] == 1, "review_count"
].sum()

average_score = (
    reviews["review_score"] * reviews["review_count"]
).sum() / total_reviews

five_star_percentage = five_star / total_reviews * 100
one_star_percentage = one_star / total_reviews * 100

# --------------------------------------------------
# 8. CREATE BUSINESS INSIGHTS
# --------------------------------------------------

report = []

report.append("BUSINESS INSIGHTS AND RECOMMENDATIONS")
report.append("=" * 65)

report.append("\n1. ORDER DEMAND")
report.append(
    f"The highest order volume occurred in {peak_month['purchase_month']}, "
    f"with {int(peak_month['total_orders']):,} orders."
)
report.append(
    f"The first month in the dataset is {first_month['purchase_month']} "
    f"({int(first_month['total_orders']):,} orders)."
)
report.append(
    f"The last month in the dataset is {last_month['purchase_month']} "
    f"({int(last_month['total_orders']):,} orders)."
)
report.append(
    "The first and last months may cover incomplete periods. "
    "Their low counts should be checked before drawing demand conclusions."
)

report.append("\n2. DELIVERY PERFORMANCE")
report.append(
    f"Of {len(delivered):,} eligible delivered orders, "
    f"{len(late_orders):,} were late ({late_percentage:.2f}%)."
)
report.append(
    f"{len(on_time_early):,} orders were delivered on time or early."
)
report.append(
    "Recommendation: investigate late deliveries by destination, "
    "seller, and order period to identify where delays are concentrated."
)

report.append("\n3. GEOGRAPHICAL PERFORMANCE")
report.append(
    f"{slowest_state['customer_state']} had the highest average delivery "
    f"time among states with at least 100 eligible orders "
    f"({slowest_state['average_delivery_days']:.2f} days)."
)
report.append(
    f"{fastest_state['customer_state']} had the lowest average delivery "
    f"time among the same group "
    f"({fastest_state['average_delivery_days']:.2f} days)."
)
report.append(
    "Recommendation: review delivery routes, distance, seller locations, "
    "and carrier performance in slower destinations. The state comparison "
    "shows an association, not the cause of delays."
)

report.append("\n4. PRODUCT CATEGORY PERFORMANCE")
report.append(
    f"{top_category['category']} ranked first by recorded item revenue, "
    f"at R${top_category['product_revenue']:,.2f}."
)
report.append(
    f"{second_category['category']} ranked second by recorded item revenue, "
    f"at R${second_category['product_revenue']:,.2f}."
)
report.append(
    "Recommendation: use category demand when planning inventory and "
    "fulfilment capacity, while considering seasonality and stock availability."
)

report.append("\n5. CUSTOMER REVIEW PATTERNS")
report.append(
    f"The weighted average review score was {average_score:.2f} out of 5."
)
report.append(
    f"Five-star reviews: {five_star:,} ({five_star_percentage:.2f}%)."
)
report.append(
    f"One-star reviews: {one_star:,} ({one_star_percentage:.2f}%)."
)
report.append(
    "Recommendation: examine low-score orders alongside delivery delays "
    "and review comments to identify possible service issues. "
    "Do not assume delivery delay is the only reason for low scores."
)

report.append("\n6. FREIGHT CHARGE INTERPRETATION")
report.append(
    "The dataset records freight charges paid or associated with orders. "
    "These values should not be treated as the logistics company's actual "
    "internal transportation costs or profit."
)
report.append(
    "Recommendation: compare freight charges by destination, order weight, "
    "and product category to understand customer-facing shipping patterns."
)

report.append("\n7. PROJECT LIMITATIONS")
report.append(
    "- The dataset represents Brazilian e-commerce activity, not global logistics."
)
report.append(
    "- The data covers a historical period and may not represent current operations."
)
report.append(
    "- Some order timestamps and product measurements are missing."
)
report.append(
    "- Date sequence inconsistencies were flagged and not automatically removed."
)
report.append(
    "- Duplicate review IDs were retained for investigation."
)
report.append(
    "- Freight charges do not provide actual carrier operating costs."
)
report.append(
    "- The analysis identifies patterns and associations, not proven causes."
)

report.append("\nBUSINESS INSIGHT ANALYSIS COMPLETED.")

report_text = "\n".join(report)

output_path = REPORT_DIR / "business_insights_recommendations.txt"
output_path.write_text(report_text, encoding="utf-8")

print(report_text)
print("\nReport saved to:", output_path)
