import uuid
from flask import Blueprint, Response, current_app, jsonify, request
from models import UpdateCompanyDTO
from services.mappers import company_to_viewmodel
from models.Exceptions import CompanyAlreadyExistsError, CompanyNotFoundError, InvalidUpdateError, OwnerAlreadyHasCompanyError
from pydantic import ValidationError
from services.CompanyService import create_company, delete_company, get_company_by_external_guid, update_company

from models.CreateCompanyDTO import CreateCompanyDTO
from models.UpdateCompanyDTO import UpdateCompanyDTO
api = Blueprint("api", __name__)

# POST localhost/api/company
# ✅ Create company
@api.route("/company", methods=["POST"])
def request_create_company():
    try:
        data = CreateCompanyDTO(**request.json).model_dump()
        newCompany = create_company(data)
        return company_to_viewmodel(newCompany).model_dump_json(), 201
    except ValidationError as error:
        return jsonify(error.errors()), 400
    except CompanyAlreadyExistsError as error:
        return jsonify({"error": str(error)}), 409
    except OwnerAlreadyHasCompanyError as error:
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
    try:
        company = get_company_by_external_guid(external_guid)
    except CompanyNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    return company_to_viewmodel(company).model_dump_json(), 200

# PATCH localhost/api/company/<external_guid>
# 🔄 Update company info
@api.route("/company/<external_guid>", methods=["PATCH"])
def request_update_company(external_guid: str):
    if not request.json:    # Ensure request body is not empty
        return jsonify({"error": "Request body cannot be empty"}), 400
    try:
        # validate UUID format
        external_guid = str(uuid.UUID(external_guid))
    except ValueError:
        return jsonify({"error": "Invalid external_guid"}), 400
    try:

        # ✅ Parse and validate request JSON using the Update DTO
        dto = UpdateCompanyDTO(**request.json)

        # ✅ Call service layer to apply updates
        updated_company = update_company(external_guid, dto)

        # ✅ Convert to viewmodel for response
        return company_to_viewmodel(updated_company).model_dump_json(), 200

    except ValidationError as error:
        return jsonify(error.errors()), 400
    except CompanyNotFoundError as error:
        return jsonify({"error": str(error)}), 404
    except CompanyAlreadyExistsError as error:
        return jsonify({"error": str(error)}), 409
    
# DELETE localhost/api/company/<external_guid>
# ❌ Delete company
@api.route("/company/<external_guid>", methods=["DELETE"])
def request_delete_company(external_guid: str):
    try:
        # validate UUID format
        external_guid = str(uuid.UUID(external_guid))
    except ValueError:
        return jsonify({"error": "Invalid external_guid"}), 400
    try:
        delete_company(external_guid)
        return Response(status=204)
    except CompanyNotFoundError as error:
        return jsonify({"error": str(error)}), 404

@api.errorhandler(500)
def handle_internal_error(e):
    current_app.logger.exception("Unexpected error in API")
    return jsonify({"error": "Internal server error"}), 500
