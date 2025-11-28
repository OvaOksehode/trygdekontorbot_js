from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, Any
from datetime import datetime

class LedgerEntryViewModel(BaseModel):
    # Base fields
    external_id: str = Field(..., alias="externalId")
    amount: int = Field(..., alias="amount")
    created_at: datetime = Field(..., alias="createdAt")
    type: str = Field(..., alias="type")

    # Optional fields for polymorphic types
    sender_authority: Optional[str] = Field(None, alias="senderAuthority")

    # Internal / ORM relationships (excluded from JSON)
    receiver: Optional[Any] = Field(None, exclude=True)
    sender_company: Optional[Any] = Field(None, exclude=True)

    # Pydantic config
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    # Computed fields for JSON
    @computed_field(alias="senderCompanyExternalId")
    def sender_company_external_id(self) -> Optional[str]:
        if self.sender_company is None:
            return None
        return getattr(self.sender_company, "external_id", None)

    @computed_field(alias="receiverCompanyExternalId")
    def receiver_company_external_id(self) -> Optional[str]:
        if self.receiver is None:
            return None
        return getattr(self.receiver, "external_id", None)
