from models.LedgerEntry import LedgerEntry
from infrastructure.db.db import db
from datetime import UTC, datetime

class CheckTransactionDetails(db.Model):
    # PK is also FK to LedgerEntry
    id = db.Column(
        db.Integer,
        db.ForeignKey('ledger_entry.id'),
        primary_key=True
    )

    from_authority = db.Column(db.String, nullable=False)
    # Add other fields specific to CompanyTransactionDetails here

    # Relationship back to LedgerEntry (1:1)
    ledger_entry = db.relationship(
        LedgerEntry,
        backref=db.backref('check_transaction_details', uselist=False),
        uselist=False
    )
