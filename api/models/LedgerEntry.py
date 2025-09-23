import uuid
from infrastructure.db.db import db
from datetime import UTC, datetime

class LedgerEntry(db.Model):
    __tablename__ = "LedgerEntry"

    ledger_entry_id = db.Column(
        "LedgerEntryID",
        db.Integer, 
        primary_key=True
    )
    external_id = db.Column(
        "ExternalID",
        db.String(36),
        nullable=False, 
        default=lambda: str(uuid.uuid4())
    )
    amount = db.Column(
        "Amount",
        db.Integer,
        nullable=False
    )
    created_at = db.Column(
        "CreatedAt",
        db.DateTime,
        default=lambda: datetime.now(UTC)
    )
    receiver_company_id = db.Column(
        "ReceiverCompanyID",
        db.Integer,
        db.ForeignKey(
            "Company.CompanyID",
            name="fk_LedgerEntry_ReceiverCompanyID"
        ),
        nullable=False
    )

    receiver = db.relationship(
        'Company',
        back_populates="ledger_entries"
    )
    
    company_transaction_details = db.relationship(
        "CompanyTransactionDetails",
        back_populates="ledger_entry",
        cascade="all, delete-orphan",
        uselist=False
    )

    check_transaction_details = db.relationship(
        "CheckTransactionDetails",
        back_populates="ledger_entry",
        cascade="all, delete-orphan",
        uselist=False
    )