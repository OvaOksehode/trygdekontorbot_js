import uuid
from infrastructure.db.db import db
from datetime import UTC, datetime

class LedgerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    receiver_id = db.Column(db.String(36), db.ForeignKey('company.id'), nullable=False)

    receiver = db.relationship(
        'Company',
        foreign_keys=[receiver_id],
        backref='ledger_entries'
    )
