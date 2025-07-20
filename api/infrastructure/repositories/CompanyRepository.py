from models.Company import Company
from infrastructure.db.db_context import db

class CompanyRepository:

    @staticmethod
    def get_by_id(company_id: int):
        return db.session.get(Company, company_id)

    @staticmethod
    def get_by_name(name: str):
        return db.session.query(Company).filter_by(name=name).first()

    @staticmethod
    def get_all():
        return db.session.query(Company).all()

    @staticmethod
    def create(company_data):
        company = Company(**company_data)
        db.session.add(company)
        db.session.commit()
        return company

    @staticmethod
    def update(company_id: int, update_data: dict):
        company = CompanyRepository.get_by_id(company_id)
        if not company:
            return None
        for key, value in update_data.items():
            setattr(company, key, value)
        db.session.commit()
        return company

    @staticmethod
    def delete(company_id: int):
        company = CompanyRepository.get_by_id(company_id)
        if not company:
            return False
        db.session.delete(company)
        db.session.commit()
        return True
