from domain.models.LedgerEntry import LedgerEntry
from infrastructure.db.db import db
from datetime import UTC, datetime

class CheckTransactionDetails(LedgerEntry):
    __tablename__ = "CheckTransactionDetails"

    # Use the same PK as LedgerEntry
    ledger_entry_id = db.Column(
        "LedgerEntryID",
        db.Integer,
        db.ForeignKey(
            "LedgerEntry.LedgerEntryID",
            name="fk_CheckTransactionDetails_LedgerEntryID"
        ),
        primary_key=True
    )

    sender_authority = db.Column(
        "SenderAuthority",
        db.String,
        nullable=False
    )

    __mapper_args__ = {
        "polymorphic_identity": "checkTransaction"
    }