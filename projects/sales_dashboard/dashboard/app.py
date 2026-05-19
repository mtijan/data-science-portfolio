from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "processed" / "sales_clean.csv"

ACCENT = "#0891b2"
COLOR_SEQUENCE = ["#0891b2", "#3b82f6", "#8b5cf6", "#ec4899", "#f43f5e", "#f59e0b", "#10b981"]

sales = pd.read_csv(DATA_PATH)
sales["order_date"] = pd.to_datetime(sales["order_date"])

region_options = [
    {"label": region, "value": region}
    for region in sorted(sales["region"].unique())
]
category_options = [
    {"label": category, "value": category}
    for category in sorted(sales["product_category"].unique())
]
segment_options = [
    {"label": segment, "value": segment}
    for segment in sorted(sales["customer_segment"].unique())
]


def style_figure(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8fafc",
        margin={"l": 24, "r": 18, "t": 58, "b": 36},
        font={"family": "Plus Jakarta Sans, Arial", "color": "#1e293b"},
        title={"font": {"size": 18, "family": "Outfit", "color": "#0f172a"}, "x": 0.02, "xanchor": "left"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    fig.update_xaxes(showgrid=False, linecolor="#e2e8f0", tickfont={"color": "#64748b"})
    fig.update_yaxes(gridcolor="#e2e8f0", linecolor="#e2e8f0", tickfont={"color": "#64748b"})
    return fig


def build_figures(filtered):
    monthly_sales = (
        filtered.groupby("order_year_month", as_index=False)
        .agg(
            total_sales=("total_sales", "sum"),
            total_profit=("profit", "sum"),
            total_orders=("order_id", "nunique"),
        )
    )

    category_sales = (
        filtered.groupby("product_category", as_index=False)
        .agg(
            total_sales=("total_sales", "sum"),
            total_profit=("profit", "sum"),
            total_orders=("order_id", "nunique"),
        )
        .sort_values("total_sales", ascending=False)
    )

    region_sales = (
        filtered.groupby("region", as_index=False)
        .agg(
            total_sales=("total_sales", "sum"),
            total_profit=("profit", "sum"),
            total_orders=("order_id", "nunique"),
        )
        .sort_values("total_sales", ascending=False)
    )

    top_products = (
        filtered.groupby("product_name", as_index=False)
        .agg(
            total_sales=("total_sales", "sum"),
            total_profit=("profit", "sum"),
            quantity_sold=("quantity", "sum"),
        )
        .sort_values("total_sales", ascending=False)
        .head(10)
    )

    monthly_fig = px.line(
        monthly_sales,
        x="order_year_month",
        y="total_sales",
        markers=True,
        title="Monthly Sales Trend",
    )
    monthly_fig.update_traces(line={"color": ACCENT, "width": 3}, marker={"size": 7})

    category_fig = px.bar(
        category_sales,
        x="product_category",
        y="total_sales",
        title="Sales by Product Category",
        text_auto=".2s",
        color="product_category",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    category_fig.update_layout(showlegend=False)

    region_fig = px.bar(
        region_sales,
        x="region",
        y="total_profit",
        title="Profit by Region",
        text_auto=".2s",
        color="region",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    region_fig.update_layout(showlegend=False)

    top_products_fig = px.bar(
        top_products,
        x="total_sales",
        y="product_name",
        orientation="h",
        title="Top 10 Products by Sales",
        text_auto=".2s",
        color_discrete_sequence=[ACCENT],
    )
    top_products_fig.update_layout(yaxis={"categoryorder": "total ascending"})

    discount_fig = px.scatter(
        filtered,
        x="discount_percent",
        y="profit",
        color="product_category",
        size="total_sales",
        hover_data=["product_name", "country", "customer_segment"],
        title="Discount Impact on Profit",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    discount_fig.update_traces(marker={"opacity": 0.68, "line": {"width": 0.5, "color": "#e2e8f0"}})
    discount_fig.update_layout(
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.22,
            "xanchor": "left",
            "x": 0,
            "title": {"text": "Product category"},
        },
        margin={"l": 56, "r": 18, "t": 70, "b": 120},
    )

    figures = [
        monthly_fig,
        category_fig,
        region_fig,
        top_products_fig,
        discount_fig,
    ]
    styled = [style_figure(fig) for fig in figures]
    # Re-apply bottom legend for discount scatter (style_figure moves it to top)
    styled[-1].update_layout(
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.28,
            "xanchor": "left",
            "x": 0,
            "title": {"text": "Product category"},
        },
        margin={"l": 56, "r": 18, "t": 58, "b": 140},
    )
    styled[-1].update_xaxes(title="Discount percent")
    styled[-1].update_yaxes(title="Profit")
    return tuple(styled)


def generate_insights(filtered, profit_margin):
    if filtered.empty:
        return (
            "No data is available for the selected filters.",
            "Try expanding the date range or removing one of the filters.",
        )

    top_category = (
        filtered.groupby("product_category", as_index=False)
        .agg(total_sales=("total_sales", "sum"))
        .sort_values("total_sales", ascending=False)
        .iloc[0]
    )
    top_region = (
        filtered.groupby("region", as_index=False)
        .agg(total_profit=("profit", "sum"))
        .sort_values("total_profit", ascending=False)
        .iloc[0]
    )
    top_segment = (
        filtered.groupby("customer_segment", as_index=False)
        .agg(total_sales=("total_sales", "sum"))
        .sort_values("total_sales", ascending=False)
        .iloc[0]
    )

    insight = (
        f"{top_category['product_category']} leads the selected view with "
        f"${top_category['total_sales']:,.2f} in sales. "
        f"{top_region['region']} contributes the highest profit at "
        f"${top_region['total_profit']:,.2f}, while the "
        f"{top_segment['customer_segment']} segment shows the strongest demand."
    )

    if profit_margin >= 0.30:
        recommendation = (
            f"Profit margin is healthy at {profit_margin:.2%}. "
            "Maintain focus on high-performing categories while monitoring discount levels."
        )
    elif profit_margin >= 0.15:
        recommendation = (
            f"Profit margin is moderate at {profit_margin:.2%}. "
            "Review discount strategy and shipping cost to protect profitability."
        )
    else:
        recommendation = (
            f"Profit margin is low at {profit_margin:.2%}. "
            "Prioritize margin recovery by reducing broad discounts and focusing on profitable products."
        )

    return insight, recommendation


external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"
]
app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    className="dashboard-page",
    children=[
        html.Div(
            className="dashboard-header",
            children=[
                html.A(
                    "← Back to Portfolio",
                    href="http://127.0.0.1:8000/",
                    className="back-btn",
                ),
                html.P("Sales Performance Dashboard", className="eyebrow"),
                html.H1("Global E-Commerce Sales Analytics"),
                html.P(
                    "Interactive dashboard for exploring sales, profit, region, "
                    "product category, and discount performance from 2023 to 2025."
                ),
            ],
        ),
        html.Div(
            className="filter-panel",
            children=[
                html.Div(
                    className="filter-control date-filter-control",
                    children=[
                        html.Label("Order Date"),
                        dcc.DatePickerRange(
                            id="date-filter",
                            min_date_allowed=sales["order_date"].min(),
                            max_date_allowed=sales["order_date"].max(),
                            start_date=sales["order_date"].min(),
                            end_date=sales["order_date"].max(),
                            display_format="YYYY-MM-DD",
                            className="date-filter",
                        ),
                    ],
                ),
                html.Div(
                    className="filter-control",
                    children=[
                        html.Label("Region"),
                        dcc.Dropdown(
                            id="region-filter",
                            options=region_options,
                            value=[],
                            multi=True,
                            placeholder="All regions",
                            className="filter-dropdown",
                        ),
                    ],
                ),
                html.Div(
                    className="filter-control",
                    children=[
                        html.Label("Product Category"),
                        dcc.Dropdown(
                            id="category-filter",
                            options=category_options,
                            value=[],
                            multi=True,
                            placeholder="All categories",
                            className="filter-dropdown",
                        ),
                    ],
                ),
                html.Div(
                    className="filter-control",
                    children=[
                        html.Label("Customer Segment"),
                        dcc.Dropdown(
                            id="segment-filter",
                            options=segment_options,
                            value=[],
                            multi=True,
                            placeholder="All segments",
                            className="filter-dropdown",
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="kpi-grid",
            children=[
                html.Div([html.H3("Total Sales"), html.P(id="total-sales")], className="kpi-card"),
                html.Div([html.H3("Total Profit"), html.P(id="total-profit")], className="kpi-card"),
                html.Div([html.H3("Orders"), html.P(id="total-orders")], className="kpi-card"),
                html.Div([html.H3("Customers"), html.P(id="total-customers")], className="kpi-card"),
                html.Div([html.H3("Avg Order Value"), html.P(id="avg-order-value")], className="kpi-card"),
                html.Div([html.H3("Profit Margin"), html.P(id="profit-margin")], className="kpi-card"),
            ],
        ),
        html.Div(
            className="insight-panel",
            children=[
                html.Div(
                    className="insight-card",
                    children=[
                        html.H3("Business Insight"),
                        html.P(id="business-insight"),
                    ],
                ),
                html.Div(
                    className="insight-card",
                    children=[
                        html.H3("Recommendation"),
                        html.P(id="business-recommendation"),
                    ],
                ),
            ],
        ),
        html.Div(
            className="chart-grid",
            children=[
                html.Div(dcc.Graph(id="monthly-sales-chart", config={"displayModeBar": False}), className="chart-card full"),
                html.Div(dcc.Graph(id="category-sales-chart", config={"displayModeBar": False}), className="chart-card"),
                html.Div(dcc.Graph(id="region-profit-chart", config={"displayModeBar": False}), className="chart-card"),
                html.Div(dcc.Graph(id="top-products-chart", config={"displayModeBar": False}), className="chart-card"),
                html.Div(dcc.Graph(id="discount-profit-chart", config={"displayModeBar": False}), className="chart-card"),
            ],
        ),
    ],
)


@app.callback(
    Output("total-sales", "children"),
    Output("total-profit", "children"),
    Output("total-orders", "children"),
    Output("total-customers", "children"),
    Output("avg-order-value", "children"),
    Output("profit-margin", "children"),
    Output("business-insight", "children"),
    Output("business-recommendation", "children"),
    Output("monthly-sales-chart", "figure"),
    Output("category-sales-chart", "figure"),
    Output("region-profit-chart", "figure"),
    Output("top-products-chart", "figure"),
    Output("discount-profit-chart", "figure"),
    Input("date-filter", "start_date"),
    Input("date-filter", "end_date"),
    Input("region-filter", "value"),
    Input("category-filter", "value"),
    Input("segment-filter", "value"),
)
def update_dashboard(start_date, end_date, selected_regions, selected_categories, selected_segments):
    filtered = sales.copy()

    if start_date:
        filtered = filtered[filtered["order_date"] >= pd.to_datetime(start_date)]

    if end_date:
        filtered = filtered[filtered["order_date"] <= pd.to_datetime(end_date)]

    if selected_regions:
        filtered = filtered[filtered["region"].isin(selected_regions)]

    if selected_categories:
        filtered = filtered[filtered["product_category"].isin(selected_categories)]

    if selected_segments:
        filtered = filtered[filtered["customer_segment"].isin(selected_segments)]

    total_sales = filtered["total_sales"].sum()
    total_profit = filtered["profit"].sum()
    total_orders = filtered["order_id"].nunique()
    total_customers = filtered["customer_name"].nunique()
    avg_order_value = total_sales / total_orders if total_orders else 0
    profit_margin = total_profit / total_sales if total_sales else 0
    business_insight, business_recommendation = generate_insights(filtered, profit_margin)

    figures = build_figures(filtered)

    return (
        f"${total_sales:,.2f}",
        f"${total_profit:,.2f}",
        f"{total_orders:,}",
        f"{total_customers:,}",
        f"${avg_order_value:,.2f}",
        f"{profit_margin:.2%}",
        business_insight,
        business_recommendation,
        *figures,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8050)
