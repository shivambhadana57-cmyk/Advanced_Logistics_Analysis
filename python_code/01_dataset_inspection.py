
import pandas as pd
from pathlib import Path
from contextlib import redirect_stdout

# Project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORT_DIR = PROJECT_DIR / "report"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# All nine original Olist files
files = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_products_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_payments_dataset.csv",
    "product_category_name_translation.csv"
]

output_file = REPORT_DIR / "dataset_inspection.txt"


def inspect_datasets():

    print("=" * 65)
    print("OLIST LOGISTICS DATASET - INITIAL INSPECTION")
    print("=" * 65)

    for filename in files:

        file_path = DATA_DIR / filename

        print(f"\n\nFILE: {filename}")
        print("-" * 65)

        if not file_path.exists():
            print("ERROR: File not found!")
            continue

        try:
            df = pd.read_csv(file_path)

            print("Rows and Columns:", df.shape)

            print("\nColumn Names:")
            print(list(df.columns))

            print("\nData Types:")
            print(df.dtypes.to_string())

            print("\nMissing Values:")
            missing = df.isnull().sum()
            missing = missing[missing > 0]

            if missing.empty:
                print("No missing values found.")
            else:
                print(missing.to_string())

            print("\nDuplicate Rows:", df.duplicated().sum())

            print("\nFirst 3 Records:")
            print(df.head(3).to_string(index=False))

            print("\nMemory Usage (MB):",
                  round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2))

        except Exception as error:
            print("ERROR:", error)

    print("\n\nINSPECTION COMPLETED.")


with open(output_file, "w", encoding="utf-8") as report:
    with redirect_stdout(report):
        inspect_datasets()

print("Dataset inspection completed!")
print("Results saved at:", output_file)

# Display the saved report in the terminal
print("\n" + output_file.read_text(encoding="utf-8"))
