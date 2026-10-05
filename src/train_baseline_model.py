from pathlib import Path
import duckdb
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


DUCKDB_PATH = Path("data/processed/safety.duckdb")
REPORTS_DIR = Path("reports/tables")
MODELS_DIR = Path("models")


TARGET = "high_severity_outcome"

FEATURES = [
    "event_month",
    "event_day_of_week",
    "state",
    "naics_2_digit",
    "naics_3_digit",
    "nature_title",
    "body_part_title",
    "event_title",
    "source_title",
    "secondary_source_title",
]


NUMERIC_FEATURES = [
    "event_month",
    "event_day_of_week",
]

CATEGORICAL_FEATURES = [
    "state",
    "naics_2_digit",
    "naics_3_digit",
    "nature_title",
    "body_part_title",
    "event_title",
    "source_title",
    "secondary_source_title",
]


def load_data() -> pd.DataFrame:
    con = duckdb.connect(str(DUCKDB_PATH))

    query = """
        SELECT
            event_year,
            event_month,
            event_day_of_week,
            state,
            naics_2_digit,
            naics_3_digit,
            nature_title,
            body_part_title,
            event_title,
            source_title,
            secondary_source_title,
            high_severity_outcome
        FROM ml_injury_features
    """

    df = con.execute(query).fetchdf()
    con.close()

    return df


def temporal_split(df: pd.DataFrame):
    train_df = df[df["event_year"] <= 2022].copy()
    valid_df = df[df["event_year"] == 2023].copy()
    test_df = df[df["event_year"] >= 2024].copy()

    return train_df, valid_df, test_df


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )

    return preprocessor


def evaluate_model(model_name: str, model, X, y) -> dict:
    y_pred = model.predict(X)

    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X)[:, 1]
    else:
        y_score = y_pred

    metrics = {
        "model": model_name,
        "accuracy": accuracy_score(y, y_pred),
        "precision": precision_score(y, y_pred, zero_division=0),
        "recall": recall_score(y, y_pred, zero_division=0),
        "f1": f1_score(y, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y, y_score),
        "pr_auc": average_precision_score(y, y_score),
    }

    tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()

    metrics.update(
        {
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp,
        }
    )

    return metrics


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()

    if df.empty:
        raise ValueError("No data found in ml_injury_features. Run `python src/run_sql.py` first.")

    train_df, valid_df, test_df = temporal_split(df)

    print(f"Train rows: {len(train_df):,}")
    print(f"Validation rows: {len(valid_df):,}")
    print(f"Test rows: {len(test_df):,}")

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_valid = valid_df[FEATURES]
    y_valid = valid_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    preprocessor = build_preprocessor()

    dummy_model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", DummyClassifier(strategy="most_frequent")),
        ]
    )

    logistic_model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    solver="liblinear",
                ),
            ),
        ]
    )

    print("\nTraining DummyClassifier...")
    dummy_model.fit(X_train, y_train)

    print("Training LogisticRegression...")
    logistic_model.fit(X_train, y_train)

    results = []

    for model_name, model in [
        ("dummy_most_frequent", dummy_model),
        ("logistic_regression_balanced", logistic_model),
    ]:
        valid_metrics = evaluate_model(
            model_name=f"{model_name}_validation",
            model=model,
            X=X_valid,
            y=y_valid,
        )

        test_metrics = evaluate_model(
            model_name=f"{model_name}_test",
            model=model,
            X=X_test,
            y=y_test,
        )

        results.extend([valid_metrics, test_metrics])

    metrics_df = pd.DataFrame(results)
    metrics_path = REPORTS_DIR / "baseline_model_metrics.csv"
    metrics_df.to_csv(metrics_path, index=False)

    model_path = MODELS_DIR / "logistic_regression_baseline.joblib"
    joblib.dump(logistic_model, model_path)

    print("\nModel metrics:")
    print(metrics_df)

    print(f"\nSaved metrics to: {metrics_path}")
    print(f"Saved model to: {model_path}")


if __name__ == "__main__":
    main()