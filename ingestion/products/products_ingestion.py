from pathlib import Path
from datetime import datetime
import json
import urllib.request


BASE_DIR = Path(__file__).resolve().parents[2]
RAW_PRODUCTS = BASE_DIR / "raw" / "products"

API_URL = "https://dummyjson.com/products"


def extract_products():
    print("Iniciando extracción de productos...")
    print(f"Fuente: {API_URL}")

    request = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

        products = data.get("products", [])

        if not products:
            raise ValueError("La API no devolvió productos.")

        RAW_PRODUCTS.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = RAW_PRODUCTS / f"products_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        print(f"Productos obtenidos: {len(products)}")
        print(f"Archivo RAW: {output_file}")

        return output_file

    except Exception as e:
        print(f"ERROR durante la extracción: {e}")
        raise


if __name__ == "__main__":
    extract_products()