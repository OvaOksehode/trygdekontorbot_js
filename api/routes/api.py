import uuid
from flask import Blueprint, current_app, jsonify, request
from services.mappers import company_to_viewmodel
from models.Exceptions import CompanyAlreadyExistsError
from pydantic import ValidationError
from services.CompanyService import create_company, get_company_by_external_guid

from models.CompanyDTO import CompanyDTO
api = Blueprint("api", __name__)


# Routes:
# Company:
# - Create user [ X ]
# abt creating users: Normal api clients should only be able to manage their own company, clients with special access should be able to manage multiple. Same goes for other resources' CRUD operations.
# - Read user   [ X ]
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
        
    # catch all other 4xx errors

# GET localhost/api/company/<external_guid>
# ⏎ Get company
@api.route("/company/<external_guid>", methods=["GET"])
def request_get_company(external_guid: str):
    try:
        # validate UUID format
        external_guid = str(uuid.UUID(external_guid))
    except ValueError:
        return jsonify({"error": "Invalid external_guid"}), 400

    company = get_company_by_external_guid(external_guid)
    if not company:
        return jsonify({"error": f"Company with external_guid {external_guid} not found"}), 404

    return company_to_viewmodel(company).model_dump_json(), 200


@api.errorhandler(500)
def handle_internal_error(e):
    current_app.logger.exception("Unexpected error in API")
    return jsonify({"error": "Internal server error"}), 500
