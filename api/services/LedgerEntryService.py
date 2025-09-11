from typing import Tuple
from infrastructure.repositories.LedgerEntryRepository import LedgerEntryRepository
from models import CompanyTransactionDetails, CreateCompanyTransactionDTO, LedgerEntry


def create_company_transaction(dto_data: CreateCompanyTransactionDTO) -> Tuple[LedgerEntry, CompanyTransactionDetails]:
    # Check that sender and receiver exists
    # Check that sender has enough balance
    newLedgerEntry = LedgerEntry(
        amount = dto_data.amount,
        receiver_id = dto_data.receiver_id
    )
    newCompanyTransactionDetails = CompanyTransactionDetails(
        from_company_id = dto_data.from_company_id
    )
    # Persist ledger + transaction details via repository
    persisted_ledger, persisted_tx = LedgerEntryRepository.createCompanyTransaction(
        newLedgerEntry,
        newCompanyTransactionDetails
    )

    # Update balances after persistence
    # sender.balance -= dto_data.amount
    # receiver.balance += dto_data.amount

    # CompanyRepository.update(sender)
    # CompanyRepository.update(receiver)

    return persisted_ledger, persisted_tx