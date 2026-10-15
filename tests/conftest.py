import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def ride_streams():
    with open(FIXTURES / "ride_streams.json", encoding="utf-8") as f:
        return json.load(f)
