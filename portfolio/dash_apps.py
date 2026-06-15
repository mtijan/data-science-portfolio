import os
import sys
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, ctx, dcc, html
from django_plotly_dash import DjangoDash

# Base directory for the entire project
BASE_DIR = Path(__file__).resolve().parents[1]

# --- Common Constants ---
ACCENT = "#0891b2"
COLOR_SEQUENCE = ["#0891b2", "#3b82f6", "#8b5cf6", "#ec4899", "#f43f5e", "#f59e0b", "#10b981"]
CHURN_COLOR_SEQUENCE = ["#007c89", "#f28e2b", "#4e79a7", "#e15759", "#59a14f"]


# ==========================================
# 1. SALES DASHBOARD
# ==========================================
sales_dash = DjangoDash('SalesDashboard')

SALES_DATA_PATH = BASE_DIR / "projects" / "sales_dashboard" / "data" / "processed" / "sales_clean.csv"

if SALES_DATA_PATH.exists():
    sales_df = pd.read_csv(SALES_DATA_PATH)
    sales_df["order_date"] = pd.to_datetime(sales_df["order_date"])
else:
    sales_df = pd.DataFrame()

# Helper functions for Sales Dashboard
def style_sales_figure(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f5fbfe",
        margin={"l": 24, "r": 18, "t": 58, "b": 36},
        font={"family": "Plus Jakarta Sans, Arial", "color": "#1e293b"},
        title={"font": {"size": 18, "family": "Outfit", "color": "#0f172a"}, "x": 0.02, "xanchor": "left"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    fig.update_xaxes(showgrid=False, linecolor="#e2e8f0", tickfont={"color": "#64748b"})
    fig.update_yaxes(gridcolor="#e2e8f0", linecolor="#e2e8f0", tickfont={"color": "#64748b"})
    return fig

def build_sales_figures(filtered):
    monthly_sales = filtered.groupby("order_year_month", as_index=False).agg(total_sales=("total_sales", "sum"))
    category_sales = filtered.groupby("product_category", as_index=False).agg(total_sales=("total_sales", "sum")).sort_values("total_sales", ascending=False)
    region_sales = filtered.groupby("region", as_index=False).agg(total_profit=("profit", "sum")).sort_values("total_profit", ascending=False)
    top_products = filtered.groupby("product_name", as_index=False).agg(total_sales=("total_sales", "sum")).sort_values("total_sales", ascending=False).head(10)

    monthly_fig = px.line(monthly_sales, x="order_year_month", y="total_sales", markers=True, title="Monthly Sales Trend")
    category_fig = px.bar(category_sales, x="product_category", y="total_sales", title="Sales by Category", color="product_category", color_discrete_sequence=COLOR_SEQUENCE)
    region_fig = px.bar(region_sales, x="region", y="total_profit", title="Profit by Region", color="region", color_discrete_sequence=COLOR_SEQUENCE)
    top_products_fig = px.bar(top_products, x="total_sales", y="product_name", orientation="h", title="Top 10 Products")
    discount_fig = px.scatter(filtered, x="discount_percent", y="profit", color="product_category", title="Discount vs Profit", color_discrete_sequence=COLOR_SEQUENCE)

    figs = [monthly_fig, category_fig, region_fig, top_products_fig, discount_fig]
    return [style_sales_figure(f) for f in figs]

sales_dash.layout = html.Div([
    html.Div([
        dcc.DatePickerRange(
            id="date-filter",
            min_date_allowed=sales_df["order_date"].min() if not sales_df.empty else None,
            max_date_allowed=sales_df["order_date"].max() if not sales_df.empty else None,
            start_date=sales_df["order_date"].min() if not sales_df.empty else None,
            end_date=sales_df["order_date"].max() if not sales_df.empty else None,
        ),
        dcc.Dropdown(id="region-filter", options=[{"label": r, "value": r} for r in sorted(sales_df["region"].unique())] if not sales_df.empty else [], multi=True, placeholder="All Regions"),
    ], className="filter-panel"),
    html.Div([
        dcc.Graph(id="monthly-sales-chart"),
        dcc.Graph(id="category-sales-chart"),
    ], className="chart-grid")
])

@sales_dash.callback(
    Output("monthly-sales-chart", "figure"),
    Output("category-sales-chart", "figure"),
    Input("date-filter", "start_date"),
    Input("date-filter", "end_date"),
    Input("region-filter", "value"),
)
def update_sales_dashboard(start_date, end_date, selected_regions):
    filtered = sales_df.copy()
    if start_date: filtered = filtered[filtered["order_date"] >= pd.to_datetime(start_date)]
    if end_date: filtered = filtered[filtered["order_date"] <= pd.to_datetime(end_date)]
    if selected_regions: filtered = filtered[filtered["region"].isin(selected_regions)]
    
    figs = build_sales_figures(filtered)
    return figs[0], figs[1]


# ==========================================
# 2. CHURN PREDICTION
# ==========================================
churn_dash = DjangoDash('ChurnPrediction')

CHURN_DATA_PATH = BASE_DIR / "projects" / "churn_prediction" / "data" / "processed" / "churn_clean.csv"
CHURN_MODEL_PATH = BASE_DIR / "projects" / "churn_prediction" / "models" / "churn_gradient_boosting.joblib"

if CHURN_DATA_PATH.exists() and CHURN_MODEL_PATH.exists():
    churn_df = pd.read_csv(CHURN_DATA_PATH)
    churn_model_pkg = joblib.load(CHURN_MODEL_PATH)
    c_model = churn_model_pkg["model"]
    c_threshold = churn_model_pkg["threshold"]
    c_features = churn_model_pkg["feature_columns"]
else:
    churn_df = pd.DataFrame()
    c_model = None

def build_churn_bar(data, col, title):
    chart_data = data.groupby(col, as_index=False)["is_churned"].mean().sort_values("is_churned", ascending=False)
    fig = px.bar(chart_data, x=col, y="is_churned", title=title, color_discrete_sequence=CHURN_COLOR_SEQUENCE)
    fig.update_layout(template="plotly_white")
    return fig

churn_dash.layout = html.Div([
    html.Div([
        dcc.Dropdown(id="contract-filter", options=[{"label": i, "value": i} for i in sorted(churn_df["contract"].unique())] if not churn_df.empty else [], multi=True, placeholder="All Contracts"),
    ], className="filter-panel"),
    dcc.Graph(id="contract-chart"),
    html.Div([
        html.H3("Churn Risk Simulator"),
        dcc.Input(id="pred-tenure", type="number", value=6, placeholder="Tenure"),
        html.Button("Predict", id="predict-button"),
        html.Div(id="prediction-result")
    ])
])

@churn_dash.callback(
    Output("contract-chart", "figure"),
    Input("contract-filter", "value"),
)
def update_churn_dashboard(contracts):
    filtered = churn_df.copy()
    if contracts: filtered = filtered[filtered["contract"].isin(contracts)]
    return build_churn_bar(filtered, "contract", "Churn Rate by Contract")


# ==========================================
# 3. AI DOCUMENT ASSISTANT (RAG)
# ==========================================
rag_dash = DjangoDash('AIDocumentAssistant')

# Setup path for RAG modules
RAG_PROJECT_DIR = BASE_DIR / "projects" / "ai_document_assistant"
RAG_SRC_DIR = RAG_PROJECT_DIR / "src"
if str(RAG_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_SRC_DIR))

try:
    from rag_pipeline import DocumentRagPipeline
    _pipeline = None
    def get_pipeline():
        global _pipeline
        if _pipeline is None: _pipeline = DocumentRagPipeline()
        return _pipeline
except ImportError:
    def get_pipeline(): return None

rag_dash.layout = html.Div([
    html.H2("AI Document Assistant"),
    dcc.Textarea(id="question-input", value="Rangkum profil kandidat", style={'width': '100%', 'height': 100}),
    html.Button("Ask AI", id="ask-button"),
    dcc.Loading(html.Div(id="answer-output"))
])

@rag_dash.callback(
    Output("answer-output", "children"),
    Input("ask-button", "n_clicks"),
    State("question-input", "value"),
)
def answer_question(n_clicks, question):
    if not n_clicks or not question: return "Ask a question..."
    pipeline = get_pipeline()
    if not pipeline: return "RAG Pipeline not available."
    result = pipeline.answer_question(question)
    return html.Div([
        html.H4("Answer:"),
        html.P(result.answer)
    ])
