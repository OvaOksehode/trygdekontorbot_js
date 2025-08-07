from pydantic import BaseModel
from datetime import date

class CompanyDTO(BaseModel):
  name: str
  discord_id: int