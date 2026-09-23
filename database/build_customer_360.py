import psycopg2
import os


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": 5432,
    "database": "retaildb",
    "user": "retail_user",
    "password": "retail_password",
}


def build_customer_360():
    print("Construyendo Customer 360...")

    connection = psycopg2.connect(**DB_CONFIG)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DROP TABLE IF EXISTS retail_mart.customer_360;
        """)

        cursor.execute("""
            CREATE TABLE retail_mart.customer_360 AS

            SELECT
                customer_id,
                MAX(city) AS city,
                MAX(segment) AS segment,
                MIN(signup_date) AS signup_date,

                COUNT(DISTINCT sale_id) AS total_purchases,

                SUM(quantity) AS total_quantity,

                ROUND(
                    SUM(total_line),
                    2
                ) AS total_spent,

                ROUND(
                    SUM(total_line)
                    / NULLIF(
                        COUNT(DISTINCT sale_id),
                        0
                    ),
                    2
                ) AS average_ticket,

                MAX(timestamp) AS last_purchase_date,

                COUNT(DISTINCT product_id) AS unique_products

            FROM retail_intermediate.sales_enriched

            GROUP BY customer_id;
        """)

        connection.commit()

        cursor.execute("""
            SELECT COUNT(*)
            FROM retail_mart.customer_360;
        """)

        count = cursor.fetchone()[0]

        print(
            f"Clientes con compras: {count}"
        )

    finally:
        cursor.close()
        connection.close()

    print(
        "Customer 360 construido correctamente."
    )


if __name__ == "__main__":
    build_customer_360()