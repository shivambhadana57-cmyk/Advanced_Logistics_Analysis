
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --------------------------------------------------
# 1. PATHS AND SETTINGS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
EDA_DIR = BASE_DIR / "visualizations" / "eda_data"
OUTPUT_DIR = BASE_DIR / "visualizations" / "charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")

def save_chart(filename):
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {filename}")

# --------------------------------------------------
# 2. MONTHLY ORDER TREND
# --------------------------------------------------

monthly = pd.read_csv(EDA_DIR / "monthly_order_trend.csv")

plt.figure(figsize=(13, 6))
sns.lineplot(
    data=monthly,
    x="purchase_month",
    y="total_orders",
    marker="o"
)

plt.title("Monthly E-Commerce Order Trend", fontsize=16)
plt.xlabel("Purchase Month")
plt.ylabel("Number of Orders")
plt.xticks(rotation=60, ha="right")

save_chart("01_monthly_order_trend.png")

# --------------------------------------------------
# 3. DELIVERY OUTCOMES
# --------------------------------------------------

orders = pd.read_csv(
    BASE_DIR / "data" / "processed" / "cleaned_orders.csv"
)

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

delivered["delay_days"] = (
    delivered["order_delivered_customer_date"]
    - delivered["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

delivered["delivery_result"] = delivered["delay_days"].apply(
    lambda value: "Late" if value > 0 else "On time or early"
)

delivery_counts = (
    delivered["delivery_result"]
    .value_counts()
    .rename_axis("delivery_result")
    .reset_index(name="orders")
)

plt.figure(figsize=(8, 6))
ax = sns.barplot(
    data=delivery_counts,
    x="delivery_result",
    y="orders"
)

plt.title("Delivered Orders: Late vs On Time or Early", fontsize=15)
plt.xlabel("Delivery Result")
plt.ylabel("Number of Orders")

for container in ax.containers:
    ax.bar_label(container, fmt="%.0f")

save_chart("02_delivery_outcomes.png")

# --------------------------------------------------
# 4. DELIVERY PERFORMANCE BY STATE
# --------------------------------------------------

state_data = pd.read_csv(
    EDA_DIR / "delivery_performance_by_state.csv"
)

# Exclude states with fewer than 100 eligible delivered orders
# to reduce misleading averages from very small samples.
state_data = state_data[
    state_data["delivered_orders"] >= 100
].copy()

slowest_states = state_data.nlargest(
    10, "average_delivery_days"
).sort_values("average_delivery_days")

plt.figure(figsize=(10, 7))
sns.barplot(
    data=slowest_states,
    x="average_delivery_days",
    y="customer_state"
)

plt.title(
    "10 States with the Highest Average Delivery Time\n"
    "(Minimum 100 Eligible Delivered Orders)",
    fontsize=14
)
plt.xlabel("Average Delivery Time (Days)")
plt.ylabel("Customer State")

save_chart("03_slowest_delivery_states.png")

# --------------------------------------------------
# 5. PRODUCT CATEGORY REVENUE
# --------------------------------------------------

categories = pd.read_csv(
    EDA_DIR / "product_category_analysis.csv"
)

top_categories = categories.nlargest(
    10, "product_revenue"
).sort_values("product_revenue")

plt.figure(figsize=(11, 7))
sns.barplot(
    data=top_categories,
    x="product_revenue",
    y="category"
)

plt.title("Top 10 Product Categories by Recorded Item Revenue", fontsize=14)
plt.xlabel("Recorded Product Revenue (R$)")
plt.ylabel("Product Category")

save_chart("04_top_product_categories.png")

# --------------------------------------------------
# 6. REVIEW SCORE DISTRIBUTION
# --------------------------------------------------

reviews = pd.read_csv(
    EDA_DIR / "review_score_distribution.csv"
)

reviews["review_score"] = reviews["review_score"].astype(str)

plt.figure(figsize=(8, 6))
ax = sns.barplot(
    data=reviews,
    x="review_score",
    y="review_count"
)

plt.title("Customer Review Score Distribution", fontsize=15)
plt.xlabel("Review Score (1 to 5)")
plt.ylabel("Number of Reviews")

for container in ax.containers:
    ax.bar_label(container, fmt="%.0f")

save_chart("05_review_score_distribution.png")

# --------------------------------------------------
# 7. COMPLETION MESSAGE
# --------------------------------------------------

print("\n" + "=" * 55)
print("VISUALIZATION GENERATION COMPLETED")
print("=" * 55)

print("Charts saved in:", OUTPUT_DIR)

print("\nGenerated charts:")
for file in sorted(OUTPUT_DIR.glob("*.png")):
    print("-", file.name)
