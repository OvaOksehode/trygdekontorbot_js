class CompanyAlreadyExistsError(Exception):
    """Raised when trying to create a company that already exists."""
    pass

class CompanyNotFoundError(Exception):
    """Raised when trying to get a company that does not exist."""
    pass

class InvalidUpdateError(Exception):
    """Raised when trying to update a company with invalid data."""
    pass

class OwnerAlreadyHasCompanyError(Exception):
    """Raised when trying to create a company for an owner that already has a company."""
    pass