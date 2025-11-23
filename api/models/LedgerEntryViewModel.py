from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, Any
from datetime import datetime

class LedgerEntryViewModel(BaseModel):
    external_id: str = Field(..., alias="externalId")
    amount: int = Field(..., alias="amount")
    created_at: datetime = Field(..., alias="createdAt")
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
