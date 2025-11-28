import pytest
from datetime import datetime, UTC, timedelta
from domain.models.LedgerEntry import LedgerEntry
from domain.models.CompanyTransactionDetails import CompanyTransactionDetails
from domain.models.CheckTransactionDetails import CheckTransactionDetails
from infrastructure.repositories.LedgerEntryRepository import LedgerRepository
from infrastructure.db.db import db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """
    Creates a clean in-memory SQLite database for each test.
    """
    db.create_all()
    yield
    db.session.rollback()
    db.drop_all()


@pytest.fixture
def seed_data():
    """Seed some LedgerEntry and subclass data for testing."""
    base_entry = LedgerEntry(
        amount=1000,
        receiver_company_id=1,
        created_at=datetime.now(UTC) - timedelta(days=2),
    )
    company_entry = CompanyTransactionDetails(
        amount=2000,
        receiver_company_id=2,
        sender_company_id="A1",
        created_at=datetime.now(UTC) - timedelta(days=1),
    )
    check_entry = CheckTransactionDetails(
        amount=3000,
        receiver_company_id=3,
        sender_authority="Finance",
        created_at=datetime.now(UTC),
    )

    db.session.add_all([base_entry, company_entry, check_entry])
    db.session.commit()

    return {
        "base": base_entry,
        "company": company_entry,
        "check": check_entry,
    }


def test_query_all_entries(seed_data):
    """It should return all ledger entries polymorphically."""
    results = LedgerRepository.query_ledger_entries({})
    assert len(results) == 3
    # Polymorphic instances
    types = {type(r).__name__ for r in results}
    assert "LedgerEntry" in types
    assert "CompanyTransactionDetails" in types
    assert "CheckTransactionDetails" in types


def test_filter_by_receiver_company_id(seed_data):
    """It should filter correctly by receiver_company_id."""
    results = LedgerRepository.query_ledger_entries({"receiver_company_id": 2})
    assert len(results) == 1
    assert isinstance(results[0], CompanyTransactionDetails)
    assert results[0].receiver_company_id == 2


def test_filter_by_type(seed_data):
    """It should filter by type discriminator correctly."""
    results = LedgerRepository.query_ledger_entries({"type": "check_transaction_details"})
    assert len(results) == 1
    assert isinstance(results[0], CheckTransactionDetails)
    assert results[0].amount == 3000


def test_limit_results(seed_data):
    """It should apply the limit correctly."""
    results = LedgerRepository.query_ledger_entries({}, limit=2)
    assert len(results) == 2


def test_order_by_created_at_desc(seed_data):
    """It should order entries newest first."""
    results = LedgerRepository.query_ledger_entries({})
    assert results[0].created_at >= results[1].created_at
