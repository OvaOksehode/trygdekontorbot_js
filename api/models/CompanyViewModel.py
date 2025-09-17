from datetime import datetime
from pydantic import BaseModel, Field

class CompanyViewModel(BaseModel):
    external_id: str = Field(..., alias="ExternalID")
    name: str = Field(..., alias="Name")
    owner: int = Field(..., alias="OwnerID")
    balance: int = Field(..., alias="Balance")
    created_at: datetime = Field(..., alias="CreatedAt")
    last_trygd_claim: datetime | None = Field(None, alias="LastTrygdClaim")

    class Config:
        validate_by_name = True  # supports both aliases and field names
        from_attributes = True