import pytest
import uuid
import random
from faker import Faker

fake = Faker()


@pytest.fixture
def company(client):
    """Helper to create a company and return its payload."""
    payload = {
        "name": fake.company(),
        "owner": random.randint(1, 1000),
    }
    res = client.post("/api/company", json=payload)
    assert res.status_code == 201
    return res.get_json()


def test_create_company_transaction(client, company):
    """Happy path: create a transaction between two companies."""
    sender = company
    receiver_payload = {
        "name": fake.company(),
        "owner": random.randint(1001, 2000),
    }
    res_receiver = client.post("/api/company", json=receiver_payload)
    assert res_receiver.status_code == 201
    receiver = res_receiver.get_json()

    tx_payload = {
        "amount": 90,  # Needs to be adjusted after the starter cash has been implemented
        "receiver_id": receiver["external_id"],
        "from_company_id": sender["external_id"],
    }

    res = client.post("/api/company-transaction", json=tx_payload)
    assert res.status_code == 201
    tx = res.get_json()

    assert tx["amount"] == tx_payload["amount"]
    assert tx["receiver_id"] == receiver["external_id"]
    assert tx["from_company_id"] == sender["external_id"]


def test_create_transaction_invalid_amount(client, company):
    """Transaction with amount <= 0 should fail validation."""
    receiver_payload = {
        "name": fake.company(),
        "owner": random.randint(2001, 3000),
    }
    receiver = client.post("/api/company", json=receiver_payload).get_json()

    tx_payload = {
        "amount": 0,  # ❌ invalid
        "receiver_id": receiver["external_id"],
        "from_company_id": company["external_id"],
    }

    res = client.post("/api/company-transaction", json=tx_payload)
    assert res.status_code == 400
    errors = res.get_json()
    assert "amount" in errors["error"].lower()

def test_create_transaction_nonexistent_company(client, company):
    """Transaction with a non-existent receiver should fail."""
    fake_guid = str(uuid.uuid4())

    tx_payload = {
        "amount": 90,
        "receiver_id": fake_guid,  # ❌ not in DB
        "from_company_id": company["external_id"],
    }

    res = client.post("/api/company-transaction", json=tx_payload)
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"].lower()


def test_get_company_transaction(client, company):
    """Create a transaction, then fetch it by external_id."""
    receiver_payload = {
        "name": fake.company(),
        "owner": random.randint(3001, 4000),
    }
    receiver = client.post("/api/company", json=receiver_payload).get_json()

    tx_payload = {
        "amount": 50,   # also reliant on starter cash
        "receiver_id": receiver["external_id"],
        "from_company_id": company["external_id"],
    }

    res_create = client.post("/api/company-transaction", json=tx_payload)
    assert res_create.status_code == 201
    tx = res_create.get_json()
    tx_guid = tx["external_id"]

    res_get = client.get(f"/api/company-transaction/{tx_guid}")
    assert res_get.status_code == 201
    fetched = res_get.get_json()

    assert fetched["external_id"] == tx_guid
    assert fetched["amount"] == tx_payload["amount"]


@pytest.mark.parametrize("guid", ["not-a-uuid", "12345", "!!!"])
def test_get_transaction_invalid_uuid(client, guid):
    res = client.get(f"/api/company-transaction/{guid}")
    assert res.status_code == 400
    assert "invalid" in res.get_json()["error"].lower()


def test_get_nonexistent_transaction(client):
    fake_guid = str(uuid.uuid4())
    res = client.get(f"/api/company-transaction/{fake_guid}")
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"].lower()
