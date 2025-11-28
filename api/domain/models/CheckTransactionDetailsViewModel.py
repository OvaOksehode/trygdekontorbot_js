from datetime import datetime
from typing import Literal

from domain.models.LedgerEntryViewModel import LedgerEntryViewModel

class CheckTransactionDetailsViewModel(LedgerEntryViewModel):
    type: Literal["check_transaction_details"]
    sender_authority: str

    model_config = dict(from_attributes=True)
