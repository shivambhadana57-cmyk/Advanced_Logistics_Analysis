# Python Code – Logistics Performance Analysis

This folder contains the six Python scripts developed for the Advanced Logistics Performance Analysis project.

## Scripts and Their Purpose

| Script | Description |
|---|---|
| `01_dataset_inspection.py` | Loads and inspects the nine datasets. |
| `02_data_quality_assessment.py` | Checks missing values, duplicates, date inconsistencies, and data quality. |
| `03_cleaning_preprocessing.py` | Cleans and prepares datasets for analysis. |
| `04_exploratory_data_analysis.py` | Performs exploratory analysis and generates summary CSV files. |
| `05_create_visualizations.py` | Creates five charts using Matplotlib and Seaborn. |
| `06_business_insights.py` | Summarizes findings and generates business recommendations. |

## Requirements

The project uses the following Python libraries:

- pandas
- numpy
- matplotlib
- seaborn

Install the required libraries from the project root directory:

```bash
pip install -r requirements.txt
```

## How to Run

Open the VS Code terminal in the main project folder and execute the scripts in sequence.

Example:

```bash
python python_code/01_dataset_inspection.py
```

Continue with the remaining scripts in numerical order.

## Output

The scripts generate cleaned datasets, EDA summary files, charts, and analytical reports in their respective project folders.

**Note:** The original dataset must be downloaded separately and placed in `data/raw/` before running the scripts.
