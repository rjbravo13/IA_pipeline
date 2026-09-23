import psycopg2
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": 5432,
    "database": "retaildb",
    "user": "retail_user",
    "password": "retail_password",
}


def check_features():
    connection = psycopg2.connect(**DB_CONFIG)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                customer_id,
                city,
                segment,
                total_purchases,
                total_quantity,
                total_spent,
                average_ticket,
                unique_products,
                recency_days,
                at_risk
            FROM retail_mart.customer_features
            ORDER BY customer_id
            LIMIT 10;
        """)

        rows = cursor.fetchall()

        print("\nFEATURES DE CUSTOMER 360")
        print("=" * 130)

        for row in rows:
            print(row)

        print("=" * 130)

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    check_features()