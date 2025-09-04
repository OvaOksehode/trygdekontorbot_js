class CompanyAlreadyExistsError(Exception):
    """Raised when trying to create a company that already exists."""
    pass

class OwnerAlreadyHasCompanyError(Exception):
    """Raised when trying to create a company for an owner that already has a company."""
    pass