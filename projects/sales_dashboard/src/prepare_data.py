from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA = PROJECT_DIR / "data" / "raw" / "ecommerce_sales.csv"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed" / "sales_clean.csv"

REQUIRED_COLUMNS = {
    "order_id",
    "order_date",
    "customer_name",
    "customer_segment",
    "country",
    "region",
    "product_category",
    "product_name",
    "quantity",
    "unit_price",
    "discount_percent",
    "total_sales",
    "shipping_cost",
    "profit",
    "payment_method",
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    return df


def validate_columns(df: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")


def prepare_sales_data(raw_path: Path = RAW_DATA) -> pd.DataFrame:
    sales = pd.read_csv(raw_path)
    sales = standardize_columns(sales)
    validate_columns(sales)

    sales = sales.drop_duplicates().copy()
    sales["order_date"] = pd.to_datetime(sales["order_date"])

    sales["order_year"] = sales["order_date"].dt.year
    sales["order_month"] = sales["order_date"].dt.month
    sales["order_month_name"] = sales["order_date"].dt.strftime("%b")
    sales["order_year_month"] = sales["order_date"].dt.to_period("M").astype(str)
    sales["order_quarter"] = sales["order_date"].dt.to_period("Q").astype(str)

    sales["gross_sales"] = sales["quantity"] * sales["unit_price"]
    sales["discount_amount"] = (
        sales["gross_sales"] * (sales["discount_percent"] / 100)
    )
    sales["net_sales_check"] = sales["gross_sales"] - sales["discount_amount"]
    sales["sales_diff"] = sales["total_sales"] - sales["net_sales_check"]

    sales["profit_margin"] = sales["profit"] / sales["total_sales"]
    sales["shipping_cost_ratio"] = sales["shipping_cost"] / sales["total_sales"]

    return sales


def print_summary(sales: pd.DataFrame) -> None:
    total_sales = sales["total_sales"].sum()
    total_profit = sales["profit"].sum()
    total_orders = sales["order_id"].nunique()
    total_customers = sales["customer_name"].nunique()
    avg_order_value = total_sales / total_orders
    profit_margin = total_profit / total_sales

    print("Sales data prepared successfully")
    print(f"Rows: {len(sales):,}")
    print(f"Columns: {len(sales.columns):,}")
    print(f"Date range: {sales['order_date'].min().date()} to {sales['order_date'].max().date()}")
    print(f"Total sales: {total_sales:,.2f}")
    print(f"Total profit: {total_profit:,.2f}")
    print(f"Total orders: {total_orders:,}")
    print(f"Total customers: {total_customers:,}")
    print(f"Average order value: {avg_order_value:,.2f}")
    print(f"Profit margin: {profit_margin:.2%}")
    print(f"Saved to: {PROCESSED_DATA}")


def main() -> None:
    if not RAW_DATA.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_DATA}. "
            "Download the dataset and save it as ecommerce_sales.csv."
        )

    sales = prepare_sales_data(RAW_DATA)
    PROCESSED_DATA.parent.mkdir(parents=True, exist_ok=True)
    sales.to_csv(PROCESSED_DATA, index=False)
    print_summary(sales)


if __name__ == "__main__":
    main()
