from pydantic import BaseModel

class CompanyDTO(BaseModel):
  name: str