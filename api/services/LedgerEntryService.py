from datetime import UTC, datetime, timedelta, timezone
from typing import Tuple
from models.CheckTransactionDetails import CheckTransactionDetails
from models.CreateCheckTransactionDTO import CreateCheckTransactionDTO
from models.Exceptions import ClaimCooldownActiveError, CompanyNotEnoughFundsError, CompanyNotFoundError, InvalidQueryError, LedgerEntryNotFoundError
from infrastructure.repositories.CompanyRepository import CompanyRepository
from infrastructure.repositories.LedgerEntryRepository import LedgerEntryRepository
from models.CreateCompanyTransactionDTO import CreateCompanyTransactionDTO
from models.CompanyTransactionDetails import CompanyTransactionDetails
from models.LedgerEntry import LedgerEntry
from config import settings


ALLOWED_QUERY_FILTERS = {
    "receiverCompanyId": "receiver_company_uuid",
    "type": "type",
    "date_from": "created_at__gte",
    "date_to": "created_at__lte",
}

def create_company_transaction(dto_data: CreateCompanyTransactionDTO) -> Tuple[LedgerEntry, CompanyTransactionDetails]:
    # Check that sender and receiver exists
    sender = CompanyRepository.get_by_external_id(dto_data.sender_company_id)
    receiver = CompanyRepository.get_by_external_id(dto_data.receiver_company_id)

    if sender is None or receiver is None:
        raise CompanyNotFoundError(f"Company with external_guid {dto_data.sender_company_id} not found")
    
    if dto_data.amount > sender.balance:
        raise CompanyNotEnoughFundsError(f"Sender {sender.name} does not have enough funds to complete the requested transaction")

    # Check that sender has enough balance
    newLedgerEntry = LedgerEntry(
        amount = dto_data.amount,
        receiver_company_id = dto_data.receiver_company_id
    )
    newCompanyTransactionDetails = CompanyTransactionDetails(
        sender_company_id = dto_data.sender_company_id
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
    receiver = CompanyRepository.get_by_external_id(dto_data.receiver_company_id)

    if receiver is None:
        raise CompanyNotFoundError(f"Company with external_guid {dto_data.receiver_company_id} not found")

    # Check that sender has enough balance
    newLedgerEntry = LedgerEntry(
        amount = dto_data.amount,
        receiver_company_id = receiver.company_id
    )
    newCheckTransactionDetails = CheckTransactionDetails(
        sender_authority = dto_data.sender_authority
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
    transaction = LedgerEntryRepository.get_company_transaction_by_external_id(external_guid);
    if transaction is None:
        raise LedgerEntryNotFoundError(f"Company with external_guid {external_guid} not found")
    return transaction

def get_check_transaction_by_external_guid(external_guid: str):
    transaction = LedgerEntryRepository.get_check_transaction_by_external_id(external_guid);
    if transaction is None:
        raise LedgerEntryNotFoundError(f"Company with external_guid {external_guid} not found")
    return transaction

def can_claim(company, cooldown_hours: int = 1) -> bool:
    if not company.last_trygd_claim:
        return True

    # treat the naive timestamp as UTC
    last_claim_utc = company.last_trygd_claim.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    cooldown_period = timedelta(hours=cooldown_hours)

    return (now - last_claim_utc) >= cooldown_period

def minutes_until_next_claim(company, cooldown_hours: int = 1) -> int:
    if not company.last_trygd_claim:
        return 0

    # Treat the naive timestamp as UTC
    last_claim_utc = company.last_trygd_claim.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    cooldown_period = timedelta(hours=cooldown_hours)
    next_allowed = last_claim_utc + cooldown_period

    remaining = max(next_allowed - now, timedelta(0))
    return int(remaining.total_seconds() // 60)

def company_claim_cash(external_guid: str):
    from services.CompanyService import get_company_by_external_guid    # Lazy import circular dependency fix, TODO: refactor
    
    company = get_company_by_external_guid(external_guid);
    if company is None:
        raise CompanyNotFoundError(f"Company with external_guid {external_guid} not found")
    
    if not can_claim(company):
        raise ClaimCooldownActiveError(
            f"Claim is on cooldown for {company.name}. Please wait {minutes_until_next_claim(company)} minute(s) before trying again.",
            minutes_until_next_claim(company)
                                       )
    persisted_ledger, persisted_tx = create_check_transaction(
        CreateCheckTransactionDTO(
            amount = company.trygd_amount,
            receiver_company_id = company.external_id,
            sender_authority = settings.default_trygd_authority
        )
    )
    # company.balance += persisted_ledger.amount;
    company.last_trygd_claim = datetime.now(UTC)
    CompanyRepository.update(company);

    return persisted_ledger, persisted_tx

def query_ledger_entries(filters: dict, limit: int | None = None):
        if not filters:
            raise InvalidQueryError("At least one filter must be provided")

        unknown_keys = [k for k in filters if k not in ALLOWED_QUERY_FILTERS]
        if unknown_keys:
            raise InvalidQueryError(f"Invalid filter(s): {', '.join(unknown_keys)}")

        normalized = {ALLOWED_QUERY_FILTERS[k]: v for k, v in filters.items()}
        entries = LedgerEntryRepository.query_ledger_entries(normalized, limit=limit)

        if not entries:
            raise LedgerEntryNotFoundError("No ledger entries found with the provided filters.")

        return entries