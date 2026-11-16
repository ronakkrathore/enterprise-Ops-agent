
from sqlalchemy.engine import Engine

from shared.database.adapters import duckdb_metadata

def _validate_database_support(engine: Engine) -> None:
    database_type = engine.dialect.name

    if database_type != "duckdb":
        raise NotImplementedError(
            f"Database support is not yet implemented for: {database_type}"
        )


def _validate_table_exists(
    engine: Engine,
    table_name: str,
    schema_name: str = "main"
) -> None:
    """
    Validate that a table or view exists in the specified schema.
    """

    objects = get_table_names(engine)

    exists = any(
        obj["name"] == table_name
        and obj["schema"] == schema_name
        for obj in objects
    )

    if not exists:
        raise ValueError(
            f"Table or view '{schema_name}.{table_name}' does not exist."
        )



def get_table_names(engine: Engine) -> list[dict[str, str]]:
    """
    Retrieve tables and views with their metadata
    using the appropriate database adapter.

    Returns:
        A list of dictionaries containing:
        - database
        - schema
        - name
        - object_type (BASE TABLE or VIEW)
    """

    database_type = engine.dialect.name

    if database_type == "duckdb":
        return duckdb_metadata.get_table_names(engine)

    raise NotImplementedError(
        f"Table and view discovery is not yet supported for: {database_type}"
    )


def get_table_columns(
    engine: Engine,
    table_name: str,
    schema_name: str = "main"
) -> list[dict]:
    """
    Retrieve column metadata using the appropriate database adapter.
    """

    _validate_database_support(engine)
    _validate_table_exists(engine, table_name, schema_name)

    return duckdb_metadata.get_table_columns(
        engine,
        table_name,
        schema_name
    )


def get_primary_keys(
    engine: Engine,
    table_name: str,
    schema_name: str = "main"
) -> list[str]:
    """
    Retrieve primary keys using the appropriate database adapter.
    """

    _validate_database_support(engine)
    _validate_table_exists(engine, table_name, schema_name)

    return duckdb_metadata.get_primary_keys(
        engine,
        table_name,
        schema_name
    )


def get_foreign_keys(
    engine: Engine,
    table_name: str,
    schema_name: str = "main"
) -> list[dict]:
    """
    Retrieve foreign keys using the appropriate database adapter.
    """

    _validate_database_support(engine)
    _validate_table_exists(engine, table_name, schema_name)

    return duckdb_metadata.get_foreign_keys(
        engine,
        table_name,
        schema_name
    )