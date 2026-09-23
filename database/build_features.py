import psycopg2
import os


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": 5432,
    "database": "retaildb",
    "user": "retail_user",
    "password": "retail_password",
}


def build_features():
    print("Construyendo features de clientes...")

    connection = psycopg2.connect(**DB_CONFIG)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DROP TABLE IF EXISTS retail_mart.customer_features;
        """)

        cursor.execute("""
            CREATE TABLE retail_mart.customer_features AS

            WITH reference_date AS (
                SELECT
                    MAX(last_purchase_date)::date AS max_purchase_date
                FROM retail_mart.customer_360
            )

            SELECT
                c.customer_id,
                c.city,
                c.segment,

                c.total_purchases,
                c.total_quantity,
                c.total_spent,
                c.average_ticket,
                c.unique_products,

                (
                    r.max_purchase_date
                    - c.last_purchase_date::date
                ) AS recency_days,

                CASE
                    WHEN (
                        r.max_purchase_date
                        - c.last_purchase_date::date
                    ) > 30
                    THEN 1
                    ELSE 0
                END AS at_risk

            FROM retail_mart.customer_360 c

            CROSS JOIN reference_date r;
        """)

        connection.commit()

        cursor.execute("""
            SELECT COUNT(*)
            FROM retail_mart.customer_features;
        """)

        count = cursor.fetchone()[0]

        print(
            f"Clientes con features: {count}"
        )

        cursor.execute("""
            SELECT
                at_risk,
                COUNT(*)
            FROM retail_mart.customer_features
            GROUP BY at_risk
            ORDER BY at_risk;
        """)

        print("\nDistribución del target:")

        for row in cursor.fetchall():
            print(
                f"at_risk={row[0]} -> "
                f"{row[1]} clientes"
            )

    finally:
        cursor.close()
        connection.close()

    print(
        "\nFeatures construidas correctamente."
    )


if __name__ == "__main__":
    build_features()