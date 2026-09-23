from pathlib import Path
import json

import joblib
import pandas as pd
import psycopg2
import os

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)


BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_DIR = BASE_DIR / "ml" / "models"
REPORT_DIR = BASE_DIR / "ml" / "reports"

MODEL_FILE = MODEL_DIR / "customer_risk_model.joblib"
METRICS_FILE = REPORT_DIR / "metrics.json"


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": 5432,
    "database": "retaildb",
    "user": "retail_user",
    "password": "retail_password",
}


def load_features():
    connection = psycopg2.connect(**DB_CONFIG)

    try:
        query = """
            SELECT
                customer_id,
                city,
                segment,
                total_purchases,
                total_quantity,
                total_spent,
                average_ticket,
                unique_products,
                at_risk
            FROM retail_mart.customer_features;
        """

        df = pd.read_sql_query(
            query,
            connection
        )

    finally:
        connection.close()

    return df


def train_model():
    print("Cargando features...")

    df = load_features()

    print(f"Registros: {len(df)}")

    # ---------------------------------------------------------
    # Features y target
    # ---------------------------------------------------------

    feature_columns = [
        "city",
        "segment",
        "total_purchases",
        "total_quantity",
        "total_spent",
        "average_ticket",
        "unique_products",
    ]

    target_column = "at_risk"

    X = df[feature_columns]
    y = df[target_column]

    # ---------------------------------------------------------
    # Separar train / test
    # ---------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print(f"Train: {len(X_train)}")
    print(f"Test : {len(X_test)}")

    # ---------------------------------------------------------
    # Columnas
    # ---------------------------------------------------------

    categorical_features = [
        "city",
        "segment",
    ]

    numeric_features = [
        "total_purchases",
        "total_quantity",
        "total_spent",
        "average_ticket",
        "unique_products",
    ]

    # ---------------------------------------------------------
    # Preprocesamiento
    # ---------------------------------------------------------

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features,
            ),
            (
                "numeric",
                StandardScaler(),
                numeric_features,
            ),
        ]
    )

    # ---------------------------------------------------------
    # Modelo
    # ---------------------------------------------------------

    model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )

    print("\nEntrenando modelo...")

    model.fit(
        X_train,
        y_train
    )

    # ---------------------------------------------------------
    # Predicción
    # ---------------------------------------------------------

    y_pred = model.predict(X_test)

    # ---------------------------------------------------------
    # Métricas
    # ---------------------------------------------------------

    metrics = {
        "accuracy": accuracy_score(
            y_test,
            y_pred,
        ),
        "precision": precision_score(
            y_test,
            y_pred,
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            y_pred,
            zero_division=0,
        ),
        "f1": f1_score(
            y_test,
            y_pred,
            zero_division=0,
        ),
    }

    print("\nMÉTRICAS")
    print("=" * 50)

    for metric, value in metrics.items():
        print(
            f"{metric:10}: "
            f"{value:.4f}"
        )

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            y_pred,
            zero_division=0,
        )
    )

    # ---------------------------------------------------------
    # Guardar modelo
    # ---------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_FILE,
    )

    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "model": "LogisticRegression",
                "random_state": 42,
                "test_size": 0.20,
                "features": feature_columns,
                "target": target_column,
                "metrics": metrics,
            },
            file,
            indent=2,
        )

    print("\nModelo guardado:")
    print(MODEL_FILE)

    print("\nMétricas guardadas:")
    print(METRICS_FILE)


if __name__ == "__main__":
    train_model()