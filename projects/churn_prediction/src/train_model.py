from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "processed" / "churn_clean.csv"
MODEL_PATH = PROJECT_DIR / "models" / "churn_gradient_boosting.joblib"
REPORT_PATH = PROJECT_DIR / "reports" / "evaluation_summary.md"

TARGET = "is_churned"
SELECTED_THRESHOLD = 0.28

FEATURE_COLUMNS = [
    "gender",
    "senior_citizen",
    "partner",
    "dependents",
    "tenure",
    "phone_service",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
    "contract",
    "paperless_billing",
    "payment_method",
    "monthly_charges",
    "total_charges",
    "has_internet_service",
    "has_month_to_month_contract",
    "has_automatic_payment",
    "avg_monthly_total_ratio",
    "tenure_group",
    "monthly_charge_group",
]


def build_pipeline(numeric_features, categorical_features):
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", GradientBoostingClassifier(random_state=42)),
        ]
    )


def evaluate_threshold(y_test, y_proba, threshold):
    y_pred = (y_proba >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test,
        y_pred,
        labels=[1],
        zero_division=0,
    )

    return {
        "precision_churn": float(precision[0]),
        "recall_churn": float(recall[0]),
        "f1_churn": float(f1[0]),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "classification_report": classification_report(y_test, y_pred),
    }


def write_report(metrics_default, metrics_selected, roc_auc):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    report = f"""# Customer Churn Model Evaluation

## Model

```text
Algorithm: Gradient Boosting Classifier
Target: is_churned
Dataset: Telco Customer Churn
ROC-AUC: {roc_auc:.4f}
Selected threshold: {SELECTED_THRESHOLD}
```

## Threshold 0.50

```text
Precision churn: {metrics_default["precision_churn"]:.4f}
Recall churn: {metrics_default["recall_churn"]:.4f}
F1 churn: {metrics_default["f1_churn"]:.4f}
```

Confusion matrix:

```text
{metrics_default["confusion_matrix"]}
```

Classification report:

```text
{metrics_default["classification_report"]}
```

## Selected Threshold {SELECTED_THRESHOLD}

```text
Precision churn: {metrics_selected["precision_churn"]:.4f}
Recall churn: {metrics_selected["recall_churn"]:.4f}
F1 churn: {metrics_selected["f1_churn"]:.4f}
```

Confusion matrix:

```text
{metrics_selected["confusion_matrix"]}
```

Classification report:

```text
{metrics_selected["classification_report"]}
```

## Business Interpretation

The selected threshold improves churn recall, helping the business identify more at-risk customers for retention campaigns. The trade-off is lower precision, meaning some customers flagged as high risk may not churn.

Key churn risk signals from EDA:

```text
- Month-to-month contract
- Short tenure
- High monthly charges
- Electronic check payment
- Lack of support services such as online security or tech support
```
"""

    REPORT_PATH.write_text(report, encoding="utf-8")


def train_model():
    df = pd.read_csv(DATA_PATH)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET]

    numeric_features = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_features = [col for col in X.columns if col not in numeric_features]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = build_pipeline(numeric_features, categorical_features)
    model.fit(X_train, y_train)

    y_proba = model.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_proba)

    metrics_default = evaluate_threshold(y_test, y_proba, 0.50)
    metrics_selected = evaluate_threshold(y_test, y_proba, SELECTED_THRESHOLD)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "threshold": SELECTED_THRESHOLD,
            "feature_columns": FEATURE_COLUMNS,
            "roc_auc": roc_auc,
        },
        MODEL_PATH,
    )
    write_report(metrics_default, metrics_selected, roc_auc)

    print(f"ROC-AUC: {roc_auc:.4f}")
    print(f"Selected threshold: {SELECTED_THRESHOLD}")
    print(f"Recall churn: {metrics_selected['recall_churn']:.4f}")
    print(f"Precision churn: {metrics_selected['precision_churn']:.4f}")
    print(f"F1 churn: {metrics_selected['f1_churn']:.4f}")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    train_model()