import psycopg2
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": 5432,
    "database": "retaildb",
    "user": "retail_user",
    "password": "retail_password",
}


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