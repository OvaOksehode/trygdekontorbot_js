from flask import Blueprint, current_app, jsonify, request
from services.mappers import company_to_viewmodel
from models.Exceptions import CompanyAlreadyExistsError
from models.CompanyViewModel import CompanyViewModel
from pydantic import ValidationError
from services.CompanyService import create_company

from models.CompanyDTO import CompanyDTO
api = Blueprint("api", __name__)


# Routes:
# Company:
# - Create user [ X ]
# abt creating users: Normal api clients should only be able to manage their own company, clients with special access should be able to manage multiple. Same goes for other resources' CRUD operations.
# - Read user   [  ]
# - Update user [  ]
# - Delete user [  ]
# - Claim trygd [  ]

# Transaction:
# - Create transaction  [  ]
# - Read transaction    [  ]
# - [Admin] spawn money [  ]

# POST localhost/api/company
# ✅ Create company
@api.route("/company", methods=["POST"])
def request_create_company():
    try:
        data = CompanyDTO(**request.json).model_dump()
        newCompany = create_company(data)
        return company_to_viewmodel(newCompany).model_dump_json(), 201
    except ValidationError as error:
        return jsonify(error.errors()), 400
    except CompanyAlreadyExistsError as error:
        return jsonify({"error": str(error)}), 409
    
@api.errorhandler(500)
def handle_internal_error(e):
    current_app.logger.exception("Unexpected error in API")
    return jsonify({"error": "Internal server error"}), 500