from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_DIR = "/opt/airflow/project"


with DAG(
    dag_id="retail_customer_360",
    description="Pipeline Retail Customer 360",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["retail", "customer360", "ml"],
) as dag:

    generate_data = BashOperator(
        task_id="generate_synthetic_data",
        bash_command=(
            f"python {PROJECT_DIR}/ingestion/generate_synthetic_data.py"
        ),
    )

    ingest_products = BashOperator(
        task_id="ingest_products",
        bash_command=(
            f"python {PROJECT_DIR}/ingestion/products/products_ingestion.py"
        ),
    )

    process_customers = BashOperator(
        task_id="process_customers",
        bash_command=(
            f"python {PROJECT_DIR}/processing/customers/customers_processing.py"
        ),
    )

    process_sales = BashOperator(
        task_id="process_sales",
        bash_command=(
            f"python {PROJECT_DIR}/processing/sales/sales_processing.py"
        ),
    )

    process_products = BashOperator(
        task_id="process_products",
        bash_command=(
            f"python {PROJECT_DIR}/processing/products/products_processing.py"
        ),
    )

    quality_checks = BashOperator(
        task_id="quality_checks",
        bash_command=(
            f"python {PROJECT_DIR}/quality/quality_checks.py"
        ),
    )

    init_database = BashOperator(
        task_id="init_retail_db",
        bash_command=(
            f"python {PROJECT_DIR}/database/init_retail_db.py"
        ),
    )

    load_staging = BashOperator(
        task_id="load_staging",
        bash_command=(
            f"python {PROJECT_DIR}/database/load_staging.py"
        ),
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            f"cd {PROJECT_DIR}/dbt && "
            "dbt build --profiles-dir ."
        ),
    )

    build_features = BashOperator(
        task_id="build_features",
        bash_command=(
            f"python {PROJECT_DIR}/database/build_features.py"
        ),
    )

    train_model = BashOperator(
        task_id="train_model_mlflow",
        bash_command=(
            f"python {PROJECT_DIR}/ml/train_model_mlflow.py"
        ),
    )

    (
        generate_data
        >> [process_customers, process_sales]
    )

    ingest_products >> process_products

    (
        [process_customers, process_sales, process_products]
        >> quality_checks
        >> init_database
        >> load_staging
        >> dbt_build
        >> build_features
        >> train_model
    )