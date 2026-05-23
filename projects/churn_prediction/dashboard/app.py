from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, dcc, html


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "processed" / "churn_clean.csv"
MODEL_PATH = PROJECT_DIR / "models" / "churn_gradient_boosting.joblib"

COLOR_SEQUENCE = ["#007c89", "#f28e2b", "#4e79a7", "#e15759", "#59a14f"]


df = pd.read_csv(DATA_PATH)
model_package = joblib.load(MODEL_PATH)
model = model_package["model"]
threshold = model_package["threshold"]
roc_auc = model_package["roc_auc"]
feature_columns = model_package["feature_columns"]

contract_options = sorted(df["contract"].dropna().unique())
tenure_options = sorted(df["tenure_group"].dropna().unique())
payment_options = sorted(df["payment_method"].dropna().unique())
internet_options = sorted(df["internet_service"].dropna().unique())


def dropdown_options(column):
    return [{"label": item, "value": item} for item in sorted(df[column].dropna().unique())]


external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"
]
app = Dash(__name__, external_stylesheets=external_stylesheets)


def build_bar_chart(data, group_column, title, x_label):
    chart_data = (
        data.groupby(group_column, as_index=False)["is_churned"]
        .mean()
        .sort_values("is_churned", ascending=False)
    )

    fig = px.bar(
        chart_data,
        x=group_column,
        y="is_churned",
        title=title,
        labels={group_column: x_label, "is_churned": "Churn Rate"},
        color=group_column,
        color_discrete_sequence=COLOR_SEQUENCE,
        text="is_churned",
    )
    fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f5fbfe",
        showlegend=False,
        yaxis_tickformat=".0%",
        margin={"l": 56, "r": 24, "t": 58, "b": 46},
        font={"family": "Plus Jakarta Sans, Arial", "color": "#1e293b"},
        title={"font": {"size": 18, "family": "Outfit", "color": "#0f172a"}, "x": 0.02, "xanchor": "left"},
    )
    fig.update_xaxes(gridcolor="#e2e8f0", zerolinecolor="#e2e8f0")
    fig.update_yaxes(gridcolor="#e2e8f0", zerolinecolor="#e2e8f0")
    return fig


def filter_data(selected_contracts, selected_tenures, selected_payments, selected_internet):
    filtered = df.copy()

    if selected_contracts:
        filtered = filtered[filtered["contract"].isin(selected_contracts)]
    if selected_tenures:
        filtered = filtered[filtered["tenure_group"].isin(selected_tenures)]
    if selected_payments:
        filtered = filtered[filtered["payment_method"].isin(selected_payments)]
    if selected_internet:
        filtered = filtered[filtered["internet_service"].isin(selected_internet)]

    return filtered


def get_tenure_group(tenure):
    if tenure <= 12:
        return "0-12 months"
    if tenure <= 24:
        return "13-24 months"
    if tenure <= 48:
        return "25-48 months"
    return "49-72 months"


def get_monthly_charge_group(monthly_charges):
    if monthly_charges <= 35:
        return "low"
    if monthly_charges <= 70:
        return "medium"
    return "high"


def build_prediction_row(
    gender,
    senior_citizen,
    partner,
    dependents,
    tenure,
    phone_service,
    multiple_lines,
    internet_service,
    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies,
    contract,
    paperless_billing,
    payment_method,
    monthly_charges,
    total_charges,
):
    input_data = {
        "gender": gender,
        "senior_citizen": senior_citizen,
        "partner": partner,
        "dependents": dependents,
        "tenure": tenure,
        "phone_service": phone_service,
        "multiple_lines": multiple_lines,
        "internet_service": internet_service,
        "online_security": online_security,
        "online_backup": online_backup,
        "device_protection": device_protection,
        "tech_support": tech_support,
        "streaming_tv": streaming_tv,
        "streaming_movies": streaming_movies,
        "contract": contract,
        "paperless_billing": paperless_billing,
        "payment_method": payment_method,
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
        "has_internet_service": int(internet_service != "No"),
        "has_month_to_month_contract": int(contract == "Month-to-month"),
        "has_automatic_payment": int("automatic" in payment_method.lower()),
        "avg_monthly_total_ratio": total_charges / max(tenure, 1),
        "tenure_group": get_tenure_group(tenure),
        "monthly_charge_group": get_monthly_charge_group(monthly_charges),
    }
    return pd.DataFrame([input_data], columns=feature_columns)


app.layout = html.Div(
    className="dashboard-page",
    children=[
        html.Div(
            className="dashboard-header",
            children=[
                html.A(
                    "\u2190 Back to Portfolio",
                    href="http://127.0.0.1:8000/",
                    className="back-btn",
                ),
                html.P("MACHINE LEARNING DASHBOARD", className="eyebrow"),
                html.H1("Customer Churn Analytics"),
                html.P(
                    "Interactive dashboard to analyze churn patterns by contract, tenure, "
                    "payment method, and internet service."
                ),
            ],
        ),
        html.Div(
            className="filter-panel",
            children=[
                html.Div(
                    className="filter-control",
                    children=[
                        html.Label("Contract"),
                        dcc.Dropdown(
                            clearable=True,
                            maxHeight=140,
                            optionHeight=32,
                            id="contract-filter",
                            options=[{"label": item, "value": item} for item in contract_options],
                            value=[],
                            multi=True,
                            placeholder="All contracts",
                            className="filter-dropdown",
                        ),
                    ],
                ),
                html.Div(
                    className="filter-control",
                    children=[
                        html.Label("Tenure Group"),
                        dcc.Dropdown(
                            clearable=True,
                            maxHeight=140,
                            optionHeight=32,
                            id="tenure-filter",
                            options=[{"label": item, "value": item} for item in tenure_options],
                            value=[],
                            multi=True,
                            placeholder="All tenure groups",
                            className="filter-dropdown",
                        ),
                    ],
                ),
                html.Div(
                    className="filter-control",
                    children=[
                        html.Label("Payment Method"),
                        dcc.Dropdown(
                            clearable=True,
                            maxHeight=140,
                            optionHeight=32,
                            id="payment-filter",
                            options=[{"label": item, "value": item} for item in payment_options],
                            value=[],
                            multi=True,
                            placeholder="All payment methods",
                            className="filter-dropdown",
                        ),
                    ],
                ),
                html.Div(
                    className="filter-control",
                    children=[
                        html.Label("Internet Service"),
                        dcc.Dropdown(
                            clearable=True,
                            maxHeight=140,
                            optionHeight=32,
                            id="internet-filter",
                            options=[{"label": item, "value": item} for item in internet_options],
                            value=[],
                            multi=True,
                            placeholder="All internet services",
                            className="filter-dropdown",
                        ),
                    ],
                ),
            ],
        ),
        html.Div(id="kpi-grid", className="kpi-grid"),
        html.Div(
            className="chart-grid",
            children=[
                html.Div(dcc.Graph(id="contract-chart"), className="chart-card"),
                html.Div(dcc.Graph(id="tenure-chart"), className="chart-card"),
                html.Div(dcc.Graph(id="payment-chart"), className="chart-card"),
                html.Div(dcc.Graph(id="internet-chart"), className="chart-card"),
            ],
        ),
        html.Div(
            className="prediction-section",
            children=[
                html.Div(
                    className="prediction-header",
                    children=[
                        html.P("Churn risk simulator", className="eyebrow"),
                        html.H2("Estimate churn risk for a customer"),
                        html.P(
                            f"Use this form to test customer profiles against the trained model. "
                            f"The model ROC-AUC is {roc_auc:.4f}, and customers above the {threshold:.0%} threshold "
                            f"are treated as retention priorities."
                        ),
                    ],
                ),
                html.Div(
                    className="prediction-grid",
                    children=[
                        html.Div([html.Label("Gender"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-gender", options=dropdown_options("gender"), value="Female")], className="prediction-control"),
                        html.Div([html.Label("Senior Citizen"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-senior", options=[{"label": "No", "value": 0}, {"label": "Yes", "value": 1}], value=0)], className="prediction-control"),
                        html.Div([html.Label("Partner"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-partner", options=dropdown_options("partner"), value="No")], className="prediction-control"),
                        html.Div([html.Label("Dependents"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-dependents", options=dropdown_options("dependents"), value="No")], className="prediction-control"),
                        html.Div([html.Label("Tenure"), dcc.Input(id="pred-tenure", type="number", min=0, max=72, step=1, value=6)], className="prediction-control"),
                        html.Div([html.Label("Monthly Charges"), dcc.Input(id="pred-monthly", type="number", min=0, step=0.01, value=85)], className="prediction-control"),
                        html.Div([html.Label("Total Charges"), dcc.Input(id="pred-total", type="number", min=0, step=0.01, value=510)], className="prediction-control"),
                        html.Div([html.Label("Contract"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-contract", options=dropdown_options("contract"), value="Month-to-month")], className="prediction-control"),
                        html.Div([html.Label("Phone Service"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-phone", options=dropdown_options("phone_service"), value="Yes")], className="prediction-control"),
                        html.Div([html.Label("Multiple Lines"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-lines", options=dropdown_options("multiple_lines"), value="No")], className="prediction-control"),
                        html.Div([html.Label("Internet Service"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-internet", options=dropdown_options("internet_service"), value="Fiber optic")], className="prediction-control"),
                        html.Div([html.Label("Online Security"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-security", options=dropdown_options("online_security"), value="No")], className="prediction-control"),
                        html.Div([html.Label("Online Backup"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-backup", options=dropdown_options("online_backup"), value="No")], className="prediction-control"),
                        html.Div([html.Label("Device Protection"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-protection", options=dropdown_options("device_protection"), value="No")], className="prediction-control"),
                        html.Div([html.Label("Tech Support"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-support", options=dropdown_options("tech_support"), value="No")], className="prediction-control"),
                        html.Div([html.Label("Streaming TV"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-tv", options=dropdown_options("streaming_tv"), value="No")], className="prediction-control"),
                        html.Div([html.Label("Streaming Movies"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-movies", options=dropdown_options("streaming_movies"), value="No")], className="prediction-control"),
                        html.Div([html.Label("Paperless Billing"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-paperless", options=dropdown_options("paperless_billing"), value="Yes")], className="prediction-control"),
                        html.Div([html.Label("Payment Method"), dcc.Dropdown(clearable=False, searchable=False, maxHeight=58, optionHeight=26, id="pred-payment", options=dropdown_options("payment_method"), value="Electronic check")], className="prediction-control wide"),
                    ],
                ),
                html.Button("Predict Churn Risk", id="predict-button", n_clicks=0, className="predict-button"),
                html.Div(id="prediction-result", className="prediction-result"),
            ],
        ),
    ],
)


@app.callback(
    Output("kpi-grid", "children"),
    Output("contract-chart", "figure"),
    Output("tenure-chart", "figure"),
    Output("payment-chart", "figure"),
    Output("internet-chart", "figure"),
    Input("contract-filter", "value"),
    Input("tenure-filter", "value"),
    Input("payment-filter", "value"),
    Input("internet-filter", "value"),
)
def update_dashboard(selected_contracts, selected_tenures, selected_payments, selected_internet):
    filtered = filter_data(selected_contracts, selected_tenures, selected_payments, selected_internet)

    total_customers = len(filtered)
    churned_customers = int(filtered["is_churned"].sum())
    retained_customers = total_customers - churned_customers
    churn_rate = churned_customers / total_customers if total_customers else 0
    avg_monthly_charges = filtered["monthly_charges"].mean() if total_customers else 0

    kpi_cards = [
        html.Div([html.H3("Total Customers"), html.P(f"{total_customers:,}")], className="kpi-card"),
        html.Div([html.H3("Churned Customers"), html.P(f"{churned_customers:,}")], className="kpi-card"),
        html.Div([html.H3("Retained Customers"), html.P(f"{retained_customers:,}")], className="kpi-card"),
        html.Div([html.H3("Churn Rate"), html.P(f"{churn_rate:.2%}")], className="kpi-card"),
        html.Div([html.H3("Avg Monthly Charges"), html.P(f"${avg_monthly_charges:,.2f}")], className="kpi-card"),
    ]

    contract_fig = build_bar_chart(filtered, "contract", "Churn Rate by Contract Type", "Contract")
    tenure_fig = build_bar_chart(filtered, "tenure_group", "Churn Rate by Tenure Group", "Tenure Group")
    payment_fig = build_bar_chart(filtered, "payment_method", "Churn Rate by Payment Method", "Payment Method")
    internet_fig = build_bar_chart(filtered, "internet_service", "Churn Rate by Internet Service", "Internet Service")

    return kpi_cards, contract_fig, tenure_fig, payment_fig, internet_fig


@app.callback(
    Output("prediction-result", "children"),
    Input("predict-button", "n_clicks"),
    State("pred-gender", "value"),
    State("pred-senior", "value"),
    State("pred-partner", "value"),
    State("pred-dependents", "value"),
    State("pred-tenure", "value"),
    State("pred-phone", "value"),
    State("pred-lines", "value"),
    State("pred-internet", "value"),
    State("pred-security", "value"),
    State("pred-backup", "value"),
    State("pred-protection", "value"),
    State("pred-support", "value"),
    State("pred-tv", "value"),
    State("pred-movies", "value"),
    State("pred-contract", "value"),
    State("pred-paperless", "value"),
    State("pred-payment", "value"),
    State("pred-monthly", "value"),
    State("pred-total", "value"),
)
def predict_churn(
    n_clicks,
    gender,
    senior_citizen,
    partner,
    dependents,
    tenure,
    phone_service,
    multiple_lines,
    internet_service,
    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies,
    contract,
    paperless_billing,
    payment_method,
    monthly_charges,
    total_charges,
):
    if not n_clicks:
        return "Fill in the customer profile and click Predict Churn Risk."

    tenure = int(tenure or 0)
    monthly_charges = float(monthly_charges or 0)
    total_charges = float(total_charges or 0)

    prediction_row = build_prediction_row(
        gender,
        senior_citizen,
        partner,
        dependents,
        tenure,
        phone_service,
        multiple_lines,
        internet_service,
        online_security,
        online_backup,
        device_protection,
        tech_support,
        streaming_tv,
        streaming_movies,
        contract,
        paperless_billing,
        payment_method,
        monthly_charges,
        total_charges,
    )

    churn_probability = model.predict_proba(prediction_row)[0, 1]
    is_high_risk = churn_probability >= threshold
    risk_label = "Needs attention" if is_high_risk else "Looks stable"
    result_class = "risk-high" if is_high_risk else "risk-low"
    probability_text = f"About {churn_probability:.0%} chance this customer may leave."

    if is_high_risk:
        simple_meaning = "This customer should be prioritized by the retention team."
        action_items = [
            "Contact the customer before the next billing cycle.",
            "Review contract, support issues, and monthly charges.",
            "Offer a retention incentive if the account is valuable.",
        ]
    else:
        simple_meaning = "This customer is not an urgent churn case right now."
        action_items = [
            "Keep monitoring the customer over time.",
            "Maintain service quality and billing experience.",
            "No immediate retention campaign is required.",
        ]

    return html.Div(
        className=result_class,
        children=[
            html.Div(
                className="prediction-result-header",
                children=[
                    html.H3(risk_label),
                    html.P(probability_text, className="prediction-score"),
                ],
            ),
            html.P(simple_meaning, className="prediction-meaning"),
            html.Div(
                className="prediction-action-box",
                children=[
                    html.H4("Recommended action"),
                    html.Ul([html.Li(item) for item in action_items]),
                ],
            ),
            html.P(
                f"Model note: high risk means the score is above the {threshold:.0%} decision threshold.",
                className="prediction-note",
            ),
        ],
    )


if __name__ == "__main__":
    app.run(debug=True, port=8051)

