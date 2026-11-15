
from shared.database.connection import get_database_engine
from sqlalchemy import text


DATABASE_URL = "duckdb:///data/database/analytics.duckdb"


engine = get_database_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT 1 AS test_value"))
    print("Database connection successful!")
    print("Query result:", result.scalar())

engine.dispose()
