from pathlib import Path
import json
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_DIR = BASE_DIR / "raw" / "products"
OUTPUT_DIR = BASE_DIR / "processing" / "products"
OUTPUT_FILE = OUTPUT_DIR / "products_clean.csv"


def get_latest_raw_file():
    files = sorted(INPUT_DIR.glob("products_*.json"))

    if not files:
        raise FileNotFoundError(
            "No se encontró ningún archivo RAW de productos."
        )

    return files[-1]


def process_products():
    input_file = get_latest_raw_file()

    print("Procesando productos...")
    print(f"Entrada: {input_file}")

    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    products = data.get("products", [])

    if not products:
        raise ValueError("El archivo RAW no contiene productos.")

    print(f"Registros RAW: {len(products)}")

    df = pd.DataFrame(products)

    df = df.rename(
        columns={
            "id": "product_id"
        }
    )

    df = df[
        [
            "product_id",
            "category",
            "brand",
            "description",
            "price",
        ]
    ]

    df["product_id"] = pd.to_numeric(
        df["product_id"],
        errors="coerce"
    )

    df["category"] = (
        df["category"]
        .astype("string")
        .str.strip()
    )

    df["brand"] = (
        df["brand"]
        .astype("string")
        .str.strip()
    )

    df["description"] = (
        df["description"]
        .astype("string")
        .str.strip()
    )

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    df = df.drop_duplicates(
        subset=["product_id"]
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Registros procesados: {len(df)}")
    print(f"Archivo generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    process_products()