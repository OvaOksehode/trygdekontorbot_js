import logging
from infrastructure.repositories.CompanyRepository import CompanyRepository

def create_company(company_data):
    if CompanyRepository.get_by_name(company_data['name']) is not None:
        logging.warning(f"Cant create new company with name {company_data['name']} because a company with that name already exists")
        return False
    return CompanyRepository.create(company_data)