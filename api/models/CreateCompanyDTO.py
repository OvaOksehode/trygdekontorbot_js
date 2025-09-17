from pydantic import BaseModel, Field

class CreateCompanyDTO(BaseModel):
  name: str = Field(..., alias="name")
  owner_id: int = Field(..., alias="ownerId")

  class Config:
      validate_by_name = True