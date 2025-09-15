class CompanyAlreadyExistsError(Exception):
    """Raised when trying to create a company that already exists."""
    pass

class CompanyNotFoundError(Exception):
    """Raised when trying to get a company that does not exist."""
    pass

class LedgerEntryNotFoundError(Exception):
    """Raised when trying to get a ledger entry that does not exist."""
    pass

class CompanyNotEnoughFundsError(Exception):
    """Raised when a company is trying to send more money than it has."""
    pass

class InvalidUpdateError(Exception):
    """Raised when trying to update a company with invalid data."""
    pass

class OwnerAlreadyHasCompanyError(Exception):
    """Raised when trying to create a company for an owner that already has a company."""
    pass

class InvalidTransactionAmountError(Exception):
    """Raised when trying to create a transaction with an invalid amount."""
    pass