
from sqlalchemy.engine import Engine

from shared.database.adapters import duckdb_metadata


def get_table_names(engine: Engine) -> list[dict]:
    """
    Retrieve table metadata using the appropriate database adapter.
    """

    database_type = engine.dialect.name

    if database_type == "duckdb":
        return duckdb_metadata.get_table_names(engine)

    raise NotImplementedError(
        f"Table discovery is not yet supported for: {database_type}"
    )


def get_table_columns(
    engine: Engine,
    table_name: str,
    schema_name: str = "main"
) -> list[dict]:
    """
    Retrieve column metadata using the appropriate database adapter.
    """

    database_type = engine.dialect.name

    if database_type == "duckdb":
        return duckdb_metadata.get_table_columns(
            engine,
            table_name,
            schema_name
        )

    raise NotImplementedError(
        f"Column discovery is not yet supported for: {database_type}"
    )


def get_primary_keys(
    engine: Engine,
    table_name: str,
    schema_name: str = "main"
) -> list[str]:
    """
    Retrieve primary keys using the appropriate database adapter.
    """

    database_type = engine.dialect.name

    if database_type == "duckdb":
        return duckdb_metadata.get_primary_keys(
            engine,
            table_name,
            schema_name
        )

    raise NotImplementedError(
        f"Primary key discovery is not yet supported for: {database_type}"
    )


def get_foreign_keys(
    engine: Engine,
    table_name: str,
    schema_name: str = "main"
) -> list[dict]:
    """
    Retrieve foreign keys using the appropriate database adapter.
    """

    database_type = engine.dialect.name

    if database_type == "duckdb":
        return duckdb_metadata.get_foreign_keys(
            engine,
            table_name,
            schema_name
        )

    raise NotImplementedError(
        f"Foreign key discovery is not yet supported for: {database_type}"
    )