from datetime import datetime
from pydantic import BaseModel, Field

class CheckTransactionViewModel(BaseModel):
  external_id: str = Field(..., alias="externalId")
  amount: int = Field(..., alias="amount")
  created_at: datetime = Field(..., alias="createdAt")
  receiver_company_id: str = Field(..., alias="receiverCompanyId")
  sender_authority: str = Field(..., alias="senderAuthority")

  class Config:
    validate_by_name = True     # lets you create objects using snake_case
    from_attributes = True      # allows creating from SQLAlchemy models