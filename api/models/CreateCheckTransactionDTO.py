from pydantic import BaseModel, field_validator

from models.Exceptions import InvalidTransactionAmountError

class CreateCheckTransactionDTO(BaseModel):
  amount: int
  receiver_id: str
  from_authority: str

  @field_validator("amount")
  def amount_must_be_positive(cls, v):
      if v <= 0:
          raise InvalidTransactionAmountError("Transaction amount must be greater than 0")
      return v