from flask import jsonify


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

class ClaimCooldownActiveError(Exception):
    """Raised when trying to claim cash while cooldown is active."""
    pass

from flask import jsonify
from collections import OrderedDict


import json
from flask import Response

class ErrorResponse(Exception):
    def __init__(self, error: str, description: str, status_code: int = 400, payload: dict | None = None):
        super().__init__(description)
        self.error = error
        self.description = description
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        # preserve order
        return {
            "error": self.error,
            "errorDescription": self.description,
            **self.payload
        }

    def to_flask_response(self):
        response_body = json.dumps(self.to_dict(), ensure_ascii=False)
        return Response(response_body, status=self.status_code, mimetype="application/json")
