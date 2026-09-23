from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "raw" / "sales" / "sales.csv"
OUTPUT_DIR = BASE_DIR / "processing" / "sales"
OUTPUT_FILE = OUTPUT_DIR / "sales_clean.csv"


def process_sales():
    print("Procesando ventas...")
    print(f"Entrada: {INPUT_FILE}")

    # Leer RAW
    df = pd.read_csv(INPUT_FILE)

    print(f"Registros RAW: {len(df)}")

    # Seleccionar columnas del modelo
    df = df[
        [
            "sale_id",
            "customer_id",
            "product_id",
            "timestamp",
            "quantity",
            "unit_price",
        ]
    ]

    # Tipos de datos
    df["sale_id"] = df["sale_id"].astype("string")
    df["customer_id"] = df["customer_id"].astype("string")

    df["product_id"] = pd.to_numeric(
        df["product_id"],
        errors="coerce"
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    )

    df["unit_price"] = pd.to_numeric(
        df["unit_price"],
        errors="coerce"
    )

    # Eliminar duplicados de venta
    df = df.drop_duplicates(subset=["sale_id"])

    # Calcular total de la línea
    df["total_line"] = (
        df["quantity"] * df["unit_price"]
    )

    # Crear carpeta de salida
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Guardar datos procesados
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Registros procesados: {len(df)}")
    print(f"Archivo generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    process_sales()