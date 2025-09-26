from datetime import datetime
from pydantic import BaseModel, Field

class CompanyViewModel(BaseModel):
    external_id: str = Field(..., alias="externalId")
    name: str = Field(..., alias="name")
    owner_id: int = Field(..., alias="ownerId")
    balance: int = Field(..., alias="balance")
    created_at: datetime = Field(..., alias="createdAt")
    deleted_at: datetime = Field(..., alias="deletedAt")
    last_trygd_claim: datetime | None = Field(None, alias="lastTrygdClaim")

    class Config:
        validate_by_name = True  # supports both aliases and field names
        from_attributes = True