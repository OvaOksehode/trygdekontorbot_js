from models.Exceptions import CompanyAlreadyExistsError
from infrastructure.repositories.CompanyRepository import CompanyRepository

def create_company(company_data):
    if CompanyRepository.get_by_name(company_data['name']) is not None:
        raise CompanyAlreadyExistsError(f"Company with name {company_data['name']} already exists")
    return CompanyRepository.create(company_data)

def get_company_by_external_guid(external_guid):
    return CompanyRepository.get_by_external_id(external_guid)

def update_company(company_data_updated):
    CompanyRepository.update()