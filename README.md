# Advanced Logistics Performance Analysis Using Python

### Delivery Efficiency, Freight Charges and Operational Insights

## Project Overview

This project focuses on analysing logistics and e-commerce operations using the Olist Brazilian E-Commerce Public Dataset. The main objective is to examine delivery performance, freight charges, customer reviews, product categories, and geographical differences to identify useful business insights.

Python was used to inspect, clean, process, analyse, and visualize the datasets. The project also includes practical recommendations for improving logistics monitoring and operational decision-making.

## Project Objectives

- Inspect and understand multiple related datasets.
- Identify missing values, duplicate records, and data inconsistencies.
- Clean and preprocess data for reliable analysis.
- Analyse delivery time and late delivery performance.
- Examine freight charges and payment information.
- Identify high-performing product categories.
- Study geographical delivery differences.
- Analyse customer review patterns.
- Present findings through charts and business recommendations.

## Dataset Information

**Dataset:** Olist Brazilian E-Commerce Public Dataset

**Source:** [Kaggle – Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

The dataset contains nine related CSV files covering orders, order items, customers, sellers, products, payments, reviews, geolocation, and product category translations.

The dataset represents Brazilian e-commerce activity from 2016 to 2018.

**License:** CC BY-NC-SA 4.0. Please follow the dataset's attribution and license requirements.

## Tools and Technologies

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- VS Code
- Git and GitHub

## Project Workflow

1. Dataset Inspection – Loaded and examined all nine CSV files.
2. Data Quality Assessment – Checked missing values, duplicate records, date sequences, and data consistency.
3. Data Cleaning and Preprocessing – Prepared cleaned datasets and calculated delivery-related metrics.
4. Exploratory Data Analysis – Examined order trends, delivery performance, freight charges, product categories, and customer reviews.
5. Data Visualization – Created five charts to present important analytical findings.
6. Business Insights – Summarized findings and developed practical recommendations.

## Key Findings

- Total unique orders: 99,441
- Delivered orders: 96,478
- Eligible delivered orders for delay analysis: 96,470
- Average delivery time: 12.56 days
- Late deliveries: 7,826 (8.11%)
- On-time or early deliveries: 88,644
- Average customer review score: 4.09 out of 5
- Highest-revenue product category: Health and Beauty
- Highest monthly order volume: November 2017, with 7,544 orders

The freight values represent recorded shipping charges, not actual internal carrier operating costs. Product category revenue represents recorded item prices, not profit.

## Visualizations

Five charts were created:

1. Monthly Order Trend
2. Delivery Outcomes
3. Slowest Delivery States
4. Top Product Categories
5. Customer Review Distribution

All chart images are available in the `visualizations/charts/` folder.


## Installation and Execution

**Step 1: Clone the repository**

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

**Step 2: Open the project folder**

```bash
cd Advanced_Logistics_Analysis
```

**Step 3: Install the required libraries**

```bash
pip install -r requirements.txt
```

**Step 4: Download the dataset**

Download the Olist dataset from Kaggle and place the original CSV files inside `data/raw/`.

**Step 5: Run the Python scripts**

Run the scripts from the project root directory in the following order:

```bash
python python_code/01_dataset_inspection.py
python python_code/02_data_quality_assessment.py
python python_code/03_cleaning_preprocessing.py
python python_code/04_exploratory_data_analysis.py
python python_code/05_create_visualizations.py
python python_code/06_business_insights.py
```

## Project Outputs

The project generates:

- Cleaned datasets in `data/processed/`
- EDA summary CSV files in `visualizations/eda_data/`
- Five charts in `visualizations/charts/`
- Analytical text reports in `report/`

## Limitations

The analysis is based on historical Brazilian e-commerce data from 2016–2018. Some timestamps and product measurements are missing, and certain date inconsistencies exist. The dataset does not provide actual internal carrier operating costs or complete route information.

The findings identify patterns and relationships but do not establish direct causes.

## Future Improvements

- Delivery time prediction using machine learning.
- Late delivery risk classification.
- Geographical route analysis.
- Carrier performance evaluation.
- Freight cost optimization using actual operating cost data.
- Interactive Power BI dashboard.

## Acknowledgement

The project uses the Olist Brazilian E-Commerce Public Dataset. Credit is given to Olist and the dataset contributors. The dataset is used subject to its stated license.

---

**Project Category:** Data Analytics / Logistics Analytics

**Developed Using:** Python
