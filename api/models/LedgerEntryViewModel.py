from datetime import datetime
from pydantic import BaseModel, Field

class LedgerEntryViewModel(BaseModel):
    external_id: str = Field(..., alias="externalId")
    amount: int = Field(..., alias="amount")
    created_at: datetime = Field(..., alias="createdAt")
    receiver_company_id: str = Field(..., alias="receiverCompanyId")

    model_config = {
        "validate_by_name": True,
        "from_attributes": True,
    }
