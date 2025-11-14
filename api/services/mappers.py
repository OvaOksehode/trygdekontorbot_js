# services/mappers.py
from models.CheckTransactionDetailsViewModel import CheckTransactionDetailsViewModel
from models.CheckTransactionDetails import CheckTransactionDetails
from models.CompanyTransactionDetails import CompanyTransactionDetails
from models.LedgerEntry import LedgerEntry
from models.CompanyTransactionDetailsViewModel import CompanyTransactionDetailsViewModel
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
    return CompanyTransactionDetailsViewModel(
        external_id=ledgerEntry.external_id,
        amount=ledgerEntry.amount,
        created_at=ledgerEntry.created_at,
        receiver_company_id=ledgerEntry.receiver_company_id,
        sender_company_id=companyTransaction.sender_company_id
    )

def check_transaction_to_viewmodel(ledgerEntry: LedgerEntry, checkTransaction: CheckTransactionDetails):
    return CheckTransactionDetailsViewModel(
        external_id=ledgerEntry.external_id,
        amount=ledgerEntry.amount,
        created_at=ledgerEntry.created_at,
        receiver_company_id=ledgerEntry.receiver.external_id,
        sender_authority=checkTransaction.sender_authority
    )