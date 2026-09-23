from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "customer_risk_model_mlflow.joblib"
)

DATABASE_URL = (
    "postgresql+psycopg2://"
    "retail_user:retail_password@localhost:5432/retaildb"
)


# ============================================================
# APLICACIÓN
# ============================================================

app = FastAPI(
    title="Retail Customer 360 API",
    description="API para consultar Customer 360 y predecir riesgo de clientes",
    version="1.0.0",
)


# ============================================================
# BASE DE DATOS
# ============================================================

engine = create_engine(DATABASE_URL)


# ============================================================
# MODELO ML
# ============================================================

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print(f"Error cargando el modelo: {e}")


# ============================================================
# MODELOS DE RESPUESTA
# ============================================================

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class PredictionResponse(BaseModel):
    customer_id: str
    at_risk: int
    prediction: str
    risk_probability: float


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health", response_model=HealthResponse)
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
    }


# ============================================================
# PREDICCIÓN
# ============================================================

@app.get(
    "/predict/{customer_id}",
    response_model=PredictionResponse,
)
def predict(customer_id: str):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="El modelo ML no pudo ser cargado.",
        )

    query = text("""
        SELECT
            city,
            segment,
            total_purchases,
            total_quantity,
            total_spent,
            average_ticket,
            unique_products
        FROM retail_mart.customer_features
        WHERE customer_id = :customer_id
    """)

    try:
        with engine.connect() as connection:

            result = connection.execute(
                query,
                {"customer_id": customer_id},
            )

            row = result.fetchone()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error conectando a PostgreSQL: {str(e)}",
        )

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Cliente {customer_id} no encontrado.",
        )

    features = pd.DataFrame([{
        "city": row.city,
        "segment": row.segment,
        "total_purchases": int(row.total_purchases),
        "total_quantity": int(row.total_quantity),
        "total_spent": float(row.total_spent),
        "average_ticket": float(row.average_ticket),
        "unique_products": int(row.unique_products),
    }])

    prediction = int(model.predict(features)[0])

    probability = float(
        model.predict_proba(features)[0][1]
    )

    return {
        "customer_id": customer_id,
        "at_risk": prediction,
        "prediction": (
            "Cliente en riesgo"
            if prediction == 1
            else "Cliente no está en riesgo"
        ),
        "risk_probability": probability,
    }