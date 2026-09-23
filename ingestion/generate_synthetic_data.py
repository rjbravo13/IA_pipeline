from pathlib import Path
import random
from datetime import datetime, timedelta

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_CUSTOMERS = BASE_DIR / "raw" / "customers"
RAW_SALES = BASE_DIR / "raw" / "sales"


def generate_customers():
    random.seed(42)

    cities = [
        "Lima",
        "Arequipa",
        "Trujillo",
        "Cusco",
        "Piura",
    ]

    segments = [
        "retail",
        "premium",
        "corporate",
    ]

    customers = []

    for i in range(1, 101):

        signup_date = datetime(2024, 1, 1) + timedelta(
            days=random.randint(0, 700)
        )

        customers.append(
            {
                "customer_id": f"C{i:04d}",
                "signup_date": signup_date.date(),
                "city": random.choice(cities),
                "segment": random.choice(segments),
            }
        )

    df = pd.DataFrame(customers)

    RAW_CUSTOMERS.mkdir(parents=True, exist_ok=True)

    output = RAW_CUSTOMERS / "customers.csv"

    df.to_csv(output, index=False)

    print(f"Clientes generados: {len(df)}")
    print(f"Archivo: {output}")


def generate_sales():

    random.seed(42)

    products = list(range(1, 31))

    sales = []

    start_date = datetime(2025, 1, 1)

    for i in range(1, 1001):

        timestamp = start_date + timedelta(
            days=random.randint(0, 600),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        quantity = random.randint(1, 5)

        unit_price = round(
            random.uniform(10, 500),
            2,
        )

        sales.append(
            {
                "sale_id": f"S{i:06d}",
                "customer_id": f"C{random.randint(1, 100):04d}",
                "product_id": random.choice(products),
                "timestamp": timestamp,
                "quantity": quantity,
                "unit_price": unit_price,
            }
        )

    df = pd.DataFrame(sales)

    RAW_SALES.mkdir(parents=True, exist_ok=True)

    output = RAW_SALES / "sales.csv"

    df.to_csv(output, index=False)

    print(f"Ventas generadas: {len(df)}")
    print(f"Archivo: {output}")


if __name__ == "__main__":

    print("Generando datos sintéticos...\n")

    generate_customers()
    generate_sales()

    print("\nProceso finalizado.")