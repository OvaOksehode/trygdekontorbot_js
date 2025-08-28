# services/mappers.py
from models.CompanyViewModel import CompanyViewModel

def company_to_viewmodel(company):
    return CompanyViewModel(
        external_id=company.external_id,
        name=company.name,
        balance=company.balance,
        created_at=company.created_at,
        last_trygd_claim=company.last_trygd_claim,
    )
