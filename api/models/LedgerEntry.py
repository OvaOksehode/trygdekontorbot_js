import uuid
from infrastructure.db.db import db
from datetime import UTC, datetime

class LedgerEntry(db.Model):
    __tablename__ = "LedgerEntry"

    LedgerEntryID = db.Column(db.Integer, primary_key=True)
    ExternalID = db.Column(db.String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    Amount = db.Column(db.Integer, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    ReceiverCompanyID = db.Column(
        db.String(36),
        db.ForeignKey(
            "Company.CompanyID",
            name="fk_LedgerEntry_ReceiverCompanyID"
        ),
        nullable=False
    )

    Receiver = db.relationship(
        'Company',
        foreign_keys=[ReceiverCompanyID],
        backref='LedgerEntries'
    )
