from pathlib import Path
import os

import pandas as pd
import psycopg2


BASE_DIR = Path(__file__).resolve().parents[1]


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": 5432,
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


required_env = [
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
]

missing_env = [var for var in required_env if not os.getenv(var)]

if missing_env:
    raise RuntimeError(
        "Faltan variables de entorno requeridas: "
        + ", ".join(missing_env)
    )


CUSTOMERS_FILE = (
    BASE_DIR / "processing" / "customers" / "customers_clean.csv"
)

SALES_FILE = (
    BASE_DIR / "processing" / "sales" / "sales_clean.csv"
)

PRODUCTS_FILE = (
    BASE_DIR / "processing" / "products" / "products_clean.csv"
)


def truncate_tables(connection):
    cursor = connection.cursor()

    cursor.execute("""
        TRUNCATE TABLE
            retail_staging.sales,
            retail_staging.products,
            retail_staging.customers
        RESTART IDENTITY CASCADE;
    """)

    connection.commit()
    cursor.close()

    print("Tablas staging limpiadas correctamente")


def load_dataframe(connection, df, table_name):
    cursor = connection.cursor()

    columns = ", ".join(
        f'"{column}"' for column in df.columns
    )

    placeholders = ", ".join(
        ["%s"] * len(df.columns)
    )

    query = f"""
        INSERT INTO retail_staging.{table_name}
        ({columns})
        VALUES ({placeholders})
    """

    for row in df.itertuples(index=False, name=None):
        cursor.execute(query, row)

    connection.commit()
    cursor.close()

    print(
        f"{table_name}: {len(df)} registros cargados"
    )


def create_tables(connection):
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS retail_staging.customers (
            customer_id VARCHAR(20) PRIMARY KEY,
            signup_date DATE,
            city VARCHAR(100),
            segment VARCHAR(50)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS retail_staging.products (
            product_id INTEGER PRIMARY KEY,
            category VARCHAR(100),
            brand VARCHAR(100),
            description TEXT,
            price NUMERIC(12,2)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS retail_staging.sales (
            sale_id VARCHAR(20) PRIMARY KEY,
            customer_id VARCHAR(20),
            product_id INTEGER,
            timestamp TIMESTAMP,
            quantity INTEGER,
            unit_price NUMERIC(12,2),
            total_line NUMERIC(14,2)
        );
    """)

    connection.commit()
    cursor.close()

    print("Tablas staging creadas correctamente")


def load_staging():
    print("Conectando a PostgreSQL...")

    connection = psycopg2.connect(**DB_CONFIG)

    try:
        create_tables(connection)
        truncate_tables(connection)

        customers = pd.read_csv(CUSTOMERS_FILE)
        products = pd.read_csv(PRODUCTS_FILE)
        sales = pd.read_csv(SALES_FILE)

        # Convertir NaN a None para PostgreSQL
        customers = customers.where(
            pd.notnull(customers),
            None
        )

        products = products.where(
            pd.notnull(products),
            None
        )

        sales = sales.where(
            pd.notnull(sales),
            None
        )

        load_dataframe(
            connection,
            customers,
            "customers"
        )

        load_dataframe(
            connection,
            products,
            "products"
        )

        load_dataframe(
            connection,
            sales,
            "sales"
        )

    finally:
        connection.close()

    print("\nCarga staging finalizada.")


if __name__ == "__main__":
    load_staging()