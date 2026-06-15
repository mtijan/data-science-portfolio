# Data Science Portfolio

A unified, professional-grade portfolio website and project workspace showcasing practical data science, analytics, machine learning, and Generative AI projects.

## Architecture

This project uses a **Unified Architectural Integration**:
- **Core Framework**: Django 5.x acts as the central hub and content management system.
- **Embedded Dashboards**: Interactive Dash/Plotly applications are embedded directly into Django templates using `django-plotly-dash`, providing a seamless user experience.
- **Database Driven**: Project metadata (titles, summaries, tools, case studies) is stored in a SQLite database and can be managed via the **Django Admin**.
- **Package Management**: Built and managed with `uv` for fast, reproducible environments.

## Projects

### 1. Sales Performance Dashboard
Business intelligence dashboard for monitoring e-commerce sales, profit, and discount impact.
- **Embedded App**: `SalesDashboard`
- **Stack**: Python, pandas, Dash, Plotly
- **Highlights**: Interactive KPI cards, monthly trends, and discount-to-profit sensitivity analysis.

### 2. Customer Churn Prediction
Machine learning pipeline and risk simulator to predict customer attrition.
- **Embedded App**: `ChurnPrediction`
- **Stack**: Python, pandas, scikit-learn, Dash
- **Performance**: Gradient Boosting model with **0.8435 ROC-AUC** and high recall (79%) for proactive retention.

### 3. AI Document Assistant (RAG)
Generative AI tool for querying unstructured PDF documents with source evidence.
- **Embedded App**: `AIDocumentAssistant`
- **Stack**: LangChain, ChromaDB, SumoPod API (GLM-5 Turbo)
- **Highlights**: Retrieval-Augmented Generation with evidence-backed answers and source snippet display.

## Local Development

### 1. Setup Environment
Ensure you have `uv` installed, then run:
```powershell
uv sync
```

### 2. Database & Content
Apply migrations and populate the initial project data:
```powershell
uv run python manage.py migrate
# Initial data is already populated if you use the existing db.sqlite3
```

### 3. Run the Portfolio
Start the unified server (this hosts both the Django site and the embedded Dash apps):
```powershell
uv run python manage.py runserver
```
Visit `http://127.0.0.1:8000/` to explore the portfolio.

### 4. Admin Portal
Manage projects and content through the admin interface:
```powershell
# Create a superuser if needed:
# uv run python manage.py createsuperuser
```
Visit `http://127.0.0.1:8000/admin/` to edit project details.

## Repository Structure
- `portfolio/`: Django application logic and embedded Dash app definitions.
- `projects/`: Core data science project workspaces (scripts, notebooks, models).
- `portofolio_site/`: Project-wide settings and URL configuration.
- `static/`: Global CSS and assets.

## Repository Notes
Raw datasets, models, vector stores, and private keys are excluded from git.
```
