from datetime import datetime
from pydantic import BaseModel

class CompanyTransactionViewModel(BaseModel):
  external_id: str
  amount: int
  created_at: datetime
  receiver_id: int
  from_company_id: int