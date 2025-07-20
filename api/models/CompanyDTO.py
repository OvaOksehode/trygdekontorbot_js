from pydantic import BaseModel, EmailStr
from datetime import date

class CompanyDTO(BaseModel):
  name: str
  birth_date: date
  experience_in_years: int
  email: EmailStr