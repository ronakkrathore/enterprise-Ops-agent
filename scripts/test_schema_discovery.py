
from sqlalchemy import text

from shared.database.connection import get_database_engine
from shared.database.schema_inspector import (
    get_table_names,
    get_table_columns,
    get_primary_keys,
    get_foreign_keys
)

DATABASE_URL = "duckdb:///data/database/schema_test.duckdb"

engine = get_database_engine(DATABASE_URL)

# Create test schemas and tables
with engine.begin() as connection:

    connection.execute(text("""
        CREATE SCHEMA IF NOT EXISTS sales
    """))

    # Main schema tables
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name VARCHAR,
            email VARCHAR,
            city VARCHAR
        )
    """))

    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_amount DECIMAL(10, 2),
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
    """))

    # Sales schema: duplicate table name
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS sales.customers (
            customer_ref INTEGER PRIMARY KEY,
            company_name VARCHAR,
            region VARCHAR
        )
    """))

    # Sales schema: composite primary key
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS sales.order_items (
            order_id INTEGER,
            item_id INTEGER,
            product_name VARCHAR,
            PRIMARY KEY (order_id, item_id)
        )
    """))

    # Sales schema: composite foreign key
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS sales.shipments (
            shipment_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            item_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (order_id, item_id)
                REFERENCES sales.order_items(order_id, item_id)
        )
    """))




# Discover tables
tables = get_table_names(engine)

print("\n========== DISCOVERED TABLES ==========")

for table in tables:
    print(
        f"Database: {table['database']} | "
        f"Schema: {table['schema']} | "
        f"Table: {table['name']}"
    )


# Discover columns, primary keys and foreign keys
for table in tables:

    table_name = table["name"]
    schema_name = table["schema"]

    print(f"\n========== {schema_name}.{table_name} ==========")

    # Discover columns
    columns = get_table_columns(
        engine,
        table_name,
        schema_name
    )

    print("\nColumns:")
    for column in columns:
        print(column)

    # Discover primary keys
    primary_keys = get_primary_keys(
        engine,
        table_name,
        schema_name
    )

    print("\nPrimary keys:", primary_keys)

    # Discover foreign keys
    foreign_keys = get_foreign_keys(
        engine,
        table_name,
        schema_name
    )

    print("\nForeign keys:", foreign_keys)


# Close database engine
engine.dispose()

print("\n========== SCHEMA DISCOVERY TEST COMPLETED ==========")
