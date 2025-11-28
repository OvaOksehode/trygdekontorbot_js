from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class CreateLedgerEntryDTO(BaseModel):
    type: str = Field(..., alias="type")
    amount: int = Field(..., alias="amount")
    
    # Only include input fields relevant for creation
    sender_authority: Optional[str] = Field(None, alias="senderAuthority")
    sender_company_id: Optional[str] = Field(None, alias="senderCompanyId")
    receiver_company_id: Optional[str] = Field(None, alias="receiverCompanyId")


    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )