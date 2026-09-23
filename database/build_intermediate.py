from pathlib import Path
import psycopg2
import os


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": 5432,
    "database": "retaildb",
    "user": "retail_user",
    "password": "retail_password",
}


def build_intermediate():
    print("Construyendo capa intermediate...")

    connection = psycopg2.connect(**DB_CONFIG)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DROP TABLE IF EXISTS retail_intermediate.sales_enriched;
        """)

        cursor.execute("""
            CREATE TABLE retail_intermediate.sales_enriched AS
            SELECT
                s.sale_id,
                s.customer_id,
                c.city,
                c.segment,
                c.signup_date,

                s.product_id,
                p.category,
                p.brand,
                p.description,

                s.timestamp,
                s.quantity,
                s.unit_price,
                s.total_line

            FROM retail_staging.sales s

            INNER JOIN retail_staging.customers c
                ON s.customer_id = c.customer_id

            INNER JOIN retail_staging.products p
                ON s.product_id = p.product_id;
        """)

        connection.commit()

        cursor.execute("""
            SELECT COUNT(*)
            FROM retail_intermediate.sales_enriched;
        """)

        count = cursor.fetchone()[0]

        print(
            f"Registros en sales_enriched: {count}"
        )

    finally:
        cursor.close()
        connection.close()

    print("Capa intermediate construida correctamente.")


if __name__ == "__main__":
    build_intermediate()