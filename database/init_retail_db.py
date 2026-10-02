import os

import psycopg2


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


def create_schemas():
    print("Conectando a PostgreSQL...")

    connection = psycopg2.connect(**DB_CONFIG)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS retail_staging;
        """)

        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS retail_intermediate;
        """)

        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS retail_mart;
        """)

        connection.commit()

        print("\nEsquemas creados correctamente:")
        print(" - retail_staging")
        print(" - retail_intermediate")
        print(" - retail_mart")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_schemas()