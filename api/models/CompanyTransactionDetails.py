from models.LedgerEntry import LedgerEntry
from infrastructure.db.db import db
from datetime import UTC, datetime

class CompanyTransactionDetails(db.Model):
    __tablename__ = "CompanyTransactionDetails"  # singular, PascalCase

    # PK is also FK to LedgerEntry
    ledger_entry_id = db.Column(
        "LedgerEntryID",
        db.Integer,
        db.ForeignKey(
            "LedgerEntry.LedgerEntryID",
            name="fk_CompanyTransactionDetails_LedgerEntryID"
        ),
        primary_key=True
    )

    sender_company_id = db.Column(
        "SenderCompanyID",
        db.String(36),
        db.ForeignKey(
            "Company.CompanyID",
            name="fk_CompanyTransactionDetails_SenderCompanyID"
        ),
        nullable=False
    )
    # Add other fields specific to CompanyTransactionDetails here

    # Relationship back to LedgerEntry (1:1)
    ledger_entry = db.relationship(
        "LedgerEntry",
        backref=db.backref('company_transaction_details', uselist=False),
        uselist=False
    )

    sender_company = db.relationship(
        "Company",
        foreign_keys=[sender_company_id],
        backref="outgoing_transactions"  # all outgoing transactions initiated by this company
    )
    
    class Config:
      validate_by_name = True