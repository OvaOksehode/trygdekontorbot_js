from pydantic import BaseModel

class CreateCompanyDTO(BaseModel):
  name: str
  owner: int