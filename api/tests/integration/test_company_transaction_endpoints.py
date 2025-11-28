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
        "ownerId": random.randint(1, 1000),
    }
    res = client.post("/api/company", json=payload)
    assert res.status_code == 201
    return res.get_json()


def test_create_company_transaction(client, company):
    """Happy path: create a transaction between two companies."""
    sender = company
    receiver_payload = {
        "name": fake.company(),
        "ownerId": random.randint(1001, 2000),
    }
    res_receiver = client.post("/api/company", json=receiver_payload)
    assert res_receiver.status_code == 201
    receiver = res_receiver.get_json()

    tx_payload = {
        "amount": 90,  # Needs to be adjusted after the starter cash has been implemented
        "receiverCompanyId": receiver["externalId"],
        "senderCompanyId": sender["externalId"],
    }

    res = client.post("/api/company-transaction", json=tx_payload)
    assert res.status_code == 201
    tx = res.get_json()

    assert tx["amount"] == tx_payload["amount"]
    assert tx["receiverCompanyId"] == receiver["externalId"]
    assert tx["senderCompanyId"] == sender["externalId"]


def test_create_transaction_invalid_amount(client, company):
    """Transaction with amount <= 0 should fail validation."""
    receiver_payload = {
        "name": fake.company(),
        "ownerId": random.randint(1, 3000),
    }
    receiver = client.post("/api/company", json=receiver_payload).get_json()

    tx_payload = {
        "amount": 0,  # ❌ invalid
        "receiverId": receiver["externalId"],
        "fromCompanyId": company["externalId"],
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
        "receiverCompanyId": fake_guid,  # ❌ not in DB
        "senderCompanyId": company["externalId"],
    }

    res = client.post("/api/company-transaction", json=tx_payload)
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"].lower()


def test_get_company_transactions(client, company):
    """Create a company transaction and verify it is returned via ledger-entry endpoints"""

    receiver_payload = {
        "name": fake.company(),
        "ownerId": random.randint(3001, 4000),
    }
    receiver = client.post("/api/company", json=receiver_payload).get_json()

    tx_payload = {
        "amount": 50,
        "receiverCompanyId": receiver["externalId"],
        "senderCompanyId": company["externalId"],
        "type": "companyTransaction"
    }

    # ✅ Create the transaction
    res_create = client.post("/api/ledger-entry", json=tx_payload)
    assert res_create.status_code == 201
    tx = res_create.get_json()
    tx_guid = tx["externalId"]

    # ✅ Verify creation response
    assert tx["type"] == "companyTransaction"
    assert tx["amount"] == tx_payload["amount"]

    # ✅ Fetch SINGLE ledger entry by GUID
    res_get = client.get(f"/api/ledger-entry/{tx_guid}")
    assert res_get.status_code == 200

    fetched = res_get.get_json()
    assert fetched["externalId"] == tx_guid
    assert fetched["amount"] == tx_payload["amount"]
    assert fetched["type"] == "companyTransaction"

    # ✅ Fetch ALL ledger entries
    res_all = client.get("/api/ledger-entry?receiverCompanyId=" + receiver["externalId"])
    assert res_all.status_code == 200

    all_entries = res_all.get_json()
    assert isinstance(all_entries, list)

    # Make sure our created transaction exists in the results
    assert any(entry["externalId"] == tx_guid for entry in all_entries)
    """Create a company transaction and verify it is a LedgerEntry subclass."""
    receiver_payload = {
        "name": fake.company(),
        "ownerId": random.randint(3001, 4000),
    }
    receiver = client.post("/api/company", json=receiver_payload).get_json()

    tx_payload = {
        "amount": 50,
        "receiverCompanyId": receiver["externalId"],
        "senderCompanyId": company["externalId"],
    }

    # Create the transaction
    res_create = client.post("/api/company-transaction", json=tx_payload)
    assert res_create.status_code == 201
    tx = res_create.get_json()
    tx_guid = tx["externalId"]

    # It should include the LedgerEntry type info
    assert tx["type"] == "companyTransaction"
    assert tx["amount"] == tx_payload["amount"]

    # Fetch the transaction directly
    res_get = client.get(f"/api/ledger-entry/{tx_guid}")
    assert res_get.status_code == 200
    fetched = res_get.get_json()

    assert fetched["externalId"] == tx_guid
    assert fetched["amount"] == tx_payload["amount"]
    assert fetched["type"] == "companyTransaction"

    # Fetch from /ledger-entry to ensure polymorphic query works
    res_all = client.get("/api/ledger-entry")
    assert res_all.status_code == 200
    all_entries = res_all.get_json()
    assert any(entry["externalId"] == tx_guid for entry in all_entries)



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

def test_create_check_transaction_spawns_money(client, company):
    # create receiver company
    receiver_payload = {
        "name": fake.company(),
        "ownerId": random.randint(1001, 2000),
    }
    res_receiver = client.post("/api/company", json=receiver_payload)
    assert res_receiver.status_code == 201
    receiver = res_receiver.get_json()

    amount = 150
    payload = {
        "amount": amount,
        "receiverCompanyId": receiver["externalId"],
        "senderAuthority": "bank"
    }

    res = client.post("/api/check-transaction", json=payload)
    assert res.status_code == 201
    tx = res.get_json()

    # Basic assertions about response shape and values
    assert tx["amount"] == amount
    assert tx["receiverCompanyId"] == receiver["externalId"]
    assert tx["senderAuthority"].lower() == "bank"
    assert "externalId" in tx

    # OPTIONAL: if your GET company returns balance, assert it increased
    # (assumes initial balance was 0 or known)
    res_get = client.get(f"/api/company/{receiver['externalId']}")
    assert res_get.status_code == 200
    data = res_get.get_json()
    # check balance updated (adjust if you have starter cash)
    assert data["balance"] >= amount


@pytest.mark.parametrize("invalid_amount", [0, -20, 3.14, "abc"])
def test_create_check_transaction_invalid_amount(client, company, invalid_amount):
    # create receiver
    receiver = client.post("/api/company", json={
        "name": fake.company(),
        "ownerId": random.randint(2001, 3000)
    }).get_json()

    payload = {
        "amount": invalid_amount,
        "receiverCompanyId": receiver["externalId"],
        "senderAuthority": "system"
    }

    res = client.post("/api/check-transaction", json=payload)
    assert res.status_code == 400
    errors = res.get_json()
    # your error format may vary; be flexible:
    assert "amount" in str(errors).lower()


def test_create_check_transaction_nonexistent_receiver(client, company):
    payload = {
        "amount": 50,
        "receiverCompanyId": str(uuid.uuid4()),  # not in DB
        "senderAuthority": "bank"
    }
    res = client.post("/api/check-transaction", json=payload)
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"].lower()


def test_get_check_transaction_and_invalid_uuid(client, company):
    # create receiver
    receiver = client.post("/api/company", json={
        "name": fake.company(),
        "ownerId": random.randint(3001, 4000)
    }).get_json()

    payload = {
        "amount": 33,
        "receiverCompanyId": receiver["externalId"],
        "senderAuthority": "mint"
    }
    res_create = client.post("/api/check-transaction", json=payload)
    assert res_create.status_code == 201
    tx = res_create.get_json()
    tx_guid = tx["externalId"]

    # GET should return 200 (not 201) — adjust endpoint if necessary
    res_get = client.get(f"/api/check-transaction/{tx_guid}")
    assert res_get.status_code == 200
    fetched = res_get.get_json()
    assert fetched["externalId"] == tx_guid
    assert fetched["amount"] == payload["amount"]

    # invalid uuid returns 400
    for bad in ["not-a-uuid", "12345", "!!!"]:
        r = client.get(f"/api/check-transaction/{bad}")
        assert r.status_code == 400
        assert "invalid" in r.get_json()["error"].lower()


def test_get_nonexistent_check_transaction(client):
    fake_guid = str(uuid.uuid4())
    res = client.get(f"/api/check-transaction/{fake_guid}")
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"].lower()