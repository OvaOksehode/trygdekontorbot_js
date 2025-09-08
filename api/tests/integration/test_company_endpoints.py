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
        "owner": random.randint(1, 1000)
    }

def test_create_company(client, company_payload):
    res = client.post("/api/company", json=company_payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == company_payload["name"]
    assert "external_id" in data

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
