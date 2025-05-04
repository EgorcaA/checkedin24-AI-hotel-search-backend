import sys
from pathlib import Path

import pytest

# Add the backend directory to the Python path
backend_dir = str(Path(__file__).parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
