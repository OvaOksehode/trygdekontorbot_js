import random
import pytest
from faker import Faker
import uuid

fake = Faker()

@pytest.fixture
def company_payload():
    """Generate random company creation payload."""
    return {
        "name": fake.company(),
        "ownerId": random.randint(1, 1000)
    }

def test_create_company(client, company_payload):
    res = client.post("/api/company", json=company_payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == company_payload["name"]
    assert "externalId" in data

def test_create_company_missing_fields(client):
    """Creating with missing required fields should fail."""
    res = client.post("/api/company", json={"owner": 123})
    assert res.status_code == 400

    errors = res.get_json()
    assert isinstance(errors, list)
    # Assert that at least one error is about "name"
    assert any("name" in err["loc"] for err in errors)
    assert any("required" in err["msg"].lower() for err in errors)

def test_create_company_duplicate_name(client, company_payload):
    """Creating two companies with the same name should fail."""
    # Create first company
    res1 = client.post("/api/company", json=company_payload)
    assert res1.status_code == 201

    # Use the same name but a different owner
    duplicate_payload = {
        "name": company_payload["name"],
        "owner": company_payload["owner"] + 1  # ensure different owner
    }

    # Try creating another with the same name
    res2 = client.post("/api/company", json=duplicate_payload)
    assert res2.status_code == 409
    assert "already exists" in res2.get_json()["error"].lower()


def test_get_company(client, company_payload):
    # Create first
    res_create = client.post("api/company", json=company_payload)
    company = res_create.get_json()
    guid = company["external_id"]

    # GET
    res = client.get(f"api/company/{guid}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == company_payload["name"]
    assert data["external_id"] == guid

@pytest.mark.parametrize("method", ["get", "delete"])
@pytest.mark.parametrize("guid, expected_status", [
    ("not-a-uuid", 400),
    ("12345", 400),
    ("!!!", 400),
])
def test_invalid_uuid_rejected(client, method, guid, expected_status):
    http_call = getattr(client, method)
    res = http_call(f"/api/company/{guid}")
    assert res.status_code == expected_status
    assert "invalid" in res.get_json()["error"].lower()

def test_update_company(client, company_payload):
    # Create first
    res_create = client.post("api/company", json=company_payload)
    company = res_create.get_json()
    guid = company["external_id"]

    # PATCH
    update_data = {"name": fake.company()}
    res = client.patch(f"api/company/{guid}", json=update_data)
    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == update_data["name"]
    assert data["external_id"] == guid

def test_update_company_invalid_field(client, company_payload):
    """Trying to update a forbidden field like balance should fail."""
    res_create = client.post("/api/company", json=company_payload)
    guid = res_create.get_json()["external_id"]

    res = client.patch(f"/api/company/{guid}", json={"balance": 999999})
    assert res.status_code == 400
    errors = res.get_json()   # FIXED

    assert any("balance" in err["loc"] for err in errors)
    assert any("not permitted" in err["msg"].lower() for err in errors)


def test_update_nonexistent_company(client):
    """Updating a company that doesn't exist should return 404."""
    random_guid = str(uuid.uuid4())
    res = client.patch(f"/api/company/{random_guid}", json={"name": "Ghost Corp"})
    assert res.status_code == 404

def test_delete_company(client, company_payload):
    # Create first
    res_create = client.post("api/company", json=company_payload)
    company = res_create.get_json()
    guid = company["external_id"]

    # DELETE
    res = client.delete(f"api/company/{guid}")
    assert res.status_code == 204

    # Verify deletion
    res = client.get(f"api/company/{guid}")
    assert res.status_code == 404

def test_delete_nonexistent_company(client):
    """Deleting a non-existent company should return 404."""
    random_guid = str(uuid.uuid4())
    res = client.delete(f"/api/company/{random_guid}")
    assert res.status_code == 404

def test_company_lifecycle(client):
    """End-to-end flow: create → update → get → delete"""
    payload = {
        "name": fake.company(),
        "owner": random.randint(1, 1000)
    }

    # CREATE
    res_create = client.post("api/company", json=payload)
    assert res_create.status_code == 201
    company = res_create.get_json()
    guid = company["external_id"]

    # UPDATE
    update_data = {"name": fake.company()}
    res_update = client.patch(f"api/company/{guid}", json=update_data)
    assert res_update.status_code == 200
    assert res_update.get_json()["name"] == update_data["name"]

    # GET
    res_get = client.get(f"api/company/{guid}")
    assert res_get.status_code == 200
    assert res_get.get_json()["name"] == update_data["name"]

    # DELETE
    res_delete = client.delete(f"api/company/{guid}")
    assert res_delete.status_code == 204

    # Confirm deletion
    res_get_deleted = client.get(f"api/company/{guid}")
    assert res_get_deleted.status_code == 404
