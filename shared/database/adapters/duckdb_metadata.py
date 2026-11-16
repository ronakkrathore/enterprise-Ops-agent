
from sqlalchemy import text
from sqlalchemy.engine import Engine




def get_table_names(engine: Engine) -> list[dict[str, str]]:
    """
    Retrieve tables and views along with their schema and database.
    """

    query = text("""
        SELECT
            table_catalog,
            table_schema,
            table_name,
            table_type
        FROM information_schema.tables
        WHERE table_type IN ('BASE TABLE', 'VIEW')
        ORDER BY table_schema, table_name
    """)

    with engine.connect() as connection:
        result = connection.execute(query)

        tables = result.mappings().all()

    return [
        {
            "database": table["table_catalog"],
            "schema": table["table_schema"],
            "name": table["table_name"],
            "object_type": table["table_type"]
        }
        for table in tables
    ]


def get_table_columns(
    engine: Engine,
    table_name: str,
    schema_name: str = "main"
) -> list[dict]:
    """
    Retrieve column metadata for a specific DuckDB table and schema.
    """

    query = text("""
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = :table_name
            AND table_schema = :schema_name
        ORDER BY ordinal_position
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "table_name": table_name,
                "schema_name": schema_name
            }
        )

        columns = result.mappings().all()

    column_details = []

    for column in columns:
        column_details.append({
            "name": column["column_name"],
            "type": column["data_type"],
            "nullable": column["is_nullable"] == "YES",
            "default": column["column_default"]
        })

    return column_details




def get_primary_keys(
    engine: Engine,
    table_name: str,
    schema_name: str = "main"
) -> list[str]:
    """
    Retrieve primary key column names for a specific DuckDB table and schema.
    """

    query = text("""
        SELECT
            constraint_column_names
        FROM duckdb_constraints()
        WHERE constraint_type = 'PRIMARY KEY'
            AND table_name = :table_name
            AND schema_name = :schema_name
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "table_name": table_name,
                "schema_name": schema_name
            }
        )

        constraints = result.fetchall()

    primary_keys = []

    for constraint in constraints:
        primary_keys.extend(constraint[0])

    return primary_keys






def get_foreign_keys(
    engine: Engine,
    table_name: str,
    schema_name: str = "main"
) -> list[dict]:
    """
    Retrieve foreign key relationships for a specific
    DuckDB table and schema.
    """

    query = text("""
        SELECT
            constraint_column_names,
            referenced_table,
            referenced_column_names,
            constraint_name
        FROM duckdb_constraints()
        WHERE constraint_type = 'FOREIGN KEY'
            AND table_name = :table_name
            AND schema_name = :schema_name
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "table_name": table_name,
                "schema_name": schema_name
            }
        )

        constraints = result.mappings().all()

    foreign_keys = []

    for constraint in constraints:
        foreign_keys.append({
            "columns": constraint["constraint_column_names"],
            "referenced_schema": schema_name,
            "referenced_table": constraint["referenced_table"],
            "referenced_columns": constraint["referenced_column_names"],
            "constraint_name": constraint["constraint_name"]
        })

    return foreign_keys
