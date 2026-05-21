from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "processed" / "churn_clean.csv"
FIGURE_DIR = PROJECT_DIR / "reports" / "figures"

sns.set_theme(style="whitegrid")


def save_churn_by_contract(df):
    contract_churn = (
        df.groupby("contract", as_index=False)
        .agg(churn_rate=("is_churned", "mean"))
        .sort_values("churn_rate", ascending=False)
    )

    plt.figure(figsize=(8, 5))
    ax = sns.barplot(
        data=contract_churn,
        x="contract",
        y="churn_rate",
        hue="contract",
        palette="Set2",
        legend=False,
    )
    ax.set_title("Churn Rate by Contract Type")
    ax.set_xlabel("Contract Type")
    ax.set_ylabel("Churn Rate")
    ax.yaxis.set_major_formatter(lambda x, pos: f"{x:.0%}")

    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "churn_by_contract.png", dpi=160)
    plt.close()


def save_churn_by_tenure_group(df):
    tenure_churn = (
        df.groupby("tenure_group", as_index=False)
        .agg(churn_rate=("is_churned", "mean"))
    )

    plt.figure(figsize=(8, 5))
    ax = sns.barplot(
        data=tenure_churn,
        x="tenure_group",
        y="churn_rate",
        hue="tenure_group",
        palette="Set2",
        legend=False,
    )
    ax.set_title("Churn Rate by Tenure Group")
    ax.set_xlabel("Tenure Group")
    ax.set_ylabel("Churn Rate")
    ax.yaxis.set_major_formatter(lambda x, pos: f"{x:.0%}")
    plt.xticks(rotation=20, ha="right")

    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "churn_by_tenure_group.png", dpi=160)
    plt.close()


def save_model_performance():
    performance = pd.DataFrame(
        {
            "metric": ["ROC-AUC", "Recall", "Precision", "F1-score"],
            "score": [0.8435, 0.7888, 0.5315, 0.6351],
        }
    )

    plt.figure(figsize=(8, 5))
    ax = sns.barplot(
        data=performance,
        x="metric",
        y="score",
        hue="metric",
        palette="Set2",
        legend=False,
    )
    ax.set_title("Gradient Boosting Model Performance")
    ax.set_xlabel("Metric")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1)

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f")

    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "model_performance.png", dpi=160)
    plt.close()


def generate_figures():
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    save_churn_by_contract(df)
    save_churn_by_tenure_group(df)
    save_model_performance()

    print(f"Figures saved to: {FIGURE_DIR}")


if __name__ == "__main__":
    generate_figures()
    