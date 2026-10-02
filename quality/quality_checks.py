from pathlib import Path
import pandas as pd
import json


BASE_DIR = Path(__file__).resolve().parents[1]

CUSTOMERS_FILE = (
    BASE_DIR / "processing" / "customers" / "customers_clean.csv"
)

SALES_FILE = (
    BASE_DIR / "processing" / "sales" / "sales_clean.csv"
)

PRODUCTS_FILE = (
    BASE_DIR / "processing" / "products" / "products_clean.csv"
)

REPORTS_DIR = BASE_DIR / "quality" / "reports"
REPORT_FILE = REPORTS_DIR / "quality_report.json"


def check_not_null(df, column):
    return int(df[column].isna().sum()) == 0


def check_unique(df, column):
    return df[column].is_unique


def check_greater_than_zero(df, column):
    return (df[column] > 0).all()


def check_greater_equal_zero(df, column):
    return (df[column] >= 0).all()


def check_valid_dates(df, column):
    return df[column].notna().all()


def check_foreign_keys(sales, reference, sales_column, reference_column):
    sales_values = set(sales[sales_column].dropna())
    reference_values = set(reference[reference_column].dropna())

    return sales_values.issubset(reference_values)


def check_total_line(sales):
    calculated = sales["quantity"] * sales["unit_price"]

    difference = (
        (sales["total_line"] - calculated)
        .abs()
    )

    return (difference <= 0.01).all()


def add_result(results, rule, passed, blocking=False):
    results.append(
        {
            "rule": rule,
            "status": "PASS" if passed else "FAIL",
            "blocking": blocking,
        }
    )


def run_quality_checks():
    print("Iniciando controles de calidad...\n")

    customers = pd.read_csv(CUSTOMERS_FILE)
    sales = pd.read_csv(SALES_FILE)
    products = pd.read_csv(PRODUCTS_FILE)

    results = []

    add_result(
        results,
        "customers.customer_id no nulo",
        check_not_null(customers, "customer_id"),
        blocking=True,
    )

    add_result(
        results,
        "customers.customer_id único",
        check_unique(customers, "customer_id"),
        blocking=True,
    )

    add_result(
        results,
        "products.product_id no nulo",
        check_not_null(products, "product_id"),
        blocking=True,
    )

    add_result(
        results,
        "products.product_id único",
        check_unique(products, "product_id"),
        blocking=True,
    )

    add_result(
        results,
        "products.price >= 0",
        check_greater_equal_zero(products, "price"),
        blocking=False,
    )

    add_result(
        results,
        "sales.sale_id único",
        check_unique(sales, "sale_id"),
        blocking=True,
    )

    add_result(
        results,
        "sales.customer_id no nulo",
        check_not_null(sales, "customer_id"),
        blocking=True,
    )

    add_result(
        results,
        "sales.product_id no nulo",
        check_not_null(sales, "product_id"),
        blocking=True,
    )

    add_result(
        results,
        "sales.quantity > 0",
        check_greater_than_zero(sales, "quantity"),
        blocking=True,
    )

    add_result(
        results,
        "sales.unit_price >= 0",
        check_greater_equal_zero(sales, "unit_price"),
        blocking=True,
    )

    add_result(
        results,
        "sales.timestamp válido",
        check_valid_dates(sales, "timestamp"),
        blocking=True,
    )

    add_result(
        results,
        "sales.customer_id existe en customers",
        check_foreign_keys(
            sales,
            customers,
            "customer_id",
            "customer_id",
        ),
        blocking=True,
    )

    add_result(
        results,
        "sales.product_id existe en products",
        check_foreign_keys(
            sales,
            products,
            "product_id",
            "product_id",
        ),
        blocking=True,
    )

    add_result(
        results,
        "sales.total_line consistente",
        check_total_line(sales),
        blocking=True,
    )

    passed = sum(
        1 for result in results
        if result["status"] == "PASS"
    )

    failed = sum(
        1 for result in results
        if result["status"] == "FAIL"
    )

    blocking_failures = [
        result
        for result in results
        if result["status"] == "FAIL"
        and result["blocking"]
    ]

    report = {
        "summary": {
            "total_rules": len(results),
            "passed": passed,
            "failed": failed,
            "blocking_failures": len(blocking_failures),
        },
        "results": results,
    }

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("RESULTADOS DE CALIDAD")
    print("=" * 60)

    for result in results:
        print(
            f"{result['status']:4} | "
            f"{result['rule']}"
        )

    print("=" * 60)
    print(f"Reglas evaluadas : {len(results)}")
    print(f"PASS             : {passed}")
    print(f"FAIL             : {failed}")
    print(
        f"Fallos bloqueantes: "
        f"{len(blocking_failures)}"
    )

    print(f"\nReporte generado:")
    print(REPORT_FILE)

    if blocking_failures:
        print(
            "\nERROR: existen reglas "
            "bloqueantes que fallaron."
        )

        raise RuntimeError(
            "Proceso detenido por fallos de calidad."
        )

    print("\nTodos los controles de calidad pasaron.")


if __name__ == "__main__":
    run_quality_checks()