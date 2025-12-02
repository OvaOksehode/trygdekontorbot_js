from domain.models.LedgerEntry import LedgerEntry
from domain.models.CreateLedgerEntryDTO import CreateLedgerEntryDTO
from infrastructure.repositories.LedgerEntryRepository import LedgerEntryRepository
from domain.models.CheckTransactionDetails import CheckTransactionDetails
from domain.models.Exceptions import CompanyNotFoundError
from infrastructure.repositories.CompanyRepository import CompanyRepository
from domain.factories.LedgerEntryFactory import LedgerEntryFactory


@LedgerEntryFactory.register("checkTransaction")
def create_check_transaction(dto: CreateLedgerEntryDTO) -> LedgerEntry:
    receiver = CompanyRepository.get_by_external_id(dto.receiver_company_id)

    if receiver is None:
        raise CompanyNotFoundError(
            f"Company with external_id {dto.receiver_company_id} not found"
        )

    tx = CheckTransactionDetails(
        amount=dto.amount,
        receiver_company_id=receiver.company_id,
        sender_authority=dto.sender_authority
    )

    persisted_tx = LedgerEntryRepository.add(tx)

    receiver.balance += dto.amount
    CompanyRepository.update(receiver)

    return persisted_tx