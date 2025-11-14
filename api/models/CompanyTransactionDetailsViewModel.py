from pydantic import BaseModel, Field


class CompanyTransactionDetailsViewModel(BaseModel):
    sender_company_id: str = Field(..., alias="senderCompanyId")

    model_config = {
        "validate_by_name": True,
        "from_attributes": True,
    }
