# services/mappers.py
from models.LedgerEntryViewModel import LedgerEntryViewModel
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
    
def ledger_entry_to_viewmodel(ledger: LedgerEntry):
    # Base fields
    base_data = {
        "external_id": ledger.external_id,
        "amount": ledger.amount,
        "created_at": ledger.created_at,
        "receiver_company_id": ledger.receiver_company_id,
        "type": ledger.type,
    }

    details_data = {}
    if ledger.type == "company_transaction_details" and getattr(ledger, "companytransactiondetails", None):
        details_obj = ledger.companytransactiondetails
        details_data = CompanyTransactionDetailsViewModel.model_validate({
            "sender_company_id": details_obj.sender_company_id,
            # add other detail fields here
        }).model_dump(by_alias=True)

    elif ledger.type == "check_transaction_details" and getattr(ledger, "checktransactiondetails", None):
        details_obj = ledger.checktransactiondetails
        details_data = CheckTransactionDetailsViewModel.model_validate({
            "check_number": details_obj.check_number,
            # add other detail fields here
        }).model_dump(by_alias=True)

    return {
        "LedgerEntryViewModel": base_data,
        "details": details_data
    }
