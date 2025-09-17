from pydantic import BaseModel, Field

class CreateCompanyDTO(BaseModel):
  name: str = Field(..., alias="Name")
  owner: int = Field(..., alias="OwnerID")

  class Config:
      validate_by_name = True