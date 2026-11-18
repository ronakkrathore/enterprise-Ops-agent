import duckdb

from analyst_agent.database.transformations.build import (
    build_curated_model,
)


def test_build_curated_model():
    connection = duckdb.connect(":memory:")

    try:
        connection.execute("CREATE SCHEMA raw")

        connection.execute("""
            CREATE TABLE raw.users (
                id BIGINT,
                first_name VARCHAR,
                last_name VARCHAR,
                email VARCHAR,
                age BIGINT,
                gender VARCHAR,
                city VARCHAR,
                state VARCHAR,
                country VARCHAR,
                postal_code VARCHAR,
                traffic_source VARCHAR,
                created_at TIMESTAMP
            )
        """)

        connection.execute("""
            INSERT INTO raw.users VALUES
            (1, 'Aarav', 'Sharma', 'aarav@example.com',
             25, 'M', 'Jaipur', 'Rajasthan', 'India',
             '302001', 'Search', TIMESTAMP '2025-01-01')
        """)

        connection.execute("""
            CREATE TABLE raw.products (
                id BIGINT,
                name VARCHAR,
                brand VARCHAR,
                category VARCHAR,
                department VARCHAR,
                sku VARCHAR,
                cost DOUBLE,
                retail_price DOUBLE,
                distribution_center_id BIGINT
            )
        """)

        connection.execute("""
            INSERT INTO raw.products VALUES
            (501, 'Laptop', 'Brand A', 'Electronics',
             'Technology', 'SKU501', 500.0, 750.0, 1)
        """)

        connection.execute("""
            CREATE TABLE raw.distribution_centers (
                id BIGINT,
                name VARCHAR,
                latitude DOUBLE,
                longitude DOUBLE
            )
        """)

        connection.execute("""
            INSERT INTO raw.distribution_centers VALUES
            (1, 'Jaipur Center', 26.9124, 75.7873)
        """)

        connection.execute("""
            CREATE TABLE raw.orders (
                order_id BIGINT,
                user_id BIGINT,
                status VARCHAR,
                gender VARCHAR,
                created_at TIMESTAMP,
                shipped_at TIMESTAMP,
                delivered_at TIMESTAMP,
                returned_at TIMESTAMP,
                num_of_item BIGINT
            )
        """)

        connection.execute("""
            INSERT INTO raw.orders VALUES
            (101, 1, 'Complete', 'M',
             TIMESTAMP '2025-01-01',
             TIMESTAMP '2025-01-02',
             TIMESTAMP '2025-01-03',
             NULL, 1)
        """)

        connection.execute("""
            CREATE TABLE raw.order_items (
                id BIGINT,
                order_id BIGINT,
                user_id BIGINT,
                product_id BIGINT,
                inventory_item_id BIGINT,
                status VARCHAR,
                created_at TIMESTAMP,
                shipped_at TIMESTAMP,
                delivered_at TIMESTAMP,
                returned_at TIMESTAMP,
                sale_price DOUBLE
            )
        """)

        connection.execute("""
            INSERT INTO raw.order_items VALUES
            (1001, 101, 1, 501, 2001, 'Complete',
             TIMESTAMP '2025-01-01',
             TIMESTAMP '2025-01-02',
             TIMESTAMP '2025-01-03',
             NULL, 750.0)
        """)

        # Build all curated tables.
        build_curated_model(connection)

        expected_tables = {
            "dim_customers",
            "dim_products",
            "dim_distribution_centers",
            "fact_orders",
            "fact_order_items",
        }

        actual_tables = {
            row[0]
            for row in connection.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'curated'
            """).fetchall()
        }

        assert actual_tables == expected_tables

        # Verify that all five tables contain the expected record.
        for table_name in expected_tables:
            count = connection.execute(
                f"SELECT COUNT(*) FROM curated.{table_name}"
            ).fetchone()[0]

            assert count == 1, f"{table_name} has an unexpected row count"

    finally:
        connection.close()

def test_build_curated_model_rolls_back_on_failure():
    connection = duckdb.connect(":memory:")

    try:
        connection.execute("CREATE SCHEMA raw")
        connection.execute("CREATE SCHEMA curated")

        # Existing curated table with a known value.
        connection.execute("""
            CREATE TABLE curated.dim_customers (
                user_id BIGINT
            )
        """)

        connection.execute("""
            INSERT INTO curated.dim_customers VALUES (999)
        """)

        # Deliberately create incomplete source tables.
        # The first transformation will fail because raw.users is missing.
        connection.execute("""
            CREATE TABLE raw.products (
                id BIGINT
            )
        """)

        try:
            build_curated_model(connection)
            assert False, "Expected the transformation to fail"
        except Exception:
            pass

        # Verify that the original curated table remains unchanged.
        result = connection.execute("""
            SELECT user_id
            FROM curated.dim_customers
        """).fetchone()

        assert result == (999,)

    finally:
        connection.close()