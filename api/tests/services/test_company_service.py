import pytest
from unittest.mock import patch, MagicMock

from services.CompanyService import create_company  # Adjust import path if needed

@pytest.fixture
def company_data():
    return {
        "name": "Acme Corp"
    }

def test_create_company_success(company_data):
    with patch("services.CompanyService.CompanyRepository") as mock_repo:
        # Simulate company does not exist yet
        mock_repo.get_by_name.return_value = None
        mock_repo.create.return_value = True

        result = create_company(company_data)

        mock_repo.get_by_name.assert_called_once_with("Acme Corp")
        mock_repo.create.assert_called_once_with(company_data)
        assert result is True

def test_create_company_duplicate_name(company_data):
    with patch("services.CompanyService.CompanyRepository") as mock_repo:
        # Simulate company already exists
        mock_repo.get_by_name.return_value = {"name": "Acme Corp"}

        result = create_company(company_data)

        mock_repo.get_by_name.assert_called_once_with("Acme Corp")
        mock_repo.create.assert_not_called()
        assert result is False
