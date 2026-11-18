import duckdb

from analyst_agent.database.transformations.dimensions import (
    create_dim_customers,
    create_dim_products,
    create_dim_distribution_centers,
)

def test_create_dim_customers():
    connection = duckdb.connect(":memory:")

    try:
        connection.execute("CREATE SCHEMA raw")
        connection.execute("CREATE SCHEMA curated")

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
             25, 'M', 'Jaipur', 'Rajasthan', '302001',
             'India', 'Search', TIMESTAMP '2025-01-01 10:00:00'),

            (2, 'Meera', 'Singh', 'meera@example.com',
             27, 'F', 'Delhi', 'Delhi', '110001',
             'India', 'Organic', TIMESTAMP '2025-02-01 10:00:00')
        """)

        create_dim_customers(connection)

        result = connection.execute("""
            SELECT COUNT(*) FROM curated.dim_customers
        """).fetchone()[0]

        assert result == 2

        customer = connection.execute("""
            SELECT user_id, first_name, city
            FROM curated.dim_customers
            WHERE user_id = 1
        """).fetchone()

        assert customer == (1, "Aarav", "Jaipur")

        # Verify that all source records are preserved.
        source_count = connection.execute(
            "SELECT COUNT(*) FROM raw.users"
        ).fetchone()[0]

        target_count = connection.execute(
            "SELECT COUNT(*) FROM curated.dim_customers"
        ).fetchone()[0]

        assert source_count == target_count

        # Verify that customer IDs remain unique.
        unique_count = connection.execute(
            "SELECT COUNT(DISTINCT user_id) FROM curated.dim_customers"
        ).fetchone()[0]

        assert target_count == unique_count

    finally:
        connection.close()

def test_create_dim_products():
    connection = duckdb.connect(":memory:")

    try:
        connection.execute("CREATE SCHEMA raw")
        connection.execute("CREATE SCHEMA curated")

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
            (1, 'Laptop', 'Brand A', 'Electronics',
             'Technology', 'SKU001', 500.0, 800.0, 1),

            (2, NULL, NULL, 'Electronics',
             'Technology', 'SKU002', 300.0, 500.0, 1)
        """)

        create_dim_products(connection)

        # Verify record count.
        assert connection.execute(
            "SELECT COUNT(*) FROM curated.dim_products"
        ).fetchone()[0] == 2

        # Verify product attributes.
        product = connection.execute("""
            SELECT product_id, product_name, brand, retail_price
            FROM curated.dim_products
            WHERE product_id = 1
        """).fetchone()

        assert product == (1, "Laptop", "Brand A", 800.0)

        # Verify NULL values are preserved.
        missing_product = connection.execute("""
            SELECT product_name, brand
            FROM curated.dim_products
            WHERE product_id = 2
        """).fetchone()

        assert missing_product == (None, None)

        # Verify product IDs are unique.
        assert connection.execute("""
            SELECT COUNT(DISTINCT product_id)
            FROM curated.dim_products
        """).fetchone()[0] == 2

    finally:
        connection.close()

def test_create_dim_distribution_centers():
    connection = duckdb.connect(":memory:")

    try:
        connection.execute("CREATE SCHEMA raw")
        connection.execute("CREATE SCHEMA curated")

        connection.execute("""
            CREATE TABLE raw.distribution_centers (
                id BIGINT,
                name VARCHAR,
                latitude DOUBLE,
                longitude DOUBLE,
                distribution_center_geom VARCHAR
            )
        """)

        connection.execute("""
            INSERT INTO raw.distribution_centers VALUES
            (1, 'Center A', 26.9124, 75.7873, 'POINT(75.7873 26.9124)'),
            (2, 'Center B', 28.6139, 77.2090, 'POINT(77.2090 28.6139)')
        """)

        create_dim_distribution_centers(connection)

        # Verify record count.
        assert connection.execute("""
            SELECT COUNT(*) FROM curated.dim_distribution_centers
        """).fetchone()[0] == 2

        # Verify center attributes.
        center = connection.execute("""
            SELECT distribution_center_id,
                   distribution_center_name,
                   latitude,
                   longitude
            FROM curated.dim_distribution_centers
            WHERE distribution_center_id = 1
        """).fetchone()

        assert center == (1, "Center A", 26.9124, 75.7873)

        # Verify IDs are unique.
        assert connection.execute("""
            SELECT COUNT(DISTINCT distribution_center_id)
            FROM curated.dim_distribution_centers
        """).fetchone()[0] == 2

        # Verify geometry is excluded.
        columns = connection.execute("""
            DESCRIBE curated.dim_distribution_centers
        """).fetchall()

        column_names = [column[0] for column in columns]

        assert "distribution_center_geom" not in column_names

    finally:
        connection.close()