from pydantic import BaseModel
import uuid

class Company(BaseModel):
    company_id: str
    name: str
    created: Date

    last_trygd_claim = Column(Integer, nullable=True)
    trygd_amount = Column(Integer, nullable=False, default=10)
