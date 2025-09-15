from pydantic import BaseModel, field_validator

from models.Exceptions import InvalidTransactionAmountError

class CreateCompanyTransactionDTO(BaseModel):
  amount: int
  receiver_id: str
  from_company_id: str

  @field_validator("amount")
  def amount_must_be_positive(cls, v):
      if v <= 0:
          raise InvalidTransactionAmountError("Transaction amount must be greater than 0")
      return v