
from pathlib import Path

import pyarrow.parquet as pq
from google.cloud import bigquery


PROJECT_ID = "mapslocate-412012"
DATASET = "bigquery-public-data.thelook_ecommerce"
LOCATION = "US"

OUTPUT_DIR = Path("data/raw")

# Maximum BigQuery bytes billed per table.
# Each limit is above its corresponding dry-run estimate.
TABLES = {
    "users": 25,
    "products": 10,
    "orders": 10,
    "order_items": 20,
    "inventory_items": 100,
}


def download_table(
    client: bigquery.Client,
    table_name: str,
    max_bytes_mb: int,
) -> None:
    """Download one BigQuery table into a local Parquet file."""

    print(f"\nDownloading: {table_name}")

    query = f"""
        SELECT *
        FROM `{DATASET}.{table_name}`
    """

    config = bigquery.QueryJobConfig(
        maximum_bytes_billed=max_bytes_mb * 1024 * 1024,
        use_query_cache=False,
    )

    job = client.query(
        query,
        job_config=config,
        location=LOCATION,
    )

    result = job.result()

    table = result.to_arrow(
        create_bqstorage_client=False
    )

    output_path = OUTPUT_DIR / f"{table_name}.parquet"

    pq.write_table(
        table,
        output_path,
        compression="zstd",
    )

    file_size_mb = output_path.stat().st_size / (1024 * 1024)

    print(f"Rows downloaded: {table.num_rows:,}")
    print(f"Columns: {len(table.column_names)}")
    print(f"Bytes processed: {job.total_bytes_processed:,}")
    print(f"Local file size: {file_size_mb:.2f} MB")
    print(f"Saved to: {output_path}")


def main():
    client = bigquery.Client(project=PROJECT_ID)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for table_name, max_bytes_mb in TABLES.items():
        download_table(
            client,
            table_name,
            max_bytes_mb,
        )

    print("\nAll five tables downloaded successfully.")


if __name__ == "__main__":
    main()
