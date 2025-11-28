from domain.models.LedgerEntry import LedgerEntry
from infrastructure.db.db import db
from datetime import UTC, datetime


class CompanyTransactionDetails(LedgerEntry):
    __tablename__ = "CompanyTransactionDetails"

    # Use the same PK as LedgerEntry (inheritance FK)
    ledger_entry_id = db.Column(
        "LedgerEntryID",
        db.Integer,
        db.ForeignKey(
            "LedgerEntry.LedgerEntryID",
            name="fk_CompanyTransactionDetails_LedgerEntryID"
        ),
        primary_key=True
    )

    sender_company_id = db.Column(
        "SenderCompanyID",
        db.String(36),
        db.ForeignKey(
            "Company.CompanyID",
            name="fk_CompanyTransactionDetails_SenderCompanyID"
        ),
        nullable=False
    )

    # 🔹 Relationship to Company
    sender_company = db.relationship(
        "Company",
        foreign_keys=[sender_company_id],
        back_populates="outgoing_company_transactions"
    )

    __mapper_args__ = {
        "polymorphic_identity": "companyTransaction"
    }