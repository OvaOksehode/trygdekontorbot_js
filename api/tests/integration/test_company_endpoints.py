import random
import pytest
from faker import Faker
from config import settings
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
    assert data["balance"] == settings.starter_cash
    
    # Check that the starter cash transaction exists
    

def test_create_company_missing_fields(client):
    """Creating with missing required fields should fail."""
    res = client.post("/api/company", json={"owner": 123})
    assert res.status_code == 400

    fullRes = res.get_json()
    errors = fullRes["details"]
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
        "ownerId": company_payload["ownerId"] + 1  # ensure different owner
    }

    # Try creating another with the same name
    res2 = client.post("/api/company", json=duplicate_payload)
    assert res2.status_code == 409
    assert "already exists" in res2.get_json()["errorDescription"].lower()


def test_get_company(client, company_payload):
    # Create first
    res_create = client.post("api/company", json=company_payload)
    company = res_create.get_json()
    guid = company["externalId"]

    # GET
    res = client.get(f"api/company/{guid}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == company_payload["name"]
    assert data["externalId"] == guid

def test_query_companies_with_search_param(client, company_payload):
    import uuid

    # Generate a random base name to avoid collisions
    base_name = f"AwesomeCo-{uuid.uuid4().hex[:8]}"

    # Create 5 predictable companies
    for i in range(5):
        payload = {
            "ownerId": company_payload["ownerId"] + i,
            "name": f"{base_name} {i}"
        }
        res = client.post("/api/company", json=payload)
        assert res.status_code == 201

    # Create 3 random companies
    for i in range(3):
        payload = {
            "ownerId": company_payload["ownerId"] + 100 + i,
            "name": f"{uuid.uuid4().hex[:10]}"
        }
        res = client.post("/api/company", json=payload)
        assert res.status_code == 201

    # 1️⃣ Search with %
    res_search = client.get(f"/api/company?s={base_name}%")
    assert res_search.status_code == 200
    search_results = res_search.get_json()
    assert len(search_results) == 5
    result_names = [c["name"] for c in search_results]
    for i in range(5):
        assert f"{base_name} {i}" in result_names

    # 2️⃣ Single-character wildcard: match only single-digit numbers
    # We need to account for space + number: "AwesomeCo-XXXX ?" matches "AwesomeCo-XXXX 0..4"
    search_param = f"{base_name} ?"
    res_search = client.get(f"/api/company?s={search_param}")
    assert res_search.status_code == 200
    search_results = res_search.get_json()
    expected_names = [f"{base_name} {i}" for i in range(5) if len(str(i)) == 1]
    result_names = [c["name"] for c in search_results]
    for name in expected_names:
        assert name in result_names

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
    guid = company["externalId"]

    # PATCH
    update_data = {"name": fake.company()}
    res = client.patch(f"api/company/{guid}", json=update_data)
    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == update_data["name"]
    assert data["externalId"] == guid

def test_update_company_invalid_field(client, company_payload):
    """Trying to update a forbidden field like balance should fail."""
    res_create = client.post("/api/company", json=company_payload)
    guid = res_create.get_json()["externalId"]

    res = client.patch(f"/api/company/{guid}", json={"balance": 999999})
    assert res.status_code == 400
    body = res.get_json()   # FIXED
    errors = body["details"]
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
    guid = company["externalId"]

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
        "ownerId": random.randint(1, 1000)
    }

    # CREATE
    res_create = client.post("api/company", json=payload)
    assert res_create.status_code == 201
    company = res_create.get_json()
    guid = company["externalId"]

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

def test_claim_cash_success(client, company_payload):
    """
    ✅ GIVEN an existing company
    WHEN calling POST /api/company/<guid>/claim
    THEN it should create a new check transaction and update balance
    """
    # Create the company first via API
    res_create = client.post("/api/company", json=company_payload)
    assert res_create.status_code == 201
    company = res_create.get_json()
    external_guid = company["externalId"]

    # Get current balance
    before = client.get(f"/api/company/{external_guid}")
    assert before.status_code == 200
    before_balance = before.get_json()["balance"]

    # Claim cash
    res_claim = client.post(f"/api/company/{external_guid}/claim")
    assert res_claim.status_code == 201

    claim_data = res_claim.get_json()
    assert "amount" in claim_data
    assert "receiverCompanyExternalId" in claim_data
    assert claim_data["receiverCompanyExternalId"] == external_guid

    # Verify balance was updated
    after = client.get(f"/api/company/{external_guid}")
    assert after.status_code == 200
    after_balance = after.get_json()["balance"]

    assert after_balance == before_balance + claim_data["amount"]
