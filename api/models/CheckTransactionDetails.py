from models.LedgerEntry import LedgerEntry
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

    # Other fields specific to checks
    check_number = db.Column("CheckNumber", db.String(50))
    issued_date = db.Column(
        "IssuedDate",
        db.DateTime,
        default=lambda: datetime.now(UTC)
    )

    __mapper_args__ = {
        "polymorphic_identity": "check_transaction_details"
    }