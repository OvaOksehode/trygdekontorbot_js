from datetime import UTC, datetime
from infrastructure.db.db import db
import uuid

class Company(db.Model):
    __tablename__ = "Company"   # Plural, PascalCase

    CompanyID = db.Column(db.Integer, primary_key=True)
    ExternalID = db.Column(db.String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    Name = db.Column(db.String, nullable=False, unique=True)
    OwnerID = db.Column(db.Integer, nullable=False, server_default="-1", unique=True)
    Balance = db.Column(db.Integer, nullable=False, default=0)
    CreatedAt = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    LastTrygdClaim = db.Column(db.DateTime, nullable=True)    # Should be moved to ClaimTransaction
    TrygdAmount = db.Column(db.Integer, nullable=True)
