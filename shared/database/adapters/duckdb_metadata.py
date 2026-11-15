
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine




def get_table_names(engine: Engine) -> list[dict]:
    """
    Retrieve table names along with their schema and database.
    """

    query = text("""
        SELECT
            table_catalog,
            table_schema,
            table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
        ORDER BY table_schema, table_name
    """)

    with engine.connect() as connection:
        result = connection.execute(query)

        tables = result.mappings().all()

    return [
        {
            "database": table["table_catalog"],
            "schema": table["table_schema"],
            "name": table["table_name"]
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
    Retrieve foreign key relationships for a specific DuckDB table and schema.
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

            referenced_schema_query = text("""
                SELECT
                    rc.unique_constraint_schema AS referenced_schema,
                    tc.table_name AS referenced_table
                FROM information_schema.referential_constraints rc
                JOIN information_schema.table_constraints tc
                    ON rc.unique_constraint_catalog = tc.constraint_catalog
                    AND rc.unique_constraint_schema = tc.constraint_schema
                    AND rc.unique_constraint_name = tc.constraint_name
                WHERE rc.constraint_name = :constraint_name
                    AND rc.constraint_schema = :schema_name
            """)

            referenced_result = connection.execute(
                referenced_schema_query,
                {
                    "constraint_name": constraint["constraint_name"],
                    "schema_name": schema_name
                }
            )

            referenced_info = referenced_result.mappings().one()

            foreign_keys.append({
                "columns": constraint["constraint_column_names"],
                "referenced_schema": referenced_info["referenced_schema"],
                "referenced_table": referenced_info["referenced_table"],
                "referenced_columns": constraint["referenced_column_names"],
                "constraint_name": constraint["constraint_name"]
            })

    return foreign_keys
