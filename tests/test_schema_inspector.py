import pytest

from sqlalchemy import text

from shared.database.connection import get_database_engine
from shared.database.schema_inspector import (
    get_table_names,
    get_table_columns,
    get_primary_keys,
    get_foreign_keys
)


@pytest.fixture
def test_engine(tmp_path):
    """
    Create an isolated DuckDB database for testing.
    """

    database_path = tmp_path / "test_schema.duckdb"

    database_url = f"duckdb:///{database_path}"

    engine = get_database_engine(database_url)

    with engine.begin() as connection:

        connection.execute(text("""
            CREATE SCHEMA sales
        """))

        connection.execute(text("""
            CREATE TABLE customers (
                customer_id INTEGER PRIMARY KEY,
                customer_name VARCHAR,
                email VARCHAR
            )
        """))

        connection.execute(text("""
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                order_amount DECIMAL(10, 2),
                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id)
            )
        """))

        connection.execute(text("""
            CREATE TABLE sales.order_items (
                order_id INTEGER,
                item_id INTEGER,
                product_name VARCHAR,
                PRIMARY KEY (order_id, item_id)
            )
        """))

        connection.execute(text("""
            CREATE TABLE sales.customers (
                customer_ref INTEGER PRIMARY KEY,
                company_name VARCHAR,
                region VARCHAR
            )
        """))

        connection.execute(text("""
            CREATE TABLE sales.shipments (
                shipment_id INTEGER PRIMARY KEY,
                order_id INTEGER,
                item_id INTEGER,
                FOREIGN KEY (order_id, item_id)
                    REFERENCES sales.order_items(order_id, item_id)
            )
        """))

        connection.execute(text("""
            CREATE VIEW sales.customer_directory AS
            SELECT customer_id, customer_name, email
            FROM main.customers
        """))

    yield engine

    engine.dispose()


def test_get_table_names_discovers_tables_and_views(test_engine):

    tables = get_table_names(test_engine)

    discovered_objects = {
        (table["schema"], table["name"]): table["object_type"]
        for table in tables
    }

    assert ("main", "customers") in discovered_objects
    assert ("main", "orders") in discovered_objects
    assert ("sales", "order_items") in discovered_objects
    assert ("sales", "shipments") in discovered_objects
    assert ("sales", "customer_directory") in discovered_objects

    assert discovered_objects[
        ("sales", "customer_directory")
    ] == "VIEW"

    assert discovered_objects[
        ("main", "customers")
    ] == "BASE TABLE"



def test_get_table_columns(test_engine):

    columns = get_table_columns(
        test_engine,
        table_name="customers",
        schema_name="main"
    )

    column_metadata = {
        column["name"]: column
        for column in columns
    }

    assert len(columns) == 3

    assert "customer_id" in column_metadata
    assert "customer_name" in column_metadata
    assert "email" in column_metadata

    assert column_metadata["customer_id"]["type"] == "INTEGER"
    assert column_metadata["customer_name"]["type"] == "VARCHAR"

    assert column_metadata["customer_id"]["nullable"] is False
    assert column_metadata["customer_name"]["nullable"] is True



def test_get_primary_keys(test_engine):

    primary_keys = get_primary_keys(
        test_engine,
        table_name="customers",
        schema_name="main"
    )

    assert primary_keys == ["customer_id"]


def test_get_composite_primary_keys(test_engine):

    primary_keys = get_primary_keys(
        test_engine,
        table_name="order_items",
        schema_name="sales"
    )

    assert primary_keys == ["order_id", "item_id"]


def test_get_foreign_keys(test_engine):

    foreign_keys = get_foreign_keys(
        test_engine,
        table_name="orders",
        schema_name="main"
    )

    assert len(foreign_keys) == 1

    foreign_key = foreign_keys[0]

    assert foreign_key["columns"] == ["customer_id"]
    assert foreign_key["referenced_schema"] == "main"
    assert foreign_key["referenced_table"] == "customers"
    assert foreign_key["referenced_columns"] == ["customer_id"]


def test_get_composite_foreign_keys(test_engine):

    foreign_keys = get_foreign_keys(
        test_engine,
        table_name="shipments",
        schema_name="sales"
    )

    assert len(foreign_keys) == 1

    foreign_key = foreign_keys[0]

    assert foreign_key["columns"] == ["order_id", "item_id"]
    assert foreign_key["referenced_schema"] == "sales"
    assert foreign_key["referenced_table"] == "order_items"
    assert foreign_key["referenced_columns"] == ["order_id", "item_id"]


def test_duplicate_table_names_across_schemas(test_engine):

    tables = get_table_names(test_engine)

    customers_tables = [
        table
        for table in tables
        if table["name"] == "customers"
    ]

    assert len(customers_tables) == 2

    discovered_schemas = {
        table["schema"]
        for table in customers_tables
    }

    assert discovered_schemas == {"main", "sales"}


def test_get_view_metadata(test_engine):

    columns = get_table_columns(
        test_engine,
        table_name="customer_directory",
        schema_name="sales"
    )

    column_names = [
        column["name"]
        for column in columns
    ]

    assert column_names == [
        "customer_id",
        "customer_name",
        "email"
    ]

    primary_keys = get_primary_keys(
        test_engine,
        table_name="customer_directory",
        schema_name="sales"
    )

    foreign_keys = get_foreign_keys(
        test_engine,
        table_name="customer_directory",
        schema_name="sales"
    )

    assert primary_keys == []
    assert foreign_keys == []


def test_get_table_columns_raises_for_nonexistent_table(test_engine):
    with pytest.raises(ValueError, match="does not exist"):
        get_table_columns(
            test_engine,
            "nonexistent_table"
        )


def test_get_primary_keys_raises_for_nonexistent_table(test_engine):
    with pytest.raises(ValueError, match="does not exist"):
        get_primary_keys(
            test_engine,
            "nonexistent_table"
        )


def test_get_foreign_keys_raises_for_nonexistent_table(test_engine):
    with pytest.raises(ValueError, match="does not exist"):
        get_foreign_keys(
            test_engine,
            "nonexistent_table"
        )


def test_table_validation_uses_schema_name(test_engine):
    # The main schema has customer_id as its primary key.
    main_pks = get_primary_keys(
        test_engine,
        "customers",
        schema_name="main"
    )

    # The sales schema has customer_ref as its primary key.
    sales_pks = get_primary_keys(
        test_engine,
        "customers",
        schema_name="sales"
    )

    assert main_pks == ["customer_id"]
    assert sales_pks == ["customer_ref"]

def test_unsupported_database_raises_error():
    class FakeDialect:
        name = "unsupported_db"

    class FakeEngine:
        dialect = FakeDialect()

    with pytest.raises(
        NotImplementedError,
        match="Database support is not yet implemented"
    ):
        get_table_columns(
            FakeEngine(),
            "customers"
        )