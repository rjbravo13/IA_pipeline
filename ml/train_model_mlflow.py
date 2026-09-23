from pathlib import Path
import json

import joblib
import mlflow
import mlflow.sklearn
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
)


BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_DIR = BASE_DIR / "ml" / "models"

MODEL_FILE = (
    MODEL_DIR / "customer_risk_model_mlflow.joblib"
)

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
            connection,
        )

    finally:
        connection.close()

    return df


def train_model():

    print("Cargando features...")

    df = load_features()

    print(f"Registros: {len(df)}")

    # ---------------------------------------------------------
    # Configuración MLflow
    # ---------------------------------------------------------

    mlflow.set_tracking_uri(
        "sqlite:///mlflow.db"
    )

    mlflow.set_experiment(
        "customer_risk_prediction"
    )

    # ---------------------------------------------------------
    # Features
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
    # Train / Test
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

    max_iter = 1000

    model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=max_iter,
                    random_state=42,
                ),
            ),
        ]
    )

    # ---------------------------------------------------------
    # MLflow Run
    # ---------------------------------------------------------

    with mlflow.start_run() as run:

        print("\nEntrenando modelo...")

        model.fit(
            X_train,
            y_train,
        )

        # -----------------------------------------------------
        # Predicción
        # -----------------------------------------------------

        y_pred = model.predict(X_test)

        # -----------------------------------------------------
        # Métricas
        # -----------------------------------------------------

        accuracy = accuracy_score(
            y_test,
            y_pred,
        )

        precision = precision_score(
            y_test,
            y_pred,
            zero_division=0,
        )

        recall = recall_score(
            y_test,
            y_pred,
            zero_division=0,
        )

        f1 = f1_score(
            y_test,
            y_pred,
            zero_division=0,
        )

        # -----------------------------------------------------
        # Parámetros
        # -----------------------------------------------------

        mlflow.log_param(
            "model",
            "LogisticRegression",
        )

        mlflow.log_param(
            "random_state",
            42,
        )

        mlflow.log_param(
            "test_size",
            0.20,
        )

        mlflow.log_param(
            "max_iter",
            max_iter,
        )

        mlflow.log_param(
            "num_records",
            len(df),
        )

        mlflow.log_param(
            "num_train_records",
            len(X_train),
        )

        mlflow.log_param(
            "num_test_records",
            len(X_test),
        )

        mlflow.log_param(
            "num_features",
            len(feature_columns),
        )

        mlflow.log_param(
            "target",
            target_column,
        )

        # -----------------------------------------------------
        # Métricas
        # -----------------------------------------------------

        mlflow.log_metric(
            "accuracy",
            accuracy,
        )

        mlflow.log_metric(
            "precision",
            precision,
        )

        mlflow.log_metric(
            "recall",
            recall,
        )

        mlflow.log_metric(
            "f1",
            f1,
        )

        # -----------------------------------------------------
        # Tags
        # -----------------------------------------------------

        mlflow.set_tag(
            "project",
            "Retail Customer 360",
        )

        mlflow.set_tag(
            "data_source",
            "PostgreSQL retail_mart.customer_features",
        )

        mlflow.set_tag(
            "target_definition",
            "recency_days > 30",
        )

        # -----------------------------------------------------
        # Guardar modelo local
        # -----------------------------------------------------

        MODEL_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            model,
            MODEL_FILE,
        )

        # -----------------------------------------------------
        # Registrar modelo en MLflow
        # -----------------------------------------------------

        mlflow.sklearn.log_model(
            model,
            name="customer_risk_model",
            skops_trusted_types=[
                "sklearn.compose._column_transformer._RemainderColsList"
            ]
        )

        print("\nMÉTRICAS")
        print("=" * 50)
        print(f"accuracy  : {accuracy:.4f}")
        print(f"precision : {precision:.4f}")
        print(f"recall    : {recall:.4f}")
        print(f"f1        : {f1:.4f}")

        print("\nMLflow Run ID:")
        print(run.info.run_id)

        print("\nModelo guardado:")
        print(MODEL_FILE)


if __name__ == "__main__":
    train_model()