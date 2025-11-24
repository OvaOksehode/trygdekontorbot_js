from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, Any
from datetime import datetime

class CreateLedgerEntryDTO(BaseModel):
    amount: int = Field(..., alias="amount")
    receiver: Optional[Any] = Field(None, exclude=True)
    type: str = Field(..., alias="type")

    sender_authority: Optional[str] = Field(None, alias="senderAuthority")

    # Internal: allow Pydantic to pick up the relationship from the ORM object.
    # Excluded from output so it does not leak.
    sender_company: Optional[Any] = Field(None, exclude=True)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    # Computed field exposed in JSON as senderCompanyExternalId
    @computed_field(alias="senderCompanyExternalId")
    def sender_company_external_id(self) -> Optional[str]:
        # `self.sender_company` is the ORM Company instance (or None)
        company = self.sender_company
        if company is None:
            return None
        # adapt to whatever your Company uses for the external id attribute name
        return getattr(company, "external_id", None)
    @computed_field(alias="receiverCompanyExternalId")
    def receiver_company_external_id(self) -> Optional[str]:
        # `self.sender_company` is the ORM Company instance (or None)
        company = self.receiver
        if company is None:
            return None
        # adapt to whatever your Company uses for the external id attribute name
        return getattr(company, "external_id", None)