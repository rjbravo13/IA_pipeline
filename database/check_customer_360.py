import psycopg2
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": 5432,
    "database": "retaildb",
    "user": "retail_user",
    "password": "retail_password",
}


def check_customer_360():
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
                last_purchase_date,
                unique_products
            FROM retail_mart.customer_360
            ORDER BY total_spent DESC
            LIMIT 10;
        """)

        rows = cursor.fetchall()

        print("\nTOP 10 CLIENTES POR GASTO")
        print("=" * 110)

        for row in rows:
            print(row)

        print("=" * 110)

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    check_customer_360()