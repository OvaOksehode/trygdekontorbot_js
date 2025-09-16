from datetime import datetime
from pydantic import BaseModel

class CheckTransactionViewModel(BaseModel):
  external_id: str
  amount: int
  created_at: datetime
  receiver_id: str
  from_authority: str