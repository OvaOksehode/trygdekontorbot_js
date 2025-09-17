# services/mappers.py
from models.CheckTransactionDetailsViewModel import CheckTransactionViewModel
from models.CheckTransactionDetails import CheckTransactionDetails
from models.CompanyTransactionDetails import CompanyTransactionDetails
from models.LedgerEntry import LedgerEntry
from models.CompanyTransactionViewModel import CompanyTransactionViewModel
from models.CompanyViewModel import CompanyViewModel

def company_to_viewmodel(company):
    return CompanyViewModel(
        external_id=company.external_id,
        name=company.name,
        owner=company.owner,
        balance=company.balance,
        created_at=company.created_at,
        last_trygd_claim=company.last_trygd_claim,
    )

def company_transaction_to_viewmodel(ledgerEntry: LedgerEntry, companyTransaction: CompanyTransactionDetails):
    return CompanyTransactionViewModel(
        external_id=ledgerEntry.ExternalID,
        amount=ledgerEntry.Amount,
        created_at=ledgerEntry.CreatedAt,
        receiver_id=ledgerEntry.ReceiverCompanyID,
        from_company_id=companyTransaction.SenderCompanyID
    )

def check_transaction_to_viewmodel(ledgerEntry: LedgerEntry, checkTransaction: CheckTransactionDetails):
    return CheckTransactionViewModel(
        external_id=ledgerEntry.ExternalID,
        amount=ledgerEntry.Amount,
        created_at=ledgerEntry.CreatedAt,
        receiver_id=ledgerEntry.ReceiverCompanyID,
        from_authority=checkTransaction.SenderAuthority
    )