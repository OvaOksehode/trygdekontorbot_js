from datetime import datetime
from pydantic import BaseModel

class CompanyViewModel(BaseModel):
    external_id: str
    name: str
    owner: int
    balance: int
    created_at: datetime

    last_trygd_claim: datetime | None = None
