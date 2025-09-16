from typing import Tuple
from models.CheckTransactionDetails import CheckTransactionDetails
from models.CreateCheckTransactionDTO import CreateCheckTransactionDTO
from models.Exceptions import CompanyNotEnoughFundsError, CompanyNotFoundError, LedgerEntryNotFoundError
from infrastructure.repositories.CompanyRepository import CompanyRepository
from infrastructure.repositories.LedgerEntryRepository import LedgerEntryRepository
from models import CompanyTransactionDetails, CreateCompanyTransactionDTO, LedgerEntry


def create_company_transaction(dto_data: CreateCompanyTransactionDTO) -> Tuple[LedgerEntry, CompanyTransactionDetails]:
    # Check that sender and receiver exists
    sender = CompanyRepository.get_by_external_id(dto_data.from_company_id)
    receiver = CompanyRepository.get_by_external_id(dto_data.receiver_id)

    if sender is None or receiver is None:
        raise CompanyNotFoundError(f"Company with external_guid {dto_data.from_company_id} not found")
    
    if dto_data.amount > sender.balance:
        raise CompanyNotEnoughFundsError(f"Sender {sender.name} does not have enough funds to complete the requested transaction")

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
    sender.balance -= dto_data.amount
    receiver.balance += dto_data.amount

    CompanyRepository.update(sender)
    CompanyRepository.update(receiver)

    return persisted_ledger, persisted_tx

def create_check_transaction(dto_data: CreateCheckTransactionDTO) -> Tuple[LedgerEntry, CheckTransactionDetails]:
    # Check that sender and receiver exists
    receiver = CompanyRepository.get_by_external_id(dto_data.receiver_id)

    if receiver is None:
        raise CompanyNotFoundError(f"Company with external_guid {dto_data.from_company_id} not found")

    # Check that sender has enough balance
    newLedgerEntry = LedgerEntry(
        amount = dto_data.amount,
        receiver_id = dto_data.receiver_id
    )
    newCheckTransactionDetails = CheckTransactionDetails(
        from_authority = dto_data.from_authority
    )
    # Persist ledger + transaction details via repository
    persisted_ledger, persisted_tx = LedgerEntryRepository.createCompanyTransaction(
        newLedgerEntry,
        newCheckTransactionDetails
    )

    # Update balances after persistence
    receiver.balance += dto_data.amount

    CompanyRepository.update(receiver)

    return persisted_ledger, persisted_tx

def get_company_transaction_by_external_guid(external_guid: str):
    transaction = LedgerEntryRepository.get_by_external_id(external_guid);
    if transaction is None:
        raise LedgerEntryNotFoundError(f"Company with external_guid {external_guid} not found")
    return transaction