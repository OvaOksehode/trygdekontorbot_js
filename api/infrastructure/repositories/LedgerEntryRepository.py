# repositories/LedgerEntryRepository.py
from typing import Optional, Tuple
from models.Exceptions import LedgerEntryNotFoundError
from infrastructure.db.db import db
from models.CheckTransactionDetails import CheckTransactionDetails
from models.LedgerEntry import LedgerEntry
from models.CompanyTransactionDetails import CompanyTransactionDetails

class LedgerEntryRepository:

    @staticmethod
    def get_by_id(entry_id: int) -> LedgerEntry | None:
        return db.session.get(LedgerEntry, entry_id)

    @staticmethod
    def get_company_transaction_by_external_id(external_id: str) -> Optional[Tuple[LedgerEntry, CompanyTransactionDetails]]:
        """
        Fetch a LedgerEntry with its CompanyTransactionDetails by external_id.
        Returns None if not found or if no company transaction details exist.
        """
        result = (
            db.session.query(LedgerEntry, CompanyTransactionDetails)
            .join(CompanyTransactionDetails, CompanyTransactionDetails.ledger_entry_id == LedgerEntry.ledger_entry_id)
            .filter(LedgerEntry.external_id == external_id)
            .first()
        )

        if result is None:
            raise LedgerEntryNotFoundError(f"Company transaction with external_id {external_id} not found")

        return result  # will be (LedgerEntry, CompanyTransactionDetails) or None

    @staticmethod
    def get_check_transaction_by_external_id(external_id: str) -> Optional[Tuple[LedgerEntry, CompanyTransactionDetails]]:
        """
        Fetch a LedgerEntry with its CompanyTransactionDetails by external_id.
        Returns None if not found or if no company transaction details exist.
        """
        result = (
            db.session.query(LedgerEntry, CheckTransactionDetails)
            .join(CheckTransactionDetails, CheckTransactionDetails.ledger_entry_id == LedgerEntry.ledger_entry_id)
            .filter(LedgerEntry.external_id == external_id)
            .first()
        )

        if result is None:
            raise LedgerEntryNotFoundError(f"Check transaction with external_id {external_id} not found")

        return result  # will be (LedgerEntry, CompanyTransactionDetails) or None

    @staticmethod
    def get_all() -> list[LedgerEntry]:
        """
        Returns all ledger entries, joined with their concrete subclass rows
        (TPT). SQLAlchemy polymorphic loading takes care of materializing
        the right subclass objects.
        """
        return db.session.query(LedgerEntry).all()

    @staticmethod
    def createCompanyTransaction(ledger_entry: LedgerEntry, tx_details: CompanyTransactionDetails) -> Tuple[LedgerEntry, CompanyTransactionDetails]:
        """
        Persists a LedgerEntry and its corresponding CompanyTransactionDetails
        in a single atomic transaction, setting up the 1:1 relationship.
        """

        # Link 1:1 relationship
        tx_details.ledger_entry = ledger_entry

        # Persist both objects
        db.session.add(ledger_entry)
        db.session.add(tx_details)

        # Commit atomically
        db.session.commit()

        # Now tx_details.id == ledger_entry.id because of FK
        return ledger_entry, tx_details

    @staticmethod
    def createCheckTransaction(ledger_entry: LedgerEntry, tx_details: CheckTransactionDetails) -> Tuple[LedgerEntry, CheckTransactionDetails]:
        """
        Persists a LedgerEntry and its corresponding CompanyTransactionDetails
        in a single atomic transaction, setting up the 1:1 relationship.
        """

        # Link 1:1 relationship
        tx_details.ledger_entry = ledger_entry

        # Persist both objects
        db.session.add(ledger_entry)
        db.session.add(tx_details)

        # Commit atomically
        db.session.commit()

        # Now tx_details.id == ledger_entry.id because of FK
        return ledger_entry, tx_details

    @staticmethod
    def update(entry: LedgerEntry) -> LedgerEntry:
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def delete(entry_id: int) -> bool:
        entry = LedgerEntryRepository.get_by_id(entry_id)
        if not entry:
            return False
        db.session.delete(entry)
        db.session.commit()
        return True

    @staticmethod
    def query_ledger_entries(filters: dict, limit: int | None = None):
        query = db.session.query(LedgerEntry)

        if "company_uuid" in filters:
            query = query.filter(LedgerEntry.company_uuid == filters["company_uuid"])
        if "type" in filters:
            query = query.filter(LedgerEntry.type == filters["type"])
        if "created_at__gte" in filters:
            query = query.filter(LedgerEntry.created_at >= filters["created_at__gte"])
        if "created_at__lte" in filters:
            query = query.filter(LedgerEntry.created_at <= filters["created_at__lte"])

        query = query.order_by(LedgerEntry.created_at.desc())
        if limit:
            query = query.limit(limit)

        return query.all()


    # Extra helpers (if you want type-specific queries)

    # @staticmethod
    # def get_company_transactions() -> list[CompanyTransaction]:
    #     return db.session.query(CompanyTransaction).all()

    # @staticmethod
    # def get_checks() -> list[Check]:
    #     return db.session.query(Check).all()
