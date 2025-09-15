from models import CreateCompanyDTO
from models.Exceptions import CompanyAlreadyExistsError, CompanyNotFoundError, InvalidUpdateError, OwnerAlreadyHasCompanyError
from infrastructure.repositories.CompanyRepository import CompanyRepository

def create_company(company_data: CreateCompanyDTO):
    if CompanyRepository.get_by_owner_id(company_data['owner']) is not None:
        raise OwnerAlreadyHasCompanyError(f"Owner with id {company_data['owner']} already has a company")
    if CompanyRepository.get_by_name(company_data['name']) is not None:
        raise CompanyAlreadyExistsError(f"Company with name {company_data['name']} already exists")
    return CompanyRepository.create(company_data) # Should get turned into domain model before this

def get_company_by_external_guid(external_guid: str):
    company = CompanyRepository.get_by_external_id(external_guid);
    if company is None:
        raise CompanyNotFoundError(f"Company with external_guid {external_guid} not found")
    return company

def update_company(external_guid, updateDto):
    company = CompanyRepository.get_by_external_id(external_guid);
    if company is None:
        raise CompanyNotFoundError(f"Company with external_guid {external_guid} not found")
    if CompanyRepository.get_by_name(updateDto.name) is not None:
        raise CompanyAlreadyExistsError(f"Company with name {updateDto.name} already exists")
    company.name = updateDto.name
    return CompanyRepository.update(company)

def delete_company(external_guid):
    company = CompanyRepository.get_by_external_id(external_guid);
    if company is None:
        raise CompanyNotFoundError(f"Company with external_guid {external_guid} not found")
    CompanyRepository.delete(company.id)