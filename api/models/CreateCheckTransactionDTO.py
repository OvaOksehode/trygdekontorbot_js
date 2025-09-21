from pydantic import BaseModel, Field, field_validator

from models.Exceptions import InvalidTransactionAmountError

class CreateCheckTransactionDTO(BaseModel):
  amount: int
  receiver_company_id: str = Field(..., alias="receiverCompanyId")
  sender_authority: str = Field(..., alias="senderAuthority")

  @field_validator("amount")
  def amount_must_be_positive(cls, v):
      if v <= 0:
          raise InvalidTransactionAmountError("Transaction amount must be greater than 0")
      return v
  
  class Config:
      validate_by_name = True