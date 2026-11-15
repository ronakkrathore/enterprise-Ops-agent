
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_database_engine(
    database_url: str,
    echo: bool = False
) -> Engine:
    """
    Create and return a SQLAlchemy database engine.

    Args:
        database_url: Database connection URL.
        echo: Whether to log generated SQL statements.

    Returns:
        SQLAlchemy Engine instance.
    """

    engine = create_engine(
        database_url,
        echo=echo
    )

    return engine

