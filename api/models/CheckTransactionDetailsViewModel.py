from datetime import datetime
from pydantic import BaseModel, Field

class CheckTransactionViewModel(BaseModel):
  external_id: str = Field(..., alias="ExternalID")
  amount: int = Field(..., alias="Amount")
  created_at: datetime = Field(..., alias="CreatedAt")
  receiver_company_id: str = Field(..., alias="ReceiverCompanyID")
  from_authority: str = Field(..., alias="FromAuthority")

  class Config:
    validate_by_name = True     # lets you create objects using snake_case
    from_attributes = True      # allows creating from SQLAlchemy models