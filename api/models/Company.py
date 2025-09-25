from datetime import UTC, datetime
from infrastructure.db.db import db
import uuid

class Company(db.Model):
    __tablename__ = "Company"   # Plural, PascalCase

    company_id = db.Column(
        "CompanyID",
        db.Integer,
        primary_key=True
    )
    external_id = db.Column(
        "ExternalID",
        db.String(36),
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )
    name = db.Column(
        "Name",
        db.String,
        nullable=False,
        unique=True
    )
    owner_id = db.Column(
        "OwnerID",
        db.Integer,
        nullable=False,
        server_default="-1",
        unique=True
    )
    balance = db.Column(
        "Balance",
        db.Integer,
        nullable=False,
        default=0
    )
    created_at = db.Column(
        "CreatedAt",
        db.DateTime,
        default=lambda: datetime.now(UTC)
    )

    # Move these out in the future
    last_trygd_claim = db.Column(
        "LastTrygdClaim",
        db.DateTime,
        nullable=True
    )    
    trygd_amount = db.Column(
        "TrygdAmount",
        db.Integer,
        default=10,
        nullable=True
    )
    
    ledger_entries = db.relationship(
        "LedgerEntry",
        back_populates="receiver",
    )
    
    outgoing_company_transactions = db.relationship(
        "CompanyTransactionDetails",
        back_populates="sender_company",
    )
    