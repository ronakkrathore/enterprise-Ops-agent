import duckdb


def create_fact_orders(
    connection: duckdb.DuckDBPyConnection
) -> None:
    """
    Create the order fact table.

    Grain:
        One row per order.
    """

    connection.execute("""
        CREATE OR REPLACE TABLE curated.fact_orders AS
        SELECT
            order_id,
            user_id,
            status AS order_status,
            gender,
            created_at AS order_created_at,
            shipped_at,
            delivered_at,
            returned_at,
            num_of_item
        FROM raw.orders
    """)

def create_fact_order_items(
    connection: duckdb.DuckDBPyConnection
) -> None:
    """
    Create the order-item fact table.

    Grain:
        One row per order item.
    """

    connection.execute("""
        CREATE OR REPLACE TABLE curated.fact_order_items AS
        SELECT
            id AS order_item_id,
            order_id,
            user_id,
            product_id,
            inventory_item_id,
            status AS item_status,
            created_at AS item_created_at,
            shipped_at,
            delivered_at,
            returned_at,
            sale_price
        FROM raw.order_items
    """)