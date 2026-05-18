from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "processed" / "sales_clean.csv"


sales = pd.read_csv(DATA_PATH)
sales["order_date"] = pd.to_datetime(sales["order_date"])

total_sales = sales["total_sales"].sum()
total_profit = sales["profit"].sum()
total_orders = sales["order_id"].nunique()
total_customers = sales["customer_name"].nunique()
avg_order_value = total_sales / total_orders
profit_margin = total_profit / total_sales

monthly_sales = (
    sales.groupby("order_year_month", as_index=False)
    .agg(
        total_sales=("total_sales", "sum"),
        total_profit=("profit", "sum"),
        total_orders=("order_id", "nunique"),
    )
)

category_sales = (
    sales.groupby("product_category", as_index=False)
    .agg(
        total_sales=("total_sales", "sum"),
        total_profit=("profit", "sum"),
        total_orders=("order_id", "nunique"),
    )
    .sort_values("total_sales", ascending=False)
)

region_sales = (
    sales.groupby("region", as_index=False)
    .agg(
        total_sales=("total_sales", "sum"),
        total_profit=("profit", "sum"),
        total_orders=("order_id", "nunique"),
    )
    .sort_values("total_sales", ascending=False)
)

top_products = (
    sales.groupby("product_name", as_index=False)
    .agg(
        total_sales=("total_sales", "sum"),
        total_profit=("profit", "sum"),
        quantity_sold=("quantity", "sum"),
    )
    .sort_values("total_sales", ascending=False)
    .head(10)
)

monthly_sales_fig = px.line(
    monthly_sales,
    x="order_year_month",
    y="total_sales",
    markers=True,
    title="Monthly Sales Trend",
)

category_fig = px.bar(
    category_sales,
    x="product_category",
    y="total_sales",
    title="Sales by Product Category",
    text_auto=".2s",
)

region_fig = px.bar(
    region_sales,
    x="region",
    y="total_profit",
    title="Profit by Region",
    text_auto=".2s",
)

top_products_fig = px.bar(
    top_products,
    x="total_sales",
    y="product_name",
    orientation="h",
    title="Top 10 Products by Sales",
    text_auto=".2s",
)
top_products_fig.update_layout(yaxis={"categoryorder": "total ascending"})

discount_fig = px.scatter(
    sales,
    x="discount_percent",
    y="profit",
    color="product_category",
    size="total_sales",
    hover_data=["product_name", "country", "customer_segment"],
    title="Discount vs Profit",
)

app = Dash(__name__)

app.layout = html.Div(
    className="dashboard-page",
    children=[
        html.Div(
            className="dashboard-header",
            children=[
                html.P("Sales Performance Dashboard", className="eyebrow"),
                html.H1("Global E-Commerce Sales Analytics"),
                html.P(
                    "Interactive dashboard for exploring sales, profit, region, "
                    "product category, and discount performance from 2023 to 2025."
                ),
            ],
        ),

        html.Div(
            className="kpi-grid",
            children=[
                html.Div([html.H3("Total Sales"), html.P(f"${total_sales:,.2f}")], className="kpi-card"),
                html.Div([html.H3("Total Profit"), html.P(f"${total_profit:,.2f}")], className="kpi-card"),
                html.Div([html.H3("Orders"), html.P(f"{total_orders:,}")], className="kpi-card"),
                html.Div([html.H3("Customers"), html.P(f"{total_customers:,}")], className="kpi-card"),
                html.Div([html.H3("Avg Order Value"), html.P(f"${avg_order_value:,.2f}")], className="kpi-card"),
                html.Div([html.H3("Profit Margin"), html.P(f"{profit_margin:.2%}")], className="kpi-card"),
            ],
        ),

        html.Div(
            className="chart-grid",
            children=[
                html.Div(dcc.Graph(figure=monthly_sales_fig), className="chart-card full"),
                html.Div(dcc.Graph(figure=category_fig), className="chart-card"),
                html.Div(dcc.Graph(figure=region_fig), className="chart-card"),
                html.Div(dcc.Graph(figure=top_products_fig), className="chart-card"),
                html.Div(dcc.Graph(figure=discount_fig), className="chart-card"),
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True, port=8050)