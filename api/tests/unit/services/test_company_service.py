import pytest
from unittest.mock import patch, MagicMock

from domain.models.Company import Company
from domain.models.CreateCompanyDTO import CreateCompanyDTO
from infrastructure.repositories.CompanyRepository import CompanyRepository
from services.CompanyService import ALLOWED_QUERY_FILTERS, create_company, query_companies
from domain.models.Exceptions import CompanyNotFoundError, InvalidQueryError

@pytest.fixture
def sample_dto():
    return CreateCompanyDTO(name="TestCo", owner_id=123)

def test_create_company_success(sample_dto):
    mock_company = Company(name="TestCo", owner_id=123, external_id="uuid123")

    with patch("services.CompanyService.CompanyRepository.get_by_owner_id", return_value=None), \
         patch("services.CompanyService.CompanyRepository.get_by_name", return_value=None), \
         patch("services.CompanyService.CompanyRepository.create", return_value=mock_company), \
         patch("services.CompanyService.create_check_transaction") as mock_check:

        result = create_company(sample_dto)

        assert result == mock_company
        mock_check.assert_called_once()
        assert result.name == "TestCo"
        assert result.owner_id == 123

def test_query_companies_no_filters():
    with pytest.raises(InvalidQueryError) as exc_info:
        query_companies({})
    assert "At least one filter must be provided" in str(exc_info.value)

def test_query_companies_invalid_filter():
    filters = {"invalid_key": "value"}
    with pytest.raises(InvalidQueryError) as exc_info:
        query_companies(filters)
    assert "Invalid filter(s): invalid_key" in str(exc_info.value)


@patch.object(CompanyRepository, 'query_companies')
def test_query_companies_no_results(mock_query):
    mock_query.return_value = []
    filters = {"name": "TestCompany"}
    
    with pytest.raises(CompanyNotFoundError) as exc_info:
        query_companies(filters)
    assert "No companies found" in str(exc_info.value)
    mock_query.assert_called_once()

@patch.object(CompanyRepository, 'query_companies')
def test_query_companies_success(mock_query, app):
    with app.app_context():
        mock_company = MagicMock()
        mock_company.deleted_at = None  # ✅ simulate active company
        mock_company.name = "TestCompany"

        mock_query.return_value = [mock_company]

        filters = {"name": "TestCompany"}
        result = query_companies(filters)

        assert result == [mock_company]
        mock_query.assert_called_once()

@patch.object(CompanyRepository, 'query_companies')
def test_query_companies_excludes_deleted(mock_query, app):
    with app.app_context():
        deleted_company = MagicMock()
        deleted_company.deleted_at = "2025-10-05T12:00:00"  # simulate soft delete
        mock_query.return_value = [deleted_company]

        filters = {"name": "DeletedCo"}

        with pytest.raises(CompanyNotFoundError):
            query_companies(filters)

# ✅ 1. Normalization test
def test_query_companies_normalizes_filters():
    filters = {"name": "TestCompany", "ownerId": "123"}
    normalized_filters = {ALLOWED_QUERY_FILTERS[k]: v for k, v in filters.items()}

    mock_company = MagicMock()
    mock_company.deleted_at = None  # ✅ active company

    with patch.object(CompanyRepository, 'query_companies', return_value=[mock_company]) as mock_query:
        result = query_companies(filters)

        mock_query.assert_called_once_with(normalized_filters)
        assert len(result) == 1
        assert result[0] == mock_company


# ✅ 2. Search filtering test
@patch.object(CompanyRepository, "query_companies")
def test_query_companies_with_search(mock_query, app):
    """Test that search parameter filters the returned companies in-memory."""
    with app.app_context():
        class DummyCompany:
            def __init__(self, name):
                self.name = name
                self.deleted_at = None  # ✅ must be None for inclusion

        company1 = DummyCompany("AwesomeCompany")
        company2 = DummyCompany("OtherCompany")
        mock_query.return_value = [company1, company2]

        filters = {"ownerId": "123", "s": "Awesome%"}
        result = query_companies(filters)

        normalized_filters = {ALLOWED_QUERY_FILTERS["ownerId"]: "123"}
        mock_query.assert_called_once_with(normalized_filters)

        # ✅ Only AwesomeCompany should remain after Python-level search filtering
        assert result == [company1]