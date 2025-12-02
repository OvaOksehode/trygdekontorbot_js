from pydantic import ValidationError
from routes.api import api
from domain.models.Exceptions import ClaimCooldownActiveError, CompanyAlreadyExistsError, CompanyNotFoundError, ErrorResponse, InvalidQueryError, OwnerAlreadyHasCompanyError

@api.errorhandler(ValidationError)
def handle_validation_error(e):
    return ErrorResponse(
        error="validationError",
        description="Missing or invalid fields",
        status_code=400,
        payload={"details": e.errors()},
    ).to_flask_response()
    
@api.errorhandler(CompanyAlreadyExistsError)
def handle_validation_error(e):
    return ErrorResponse(
        error="companyAlreadyExistsError",
        description=str(e),
        status_code=409,
    ).to_flask_response()
    
@api.errorhandler(OwnerAlreadyHasCompanyError)
def handle_validation_error(e):
    return ErrorResponse(
        error="ownerAlreadyHasCompanyError",
        description=str(e),
        status_code=409,
    ).to_flask_response()
    
@api.errorhandler(CompanyNotFoundError)
def handle_validation_error(e):
    return ErrorResponse(
        error="companyNotFoundError",
        description=str(e),
        status_code=404,
    ).to_flask_response()

@api.errorhandler(InvalidQueryError)
def handle_validation_error(e):
    return ErrorResponse(
        error="invalidQueryError",
        description=str(e),
        status_code=400,
    ).to_flask_response()

@api.errorhandler(ClaimCooldownActiveError)
def handle_validation_error(e):
    return ErrorResponse(
        error="claimCooldownActiveError",
        description=str(e),
        status_code=400,
        payload={"cooldownRemainingMinutes": e.cooldown_remaining_minutes},
    ).to_flask_response()

@api.errorhandler(500)
def handle_internal_error(e):
    return ErrorResponse(
        error="internalServerError",
        description=str(e),
        status_code=500,
    ).to_flask_response()
    
