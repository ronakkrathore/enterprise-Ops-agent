
from pathlib import Path

import duckdb


DATABASE_PATH = Path("data/database/analytics.duckdb")
DATA_DIR = Path("data/raw")

TABLES = [
    "distribution_centers",
    "users",
    "products",
    "orders",
    "order_items",
    "inventory_items",
]


def main():
    connection = duckdb.connect(str(DATABASE_PATH))

    try:
        connection.execute("CREATE SCHEMA IF NOT EXISTS raw")

        connection.execute("BEGIN TRANSACTION")

        for table_name in TABLES:
            file_path = DATA_DIR / f"{table_name}.parquet"

            if not file_path.exists():
                raise FileNotFoundError(file_path)

            connection.execute(
                f"""
                CREATE OR REPLACE TABLE raw.{table_name} AS
                SELECT *
                FROM read_parquet(?)
                """,
                [str(file_path)],
            )

            row_count = connection.execute(
                f"SELECT COUNT(*) FROM raw.{table_name}"
            ).fetchone()[0]

            print(f"Loaded raw.{table_name}: {row_count:,} rows")

        connection.execute("COMMIT")

        print("\nAll raw tables loaded successfully.")

    except Exception:
        connection.execute("ROLLBACK")
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()
