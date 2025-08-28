from models import CreateCompanyStatus
from pydantic import BaseModel
from typing import Optional, Dict

class CreateCompanyResult(BaseModel):
    success: bool
    status: CreateCompanyStatus
    message: str
    data: Optional[Dict] = None
