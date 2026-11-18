import duckdb


def create_dim_customers(connection: duckdb.DuckDBPyConnection) -> None:
    """
    Create the customer dimension from raw.users.

    Grain:
        One row per customer.
    """

    connection.execute("""
        CREATE OR REPLACE TABLE curated.dim_customers AS
        SELECT
            id AS user_id,
            first_name,
            last_name,
            email,
            age,
            gender,
            city,
            state,
            country,
            postal_code,
            traffic_source,
            created_at
        FROM raw.users
    """)

def create_dim_products(connection: duckdb.DuckDBPyConnection) -> None:
    """
    Create the product dimension from raw.products.

    Grain:
        One row per product.
    """

    connection.execute("""
        CREATE OR REPLACE TABLE curated.dim_products AS
        SELECT
            id AS product_id,
            name AS product_name,
            brand,
            category,
            department,
            sku,
            cost,
            retail_price,
            distribution_center_id
        FROM raw.products
    """)

def create_dim_distribution_centers(
    connection: duckdb.DuckDBPyConnection
) -> None:
    """
    Create the distribution center dimension.

    Grain:
        One row per distribution center.
    """

    connection.execute("""
        CREATE OR REPLACE TABLE curated.dim_distribution_centers AS
        SELECT
            id AS distribution_center_id,
            name AS distribution_center_name,
            latitude,
            longitude
        FROM raw.distribution_centers
    """)