from typing import Union

from pydantic import TypeAdapter

from models.CheckTransactionDetailsViewModel import CheckTransactionDetailsViewModel
from models.CompanyTransactionDetailsViewModel import CompanyTransactionDetailsViewModel
from models.LedgerEntryViewModel import LedgerEntryViewModel

LedgerEntryUnion = TypeAdapter[
    LedgerEntryViewModel,
    CompanyTransactionDetailsViewModel,
    CheckTransactionDetailsViewModel,
]
