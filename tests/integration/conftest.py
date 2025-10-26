import os
import tempfile
import contextlib
import pytest
from fastapi.testclient import TestClient

@contextlib.contextmanager
def temp_db_env():
    with tempfile.TemporaryDirectory() as d:
        db_path = os.path.join(d, "test.db")
        old = os.environ.get("DB_PATH")
        os.environ["DB_PATH"] = db_path
        try:
            yield db_path
        finally:
            if old is None:
                os.environ.pop("DB_PATH", None)
            else:
                os.environ["DB_PATH"] = old

@pytest.fixture(scope="function")
def client():
    with temp_db_env():
        # Import inside the context so app/db read the overridden DB_PATH
        from app.main import app
        from app.db import init_db
        init_db()
        with TestClient(app) as c:
            yield c
