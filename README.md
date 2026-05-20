# Data Science Portfolio

Portfolio website and project workspace for practical data science, analytics, machine learning, and dashboard projects.

## Projects

### 1. Sales Performance Dashboard

Business intelligence dashboard for monitoring e-commerce sales, profit, product performance, customer segments, and discount impact.

```text
Status: Completed
Stack: Python, pandas, Dash, Plotly, Django
Project path: projects/sales_dashboard/
```

Highlights:

```text
- Data cleaning and feature engineering
- Interactive KPI dashboard
- Product, region, customer, and discount analysis
- Dashboard screenshots and project README
- Linked from Django portfolio website
```

### 2. Customer Churn Prediction

Machine learning project to predict customer churn using the Telco Customer Churn dataset.

```text
Status: In Progress
Stack: Python, pandas, scikit-learn, matplotlib, seaborn
Project path: projects/churn_prediction/
```

Current valid modeling result:

```text
Best model: Gradient Boosting
ROC-AUC: 0.8435
Selected threshold: 0.28
Recall churn: 0.7888
Precision churn: 0.5315
F1 churn: 0.6351
```

Highlights:

```text
- Replaced weak e-commerce churn dataset with Telco Customer Churn
- Built reproducible data preparation script
- Rebuilt EDA notebook with churn insights
- Rebuilt modeling notebook with multi-model comparison
- Achieved ROC-AUC above 0.80 without data leakage
```

## Local Development

Install dependencies with `uv`:

```powershell
uv sync
```

Run Django portfolio:

```powershell
uv run python manage.py runserver
```

Run Sales Dashboard:

```powershell
uv run python projects\sales_dashboard\dashboard\app.py
```

Prepare Churn Dataset:

```powershell
uv run python projects\churn_prediction\src\prepare_data.py
```

## Repository Notes

Raw datasets, processed datasets, models, vector stores, and local planning notes are excluded from git.

Ignored local files include:

```text
projects/*/data/raw/
projects/*/data/processed/
projects/*/models/
note_utama.md
step.md
note_command.md
AGENTS.md
```