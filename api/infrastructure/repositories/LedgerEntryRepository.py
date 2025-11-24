# repositories/LedgerEntryRepository.py
from typing import Optional, Tuple
from models.Company import Company
from models.Exceptions import InvalidQueryError, LedgerEntryNotFoundError
from infrastructure.db.db import db
from sqlalchemy.orm import selectinload
from models.CheckTransactionDetails import CheckTransactionDetails
from models.LedgerEntry import LedgerEntry
from models.CompanyTransactionDetails import CompanyTransactionDetails

class LedgerEntryRepository:

    @staticmethod
    def get_by_id(entry_id: int) -> LedgerEntry | None:
        return db.session.get(LedgerEntry, entry_id)

    @staticmethod
    def get_by_external_id(external_id: str):
        return (
            db.session.query(LedgerEntry)
            .filter(LedgerEntry.external_id == external_id)
            .options(
                # only needed if there's a chance the entry is CompanyTransactionDetails
                selectinload(CompanyTransactionDetails.sender_company)
            )
            .first()
        )


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
    def createCompanyTransaction(tx_details: CompanyTransactionDetails) -> CompanyTransactionDetails:
        """
        Creates a CompanyTransactionDetails, which is a subclass of LedgerEntry.
        """
        
        db.session.add(tx_details)
        db.session.commit()
        db.session.refresh(tx_details)

        return tx_details

    @staticmethod
    def createCheckTransaction(tx_details: CheckTransactionDetails) -> CheckTransactionDetails:
        """
        Creates a CheckTransactionDetails, which is a subclass of LedgerEntry.
        """
        # Persist the subclass only — SQLAlchemy handles the base table insert
        db.session.add(tx_details)
        db.session.commit()
        db.session.refresh(tx_details)

        return tx_details

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
    def add(entry: LedgerEntry) -> LedgerEntry:
        db.session.add(entry)
        db.session.commit()
        return entry
    
    @staticmethod
    def query_ledger_entries(filters: dict) -> list[LedgerEntry]:
        """
        filters: keys are normalized DB-ish names, e.g.
        - "type" -> LedgerEntry.type
        - "sender_company.name" -> Company.name via CompanyTransactionDetails
        - "receiver_company.name" -> Company.name via LedgerEntry.receiver (if applicable)
        """

        query = db.session.query(LedgerEntry)

        # Track whether we've already joined the subclass/company, so we don't join twice
        joined_company_sender = False
        joined_company_receiver = False

        for key, value in filters.items():

            # relational: sender_company.name -> join subclass then Company
            if key.startswith("sender_company."):
                field = key.split(".", 1)[1]

                # join the subclass table (CompanyTransactionDetails) to expose its FKs
                # join condition is on the PK/FK inheritance column
                if not joined_company_sender:
                    query = query.join(
                        CompanyTransactionDetails,
                        CompanyTransactionDetails.ledger_entry_id == LedgerEntry.ledger_entry_id
                    )
                    # now join the company table using relationship attribute on subclass
                    query = query.join(Company, Company.company_id == CompanyTransactionDetails.sender_company_id)
                    joined_company_sender = True

                query = query.filter(getattr(Company, field) == value)
                continue

            # (optional) receiver_company.name if you modeled receiver relationship directly on LedgerEntry
            if key.startswith("receiver_company."):
                field = key.split(".", 1)[1]

                if not joined_company_receiver:
                    # if LedgerEntry.receiver is a relationship to Company, do:
                    query = query.join(Company, Company.company_id == LedgerEntry.receiver_company_id)
                    joined_company_receiver = True

                query = query.filter(getattr(Company, field) == value)
                continue

            # simple ledger field filters, exact matches
            if hasattr(LedgerEntry, key):
                query = query.filter(getattr(LedgerEntry, key) == value)
            else:
                # unknown key -> raise or ignore depending on your policy
                raise InvalidQueryError(f"Invalid filter: {key}")

        return query.all()


    # Extra helpers (if you want type-specific queries)

    # @staticmethod
    # def get_company_transactions() -> list[CompanyTransaction]:
    #     return db.session.query(CompanyTransaction).all()

    # @staticmethod
    # def get_checks() -> list[Check]:
    #     return db.session.query(Check).all()
