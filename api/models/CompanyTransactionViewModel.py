from datetime import datetime
from pydantic import BaseModel, Field

class CompanyTransactionViewModel(BaseModel):
  external_id: str = Field(..., alias="externalId")
  amount: int = Field(..., alias="amount")
  created_at: datetime = Field(..., alias="createdAt")
  receiver_company_id: str = Field(..., alias="receiverCompanyId")
  sender_company_id: str = Field(..., alias="senderCompanyId")

  class Config:
    validate_by_name = True  # lets you use both aliases and attribute names
    from_attributes = True
