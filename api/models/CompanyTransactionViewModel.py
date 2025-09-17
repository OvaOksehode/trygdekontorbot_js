from datetime import datetime
from pydantic import BaseModel, Field

class CompanyTransactionViewModel(BaseModel):
  external_id: str = Field(..., alias="ExternalID")
  amount: int = Field(..., alias="Amount")
  created_at: datetime = Field(..., alias="CreatedAt")
  receiver_id: str = Field(..., alias="ReceiverCompanyID")
  from_company_id: str = Field(..., alias="FromCompanyID")

  class Config:
    validate_by_name = True  # lets you use both aliases and attribute names
    from_attributes = True
