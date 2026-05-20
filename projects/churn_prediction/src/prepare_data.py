from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_DIR / "data" / "raw" / "telco_customer_churn.csv"
PROCESSED_DATA_PATH = PROJECT_DIR / "data" / "processed" / "churn_clean.csv"


def standardize_columns(df):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(
        columns={
            "customerid": "customer_id",
            "seniorcitizen": "senior_citizen",
            "phoneservice": "phone_service",
            "multiplelines": "multiple_lines",
            "internetservice": "internet_service",
            "onlinesecurity": "online_security",
            "onlinebackup": "online_backup",
            "deviceprotection": "device_protection",
            "techsupport": "tech_support",
            "streamingtv": "streaming_tv",
            "streamingmovies": "streaming_movies",
            "paperlessbilling": "paperless_billing",
            "paymentmethod": "payment_method",
            "monthlycharges": "monthly_charges",
            "totalcharges": "total_charges",
        }
    )
    return df


def clean_values(df):
    df = df.copy()

    df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce")
    df["total_charges"] = df["total_charges"].fillna(0)

    yes_no_columns = [
        "partner",
        "dependents",
        "phone_service",
        "paperless_billing",
        "churn",
    ]

    for col in yes_no_columns:
        df[col] = df[col].str.strip()

    return df


def add_features(df):
    df = df.copy()

    df["is_churned"] = df["churn"].map({"Yes": 1, "No": 0})
    df["has_internet_service"] = (df["internet_service"] != "No").astype(int)
    df["has_month_to_month_contract"] = (df["contract"] == "Month-to-month").astype(int)
    df["has_automatic_payment"] = df["payment_method"].str.contains("automatic", case=False).astype(int)
    df["avg_monthly_total_ratio"] = df["total_charges"] / df["tenure"].clip(lower=1)

    df["tenure_group"] = pd.cut(
        df["tenure"],
        bins=[-1, 12, 24, 48, 72],
        labels=["0-12 months", "13-24 months", "25-48 months", "49-72 months"],
    ).astype(str)

    df["monthly_charge_group"] = pd.cut(
        df["monthly_charges"],
        bins=[0, 35, 70, 120],
        labels=["low", "medium", "high"],
        include_lowest=True,
    ).astype(str)

    return df


def prepare_data():
    df = pd.read_csv(RAW_DATA_PATH)

    raw_rows = len(df)
    df = standardize_columns(df)
    df = clean_values(df)
    df = add_features(df)

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print(f"Raw rows: {raw_rows:,}")
    print(f"Processed rows: {len(df):,}")
    print(f"Processed columns: {df.shape[1]:,}")
    print(f"Churn rate: {df['is_churned'].mean():.2%}")
    print(f"Processed data saved to: {PROCESSED_DATA_PATH}")


if __name__ == "__main__":
    prepare_data()