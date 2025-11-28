from datetime import UTC, datetime, timedelta, timezone
from typing import Tuple
from domain.factories.LedgerEntryFactory import LedgerEntryFactory
from domain.models.CheckTransactionDetails import CheckTransactionDetails
from domain.models.CreateCheckTransactionDTO import CreateCheckTransactionDTO
from domain.models.CreateLedgerEntryDTO import CreateLedgerEntryDTO
from domain.models.Exceptions import ClaimCooldownActiveError, CompanyNotEnoughFundsError, CompanyNotFoundError, InvalidQueryError, LedgerEntryNotFoundError
from infrastructure.repositories.CompanyRepository import CompanyRepository
from infrastructure.repositories.LedgerEntryRepository import LedgerEntryRepository
from domain.models.CreateCompanyTransactionDTO import CreateCompanyTransactionDTO
from domain.models.CompanyTransactionDetails import CompanyTransactionDetails
from domain.models.LedgerEntry import LedgerEntry
from config import settings


ALLOWED_QUERY_FILTERS = {
    "receiverCompanyId": "receiver_company_uuid",
    "senderCompanyId": "sender_company_uuid",
    "receiverCompanyName": "receiver_company.name",
    "senderCompanyName": "sender_company.name",
    "type": "type",
    "date_from": "created_at__gte",
    "date_to": "created_at__lte",
}


def create_company_transaction(dto_data: CreateCompanyTransactionDTO) -> CompanyTransactionDetails:
    # Check sender and receiver exist
    sender = CompanyRepository.get_by_external_id(dto_data.sender_company_id)
    receiver = CompanyRepository.get_by_external_id(dto_data.receiver_company_id)

    if sender is None or receiver is None:
        raise CompanyNotFoundError("Sender or receiver not found")

    if dto_data.amount > sender.balance:
        raise CompanyNotEnoughFundsError(
            f"Sender {sender.name} does not have enough funds"
        )

    # Create a single polymorphic object (NO separate LedgerEntry)
    tx = CompanyTransactionDetails(
        amount=dto_data.amount,
        receiver_company_id=receiver.company_id,
        sender_company_id=sender.company_id
    )

    # Persist via repo
    persisted_tx = LedgerEntryRepository.createCompanyTransaction(tx)

    # Update balances
    sender.balance -= dto_data.amount
    receiver.balance += dto_data.amount

    CompanyRepository.update(sender)
    CompanyRepository.update(receiver)

    return persisted_tx

def create_check_transaction(dto_data: CreateCheckTransactionDTO) -> CheckTransactionDetails:
    # 1️⃣ Ensure receiver exists
    receiver = CompanyRepository.get_by_external_id(dto_data.receiver_company_id)
    if receiver is None:
        raise CompanyNotFoundError(
            f"Company with external_guid {dto_data.receiver_company_id} not found"
        )

    # 2️⃣ Create the polymorphic subclass instance
    check_tx = CheckTransactionDetails(
        amount=dto_data.amount,                       # base LedgerEntry field
        receiver_company_id=receiver.company_id,      # base LedgerEntry field
        sender_authority=dto_data.sender_authority    # subclass-specific field
    )

    LedgerEntryRepository.createCheckTransaction(check_tx)

    # 4️⃣ Update receiver balance
    receiver.balance += dto_data.amount
    CompanyRepository.update(receiver)

    return check_tx

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

def query_ledger_entries(filters: dict) -> list[LedgerEntry]:
    if not filters:
        raise InvalidQueryError("At least one filter must be provided")

    unknown_keys = [k for k in filters if k not in ALLOWED_QUERY_FILTERS]
    if unknown_keys:
        raise InvalidQueryError(f"Invalid filter(s): {', '.join(unknown_keys)}")

    normalized_filters = {
        ALLOWED_QUERY_FILTERS[k]: v for k, v in filters.items()
    }

    entries = LedgerEntryRepository.query_ledger_entries(normalized_filters)

    if not entries:
        raise LedgerEntryNotFoundError("No ledger entries found.")

    return entries
    
def query_ledger_entry_by_guid(guid: str) -> LedgerEntry:
    result = LedgerEntryRepository.get_by_external_id(guid)
    return result

def create_ledger_entry(dto: CreateLedgerEntryDTO) -> LedgerEntry:
        return LedgerEntryFactory.create(dto)