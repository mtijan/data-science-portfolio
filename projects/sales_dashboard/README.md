# Sales Performance Dashboard

Project ini membangun dashboard penjualan berbasis data e-commerce. Tujuannya bukan hanya membuat chart, tetapi menunjukkan alur data science sederhana dari data mentah sampai insight bisnis yang bisa ditampilkan di portfolio Django.

## Goal

```text
Raw e-commerce data
-> data cleaning
-> feature engineering
-> processed dataset
-> interactive Dash dashboard
-> case study page di Django portfolio
```

## Dataset

Gunakan dataset e-commerce sales yang lebih baru agar portfolio terasa relevan.

Rekomendasi dataset:

```text
Multi-Source Data for E-Commerce Sales Prediction
Kaggle: https://www.kaggle.com/datasets/algozee/multi-source-data-for-e-commerce-sales-prediction
```

Alternatif:

```text
Global E-Commerce Sales Dataset 2025
Kaggle: https://www.kaggle.com/datasets/kojibrand/global-e-commerce-sales-dataset-2025
```

## Download Data

1. Buka halaman dataset Kaggle.
2. Download file CSV.
3. Rename file menjadi:

```text
ecommerce_sales.csv
```

4. Simpan ke:

```text
projects/sales_dashboard/data/raw/ecommerce_sales.csv
```

Folder `data/raw/` tidak perlu diupload ke git karena dataset bisa besar dan memiliki lisensi dari Kaggle.

## Folder Structure

```text
projects/sales_dashboard/
|-- data/
|   |-- raw/
|   |   `-- ecommerce_sales.csv
|   `-- processed/
|       `-- sales_clean.csv
|-- notebooks/
|   `-- sales_eda.ipynb
|-- src/
|   `-- prepare_data.py
|-- dashboard/
|   `-- app.py
|-- reports/
`-- README.md
```

## Data Preparation Plan

Script:

```text
projects/sales_dashboard/src/prepare_data.py
```

Tugas script:

```text
1. Read data/raw/ecommerce_sales.csv
2. Standardize column names
3. Parse date columns
4. Handle missing values
5. Create useful features
6. Save data/processed/sales_clean.csv
```

Feature engineering awal:

```text
order_month
order_year
order_quarter
sales_amount / revenue
profit_margin jika ada kolom profit
discount_rate jika ada kolom discount
```

## Dashboard Plan

Dash app:

```text
projects/sales_dashboard/dashboard/app.py
```

Dashboard awal:

```text
KPI cards:
- Total sales
- Total orders
- Average order value
- Total customers jika tersedia

Charts:
- Monthly sales trend
- Sales by category
- Sales by country/region
- Top products

Filters:
- Date range
- Category
- Country/region
```

## Portfolio Case Study

Halaman Django:

```text
/projects/sales-dashboard/
```

Isi case study:

```text
Problem:
Business team needs a clear way to monitor sales performance and identify growth opportunities.

Approach:
Clean e-commerce transaction data, engineer time-based and business metrics, then build an interactive dashboard.

Result:
Dashboard helps users track revenue trends, top-performing products, and regional performance.
```

## Next Steps

```text
[x] Download dataset from Kaggle
[x] Save as data/raw/ecommerce_sales.csv
[x] Inspect columns
[x] Build prepare_data.py
[x] Generate data/processed/sales_clean.csv
[ ] Build Dash dashboard app.py
[ ] Link dashboard from Django project detail page
```

