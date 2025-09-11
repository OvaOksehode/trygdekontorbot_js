# repositories/LedgerEntryRepository.py
from typing import Tuple
from infrastructure.db.db import db
from models.LedgerEntry import LedgerEntry
from models.CompanyTransactionDetails import CompanyTransactionDetails

class LedgerEntryRepository:

    @staticmethod
    def get_by_id(entry_id: int) -> LedgerEntry | None:
        return db.session.get(LedgerEntry, entry_id)

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

    # Extra helpers (if you want type-specific queries)

    # @staticmethod
    # def get_company_transactions() -> list[CompanyTransaction]:
    #     return db.session.query(CompanyTransaction).all()

    # @staticmethod
    # def get_checks() -> list[Check]:
    #     return db.session.query(Check).all()
