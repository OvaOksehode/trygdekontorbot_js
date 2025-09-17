from models.LedgerEntry import LedgerEntry
from infrastructure.db.db import db
from datetime import UTC, datetime

class CheckTransactionDetails(db.Model):
    __tablename__ = "CheckTransactionDetails"  # plural table name

    # PK is also FK to LedgerEntry
    LedgerEntryID = db.Column(
        db.Integer,
        db.ForeignKey(
            "LedgerEntry.LedgerEntryID",
            name="fk_CheckTransactionDetails_LedgerEntryID"
        ),
        primary_key=True
    )

    SenderAuthority = db.Column(db.String, nullable=False)
    # Add other fields specific to CompanyTransactionDetails here

    # Relationship back to LedgerEntry (1:1)
    LedgerEntry = db.relationship(
        "LedgerEntry",
        backref=db.backref('CheckTransactionDetails', uselist=False),
        uselist=False
    )
