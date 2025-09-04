from typing import Annotated, Optional
from pydantic import BaseModel, constr

class UpdateCompanyDTO(BaseModel):
    name: Optional[Annotated[str, constr(min_length=3)]] = None
    class Config:
          extra = "forbid"  # <-- Reject any unexpected fields