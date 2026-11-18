import duckdb

from analyst_agent.database.transformations.facts import (
    create_fact_orders,
    create_fact_order_items,
)

def test_create_fact_orders():
    connection = duckdb.connect(":memory:")

    try:
        connection.execute("CREATE SCHEMA raw")
        connection.execute("CREATE SCHEMA curated")

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
             TIMESTAMP '2025-01-01 10:00:00',
             TIMESTAMP '2025-01-02 10:00:00',
             TIMESTAMP '2025-01-03 10:00:00',
             NULL, 2),

            (102, 2, 'Returned', 'F',
             TIMESTAMP '2025-02-01 10:00:00',
             TIMESTAMP '2025-02-02 10:00:00',
             TIMESTAMP '2025-02-03 10:00:00',
             TIMESTAMP '2025-02-04 10:00:00', 1)
        """)

        create_fact_orders(connection)

        # Verify record count.
        assert connection.execute("""
            SELECT COUNT(*) FROM curated.fact_orders
        """).fetchone()[0] == 2

        # Verify order-level attributes.
        order = connection.execute("""
            SELECT order_id, user_id, order_status, num_of_item
            FROM curated.fact_orders
            WHERE order_id = 101
        """).fetchone()

        assert order == (101, 1, "Complete", 2)

        # Verify NULL timestamps are preserved.
        returned_at = connection.execute("""
            SELECT returned_at
            FROM curated.fact_orders
            WHERE order_id = 101
        """).fetchone()[0]

        assert returned_at is None

        # Verify order IDs are unique.
        unique_count = connection.execute("""
            SELECT COUNT(DISTINCT order_id)
            FROM curated.fact_orders
        """).fetchone()[0]

        assert unique_count == 2

    finally:
        connection.close()



def test_create_fact_order_items():
    connection = duckdb.connect(":memory:")

    try:
        connection.execute("CREATE SCHEMA raw")
        connection.execute("CREATE SCHEMA curated")

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
            (1, 101, 1, 501, 1001, 'Complete',
             TIMESTAMP '2025-01-01 10:00:00',
             TIMESTAMP '2025-01-02 10:00:00',
             TIMESTAMP '2025-01-03 10:00:00',
             NULL, 59.99),

            (2, 102, 2, 502, 1002, 'Returned',
             TIMESTAMP '2025-02-01 10:00:00',
             TIMESTAMP '2025-02-02 10:00:00',
             TIMESTAMP '2025-02-03 10:00:00',
             TIMESTAMP '2025-02-04 10:00:00', 89.50)
        """)

        create_fact_order_items(connection)

        # Verify row count.
        assert connection.execute("""
            SELECT COUNT(*) FROM curated.fact_order_items
        """).fetchone()[0] == 2

        # Verify item attributes and sale price.
        item = connection.execute("""
            SELECT
                order_item_id,
                order_id,
                user_id,
                product_id,
                item_status,
                sale_price
            FROM curated.fact_order_items
            WHERE order_item_id = 1
        """).fetchone()

        assert item == (1, 101, 1, 501, "Complete", 59.99)

        # Verify NULL timestamps are preserved.
        returned_at = connection.execute("""
            SELECT returned_at
            FROM curated.fact_order_items
            WHERE order_item_id = 1
        """).fetchone()[0]

        assert returned_at is None

        # Verify item IDs are unique.
        unique_count = connection.execute("""
            SELECT COUNT(DISTINCT order_item_id)
            FROM curated.fact_order_items
        """).fetchone()[0]

        assert unique_count == 2

    finally:
        connection.close()