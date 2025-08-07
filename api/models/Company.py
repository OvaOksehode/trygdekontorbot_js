from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Date
from infrastructure.db.db_context import db
import uuid

class Company(db.Model):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    company_id = Column(String(36), index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    owner_discord_id = Column(Integer, unique=True, nullable=False)
    created = Column(Date, nullable=False, default=lambda: datetime.now(timezone.utc))

    last_trygd_claim = Column(Integer, nullable=True)
    trygd_amount = Column(Integer, nullable=False, default=10)
