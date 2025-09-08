from datetime import UTC, datetime
from infrastructure.db.db import db
import uuid

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String, nullable=False, unique=True)
    owner = db.Column(db.Integer, nullable=False, server_default="-1", unique=True)
    balance = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    last_trygd_claim = db.Column(db.DateTime, nullable=True)    # Should be moved to ClaimTransaction
    trygd_amount = db.Column(db.Integer, nullable=True)
