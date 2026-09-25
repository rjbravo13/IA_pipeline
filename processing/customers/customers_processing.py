from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "raw" / "customers" / "customers.csv"
OUTPUT_DIR = BASE_DIR / "processing" / "customers"
OUTPUT_FILE = OUTPUT_DIR / "customers_clean.csv"


def process_customers():
    print("Procesando clientes...")
    print(f"Entrada: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Registros RAW: {len(df)}")

    df = df[
        [
            "customer_id",
            "signup_date",
            "city",
            "segment",
        ]
    ]

    df["customer_id"] = df["customer_id"].astype("string")
    df["signup_date"] = pd.to_datetime(
        df["signup_date"],
        errors="coerce"
    )
    df["city"] = df["city"].astype("string").str.strip()
    df["segment"] = df["segment"].astype("string").str.strip()

    df = df.drop_duplicates(subset=["customer_id"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Registros procesados: {len(df)}")
    print(f"Archivo generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    process_customers()