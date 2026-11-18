import duckdb

from analyst_agent.database.transformations.dimensions import (
    create_dim_customers,
    create_dim_products,
    create_dim_distribution_centers,
)

from analyst_agent.database.transformations.facts import (
    create_fact_orders,
    create_fact_order_items,
)


def build_curated_model(
    connection: duckdb.DuckDBPyConnection
) -> None:
    """
    Build all curated analytical tables atomically.

    If any transformation fails, all changes are rolled back.
    """

    connection.execute("BEGIN TRANSACTION")

    try:
        connection.execute("CREATE SCHEMA IF NOT EXISTS curated")

        create_dim_customers(connection)
        create_dim_products(connection)
        create_dim_distribution_centers(connection)

        create_fact_orders(connection)
        create_fact_order_items(connection)

        connection.execute("COMMIT")

    except Exception:
        connection.execute("ROLLBACK")
        raise