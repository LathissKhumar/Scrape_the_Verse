"""Test configuration and fixtures."""
import os
import sys
import tempfile
import pytest

# Ensure app package is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = os.path.dirname(current_dir)
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

from app.persistence.database import Database
from app.persistence.repository import Repository


@pytest.fixture
def temp_db():
    """Provides a fresh isolated temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = f.name

    test_db = Database(temp_path)
    test_db.init_db_sync()

    test_repo = Repository(test_db)

    yield test_db, test_repo

    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except Exception:
            pass
