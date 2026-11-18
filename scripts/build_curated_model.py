from pathlib import Path

from analyst_agent.database.transformations.build import (
    build_curated_model,
)
from shared.database.connection import get_database_engine


DATABASE_PATH = Path("data/database/analytics.duckdb")


def main():
    database_url = f"duckdb:///{DATABASE_PATH}"

    engine = get_database_engine(database_url)

    try:
        with engine.connect() as connection:
            raw_connection = connection.connection.driver_connection

            build_curated_model(raw_connection)

        print("Curated analytical model built successfully.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()