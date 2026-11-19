
from pathlib import Path

import duckdb


DATA_DIR = Path("data/raw")

EXPECTED_ROWS = {
    "distribution_centers": 10,
    "users": 100_000,
    "products": 29_120,
    "orders": 124_780,
    "order_items": 180_764,
    "inventory_items": 487_709,
}


def main():
    connection = duckdb.connect()

    total_rows = 0
    all_valid = True

    print("Verifying local Parquet files...\n")

    for table_name, expected_count in EXPECTED_ROWS.items():
        file_path = DATA_DIR / f"{table_name}.parquet"

        if not file_path.exists():
            print(f"MISSING: {table_name}")
            all_valid = False
            continue

        actual_count = connection.execute(
            "SELECT COUNT(*) FROM read_parquet(?)",
            [str(file_path)],
        ).fetchone()[0]

        total_rows += actual_count

        valid = actual_count == expected_count
        all_valid = all_valid and valid

        print(
            f"{table_name}: "
            f"{actual_count:,} rows | "
            f"{'PASS' if valid else 'FAIL'}"
        )

    print("\nTotal records:", f"{total_rows:,}")
    print("Verification:", "PASSED" if all_valid else "FAILED")

    connection.close()

    if not all_valid:
        raise RuntimeError("Raw data verification failed.")


if __name__ == "__main__":
    main()
