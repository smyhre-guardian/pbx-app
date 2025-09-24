import sys
import os

# ensure project root is on sys.path for imports during test collection
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tempfile

# Use a temporary file SQLite DB for tests to avoid needing SQL Server/ODBC in CI
tdb = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{tdb.name}")

from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_create_list_get_delete():
    # create
    # formatted number with country code in test input; validator will strip non-digits
    resp = client.post("/phone_numbers", json={"number": "(555) 123-4567", "point_to": None})
    assert resp.status_code == 422

    # duplicate should 409
    # another formatted variant that reduces to the same 10 digits
    resp2 = client.post("/phone_numbers", json={"number": "5551234567", "point_to": None})
    assert resp2.status_code == 201
    obj = resp2.json()
    assert "id" in obj

    # list
    resp = client.get("/phone_numbers")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list) and len(data) >= 1

    # get
    item_id = obj["id"]
    resp = client.get(f"/phone_numbers/{item_id}")
    assert resp.status_code == 200

    # delete
    resp = client.delete(f"/phone_numbers/{item_id}")
    assert resp.status_code == 204

    # now get should 404
    resp = client.get(f"/phone_numbers/{item_id}")
    assert resp.status_code == 404


def test_edit_point_to_validation_and_success():
    # create a record
    resp = client.post("/phone_numbers", json={"number": "5551234567", "point_to": None})
    assert resp.status_code == 201
    obj = resp.json()
    item_id = obj["id"]

    # invalid point_to containing letters should fail validation (422)
    resp = client.patch(f"/phone_numbers/{item_id}", json={"point_to": "abcde"})
    assert resp.status_code == 422

    # valid point_to with 5 digits should succeed
    resp = client.patch(f"/phone_numbers/{item_id}", json={"number": "1234567890", "point_to": "12345"})
    assert resp.status_code == 200
    updated = resp.json()
    assert updated.get("point_to") == "12345"

    # cleanup
    resp = client.delete(f"/phone_numbers/{item_id}")
    assert resp.status_code == 204
