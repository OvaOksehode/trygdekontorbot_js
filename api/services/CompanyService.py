from infrastructure.repositories.CompanyRepository import CompanyRepository

def create_company(company_data):
    if CompanyRepository.get_by_id(company_data['id']) is not None:
        print("Company already exists")
        return False
    return CompanyRepository.create(company_data)

def update_company(company_data_updated):
    CompanyRepository.update()