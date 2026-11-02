import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fake_firestore import FakeClient, fs  # noqa: E402
from core.repository import EcoRepository  # noqa: E402


@pytest.fixture
def client():
    return FakeClient()


@pytest.fixture
def repo(client):
    return EcoRepository(client, fs)
