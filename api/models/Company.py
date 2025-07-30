from sqlalchemy import Column, String, Integer, Date
from infrastructure.db.db_context import db
import uuid

class Company(db.Model):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    company_id = Column(String(36), index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    experience_in_years = Column(Integer, nullable=False)
    email = Column(String, unique=True, nullable=False)

    last_trygd_claim = Column(Integer, nullable=False)
    trygd_amount = Column(Integer, nullable=False)
