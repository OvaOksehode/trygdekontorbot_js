
from infrastructure.repositories.LedgerEntryRepository import LedgerEntryRepository
from domain.models.CompanyTransactionDetails import CompanyTransactionDetails
from domain.models.Exceptions import CompanyNotFoundError
from infrastructure.repositories.CompanyRepository import CompanyRepository
from domain.factories.LedgerEntryFactory import LedgerEntryFactory


@LedgerEntryFactory.register("companyTransaction")
def create_company_transaction(dto):
    sender = CompanyRepository.get_by_external_id(dto.sender_company_id)
    receiver = CompanyRepository.get_by_external_id(dto.receiver_company_id)

    if sender is None or receiver is None:
        raise CompanyNotFoundError("Sender or receiver not found")

    # if dto.amount > sender.balance:
    #     raise CompanyNotEnoughFundsError(
    #         f"Sender {sender.name} does not have enough funds"
    #     )

    tx = CompanyTransactionDetails(
        amount=dto.amount,
        sender_company_id=sender.company_id,
        receiver_company_id=receiver.company_id
    )

    persisted_tx = LedgerEntryRepository.add(tx)

    # Apply side effects
    sender.balance -= dto.amount
    receiver.balance += dto.amount
    CompanyRepository.update(sender)
    CompanyRepository.update(receiver)

    return persisted_tx