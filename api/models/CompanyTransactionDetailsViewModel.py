from pydantic import BaseModel, Field
from typing import Literal

from models.LedgerEntryViewModel import LedgerEntryViewModel

class CompanyTransactionDetailsViewModel(LedgerEntryViewModel):
    type: Literal["company_transaction_details"]

    sender_company_id: str = Field(..., alias="senderCompanyId")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }
