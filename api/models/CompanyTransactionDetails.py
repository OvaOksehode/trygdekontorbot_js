from models.LedgerEntry import LedgerEntry
from infrastructure.db.db import db
from datetime import UTC, datetime

class CompanyTransactionDetails(db.Model):
    __tablename__ = "CompanyTransactionDetails"  # singular, PascalCase

    # PK is also FK to LedgerEntry
    LedgerEntryID = db.Column(
        db.Integer,
        db.ForeignKey(
            "LedgerEntry.LedgerEntryID",
            name="fk_CompanyTransactionDetails_LedgerEntryID"
        ),
        primary_key=True
    )

    SenderCompanyID = db.Column(
        db.String(36),
        db.ForeignKey(
            "Company.CompanyID",
            name="fk_CompanyTransactionDetails_SenderCompanyID"
        ),
        nullable=False
    )
    # Add other fields specific to CompanyTransactionDetails here

    # Relationship back to LedgerEntry (1:1)
    LedgerEntry = db.relationship(
        "LedgerEntry",
        backref=db.backref('CompanyTransactionDetails', uselist=False),
        uselist=False
    )

    SenderCompany = db.relationship(
        "Company",
        foreign_keys=[SenderCompanyID],
        backref="OutgoingTransactions"  # all outgoing transactions initiated by this company
    )