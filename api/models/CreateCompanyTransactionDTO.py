from pydantic import BaseModel

class CreateCompanyTransactionDTO(BaseModel):
  amount: int
  receiver_id: int
  from_company_id: int