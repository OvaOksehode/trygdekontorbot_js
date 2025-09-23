from models.LedgerEntry import LedgerEntry
from infrastructure.db.db import db
from datetime import UTC, datetime

class CheckTransactionDetails(db.Model):
    __tablename__ = "CheckTransactionDetails"  # plural table name

    # PK is also FK to LedgerEntry
    ledger_entry_id = db.Column(
        "LedgerEntryID",
        db.Integer,
        db.ForeignKey(
            "LedgerEntry.LedgerEntryID",
            name="fk_CheckTransactionDetails_LedgerEntryID",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    sender_authority = db.Column(
        "SenderAuthority",
        db.String,
        nullable=False
    )
    # Add other fields specific to CompanyTransactionDetails here

    # Relationship back to LedgerEntry (1:1)
    ledger_entry = db.relationship(
        "LedgerEntry",
        backref=db.backref('check_transaction_details', uselist=False),
        uselist=False
    )
