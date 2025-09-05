from models.Company import Company
from infrastructure.db.db import db

class CompanyRepository:

    @staticmethod
    def get_by_id(company_id: int):
        return db.session.get(Company, company_id)
    @staticmethod
    def get_by_external_id(external_id: str):
        return db.session.query(Company).filter_by(external_id=external_id).first()
    @staticmethod
    def get_by_name(name: str):
        return db.session.query(Company).filter_by(name=name).first()
    @staticmethod
    def get_by_owner_id(owner_id: int):
        return db.session.query(Company).filter_by(owner=owner_id).first()
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
    def update(company: Company):
        db.session.add(company)  # SQLAlchemy will track changes
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
