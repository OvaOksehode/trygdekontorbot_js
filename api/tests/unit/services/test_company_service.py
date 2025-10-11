import pytest
from unittest.mock import patch, MagicMock

from infrastructure.repositories.CompanyRepository import CompanyRepository
from services.CompanyService import ALLOWED_QUERY_FILTERS, query_companies
from models.Exceptions import CompanyNotFoundError, InvalidQueryError

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
        mock_query.return_value = [mock_company]

        filters = {"name": "TestCompany"}
        result = query_companies(filters)

        normalized_filters = {ALLOWED_QUERY_FILTERS["name"]: "TestCompany"}
        # Updated to include search=None
        mock_query.assert_called_once_with(normalized_filters)
        assert result == [mock_company]

def test_query_companies_normalizes_filters():
    # Ensure normalization of filters
    filters = {"name": "TestCompany", "ownerId": "123"}

    normalized_filters = {ALLOWED_QUERY_FILTERS[k]: v for k, v in filters.items()}

    with patch.object(CompanyRepository, 'query_companies', return_value=[MagicMock()]) as mock_query:
        result = query_companies(filters)
        # Updated to include search=None
        mock_query.assert_called_once_with(normalized_filters)
        assert len(result) == 1

@patch.object(CompanyRepository, "query_companies")
def test_query_companies_with_search(mock_query, app):
    """Test that search parameter filters the returned companies in-memory."""
    with app.app_context():
        # Dummy objects with real .name strings
        class DummyCompany:
            def __init__(self, name):
                self.name = name

        company1 = DummyCompany("AwesomeCompany")
        company2 = DummyCompany("OtherCompany")
        mock_query.return_value = [company1, company2]

        filters = {"ownerId": "123", "s": "Awesome%"}
        result = query_companies(filters)

        # Repository should be called ONLY with normalized filters
        normalized_filters = {ALLOWED_QUERY_FILTERS["ownerId"]: "123"}
        mock_query.assert_called_once_with(normalized_filters)

        # Search should filter in Python
        assert result == [company1]