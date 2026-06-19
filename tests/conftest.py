import os
from pathlib import Path

import pytest

TEST_DATABASE_PATH = Path(__file__).with_name("rice_duck_test.db")
os.environ["DATABASE_PATH"] = str(TEST_DATABASE_PATH)
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["PASSWORD_HASH_ITERATIONS"] = "1000"

from app.core.database import get_connection, initialize_database


@pytest.fixture(autouse=True)
def clean_database() -> None:
    initialize_database()
    with get_connection() as connection:
        connection.execute("DELETE FROM dss_simulation_histories")
        connection.execute("DELETE FROM users")
    yield
    with get_connection() as connection:
        connection.execute("DELETE FROM dss_simulation_histories")
        connection.execute("DELETE FROM users")
