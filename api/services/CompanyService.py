from datetime import UTC, datetime

from services.LedgerEntryService import create_check_transaction
from models.Company import Company
from models.CreateCheckTransactionDTO import CreateCheckTransactionDTO
from models.CreateCompanyDTO import CreateCompanyDTO
from models.Exceptions import CompanyAlreadyExistsError, CompanyNotFoundError, InvalidUpdateError, OwnerAlreadyHasCompanyError
from infrastructure.repositories.CompanyRepository import CompanyRepository

from config import settings

def create_company(company_data: CreateCompanyDTO)-> Company:
    # 1️⃣ Validate uniqueness
    company_by_owner = CompanyRepository.get_by_owner_id(company_data.owner_id)
    if company_by_owner and company_by_owner.deleted_at is None:
        raise OwnerAlreadyHasCompanyError(f"Owner {company_by_owner.owner_id} already has a company")

    company_by_name = CompanyRepository.get_by_name(company_data.name)
    if company_by_name:
        raise CompanyAlreadyExistsError(f"Company {company_data.name} already exists or has existed in the past")

    # 2️⃣ Convert DTO -> ORM model
    company_model = Company(
        name=company_data.name,
        owner_id=company_data.owner_id,
        balance=0  # optional default; starter cash will be added separately
    )

    # 3️⃣ Persist the company
    new_company = CompanyRepository.create(company_model)

    # 4️⃣ Give starter cash
    starter_cash_dto = CreateCheckTransactionDTO(
        amount=settings.starter_cash,
        receiver_company_id=new_company.external_id,
        sender_authority=settings.default_check_authority
    )
    create_check_transaction(starter_cash_dto)

    return new_company

def get_company_by_external_guid(external_guid: str):
    company = CompanyRepository.get_by_external_id(external_guid);
    if company is None or company.deleted_at is not None:
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
    company = get_company_by_external_guid(external_guid);
    company.deleted_at = datetime.now(UTC)

    CompanyRepository.update(company)