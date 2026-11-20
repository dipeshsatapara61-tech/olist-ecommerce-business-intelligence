
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

PROJECT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_DIR / ".env")

# Database credentials
connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME")
)

engine = create_engine(connection_url)

try:
    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        print("POSTGRESQL CONNECTION SUCCESSFUL")

        print(result.scalar())

        print("\nDatabase:", os.getenv("DB_NAME"))

except Exception as error:
    print("CONNECTION FAILED")
    print(error)

finally:
    engine.dispose()
