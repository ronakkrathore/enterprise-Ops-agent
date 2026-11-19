
from google.cloud import bigquery


PROJECT_ID = "mapslocate-412012"
DATASET = "bigquery-public-data.thelook_ecommerce"
LOCATION = "US"

TABLES = [
    "users",
    "products",
    "orders",
    "order_items",
    "inventory_items",
]


def estimate_table_sizes():
    client = bigquery.Client(project=PROJECT_ID)

    print("Estimating BigQuery query sizes...\n")

    for table_name in TABLES:
        query = f"""
            SELECT *
            FROM `{DATASET}.{table_name}`
        """

        config = bigquery.QueryJobConfig(
            dry_run=True,
            use_query_cache=False,
        )

        job = client.query(
            query,
            job_config=config,
            location=LOCATION,
        )

        size_mb = job.total_bytes_processed / (1024 * 1024)

        print(f"Table: {table_name}")
        print(f"Estimated bytes: {job.total_bytes_processed:,}")
        print(f"Estimated size: {size_mb:.2f} MB")
        print("-" * 40)


if __name__ == "__main__":
    estimate_table_sizes()
