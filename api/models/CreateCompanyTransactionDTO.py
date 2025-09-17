from pydantic import BaseModel, Field, field_validator

from models.Exceptions import InvalidTransactionAmountError

class CreateCompanyTransactionDTO(BaseModel):
    amount: int = Field(..., alias="Amount")
    receiver_id: str = Field(..., alias="ReceiverCompanyID")
    from_company_id: str = Field(..., alias="FromCompanyID")

    @field_validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise InvalidTransactionAmountError("Transaction amount must be greater than 0")
        return v

    class Config:
        validate_by_name = True