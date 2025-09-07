import logging
import pytest
from datetime import date
from app_factory.create_app import create_app
from infrastructure.db.db_context import db
from infrastructure.logging.logging_config import setup_logging
from infrastructure.repositories.CompanyRepository import CompanyRepository

@pytest.fixture(scope="session", autouse=True)
def init_logging():
    setup_logging()

def ensure_test_env():
    from config import Settings
    settings = Settings()
    assert settings.environment == "testing", \
        f"DANGER: Tests can only run in 'testing' environment! Current: '{settings.environment}'"

@pytest.fixture(scope="module")
def app():
    logger = logging.getLogger(__name__)
    ensure_test_env()
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope="function")
def test_client(app):
    with app.app_context():
        yield app.test_client()
        db.session.rollback()
        db.session.remove()

def get_valid_company_data(**overrides):
    """Returnerer et komplett gyldig company-data-sett som kan tilpasses med overrides."""
    data = {
        'name': 'TestCompany',
        'birth_date': date(1990, 1, 1),
        'experience_in_years': 5,
        'email': 'test@example.com',
    }
    data.update(overrides)
    return data

def test_create_and_get(test_client):
    with test_client.application.app_context():
        data = get_valid_company_data(email='get@example.com')
        company = CompanyRepository.create(data)
        fetched = CompanyRepository.get_by_id(company.id)
        assert fetched is not None
        assert fetched.name == data['name']

def test_update(test_client):
    with test_client.application.app_context():
        data = get_valid_company_data(email='update@example.com', name='OldName')
        company = CompanyRepository.create(data)

        CompanyRepository.update(company.id, {'name': 'NewName'})
        updated = CompanyRepository.get_by_id(company.id)
        assert updated.name == 'NewName'

def test_delete(test_client):
    with test_client.application.app_context():
        data = get_valid_company_data(email='delete@example.com', name='DeleteMe')
        company = CompanyRepository.create(data)

        CompanyRepository.delete(company.id)
        deleted = CompanyRepository.get_by_id(company.id)
        assert deleted is None

def test_get_all(test_client):
    with test_client.application.app_context():
        CompanyRepository.create(get_valid_company_data(name='Company1', email='c1@example.com'))
        CompanyRepository.create(get_valid_company_data(name='Company2', email='c2@example.com'))

        companies = CompanyRepository.get_all()
        names = [c.name for c in companies]
        assert 'Company1' in names
        assert 'Company2' in names

def test_get_by_name(test_client):
    with test_client.application.app_context():
        data = get_valid_company_data(name='LookupCompany', email='lookup@example.com')
        created = CompanyRepository.create(data)

        fetched = CompanyRepository.get_by_name('LookupCompany')

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == 'LookupCompany'
