import uuid
from flask import Blueprint, Response, current_app, jsonify, request
from pydantic import ValidationError
from models.CompanyViewModel import CompanyViewModel
from models.CompanyTransactionViewModel import CompanyTransactionViewModel
from services.mappers import check_transaction_to_viewmodel, company_to_viewmodel, company_transaction_to_viewmodel
from services.LedgerEntryService import create_check_transaction, create_company_transaction, get_company_transaction_by_external_guid
from services.CompanyService import create_company, delete_company, get_company_by_external_guid, update_company

from models.Exceptions import CompanyAlreadyExistsError, CompanyNotEnoughFundsError, CompanyNotFoundError, InvalidTransactionAmountError, InvalidUpdateError, LedgerEntryNotFoundError, OwnerAlreadyHasCompanyError
from models.CreateCheckTransactionDTO import CreateCheckTransactionDTO
from models.CreateCompanyDTO import CreateCompanyDTO
from models.CreateCompanyTransactionDTO import CreateCompanyTransactionDTO
from models.UpdateCompanyDTO import UpdateCompanyDTO

api = Blueprint("api", __name__)

# POST localhost/api/company
# ✅ Create company
@api.route("/company", methods=["POST"])
def request_create_company():
    try:
        data = CreateCompanyDTO(**request.json)
        newCompany = create_company(data)
        return Response(
            CompanyViewModel.model_validate(newCompany).model_dump_json(by_alias=True),  # indent optional for readability
            status=201,
            mimetype="application/json"
        )
    except ValidationError as error:
        return jsonify(error.errors()), 400
    except CompanyAlreadyExistsError as error:
        return jsonify({"error": str(error)}), 409
    except OwnerAlreadyHasCompanyError as error:
        return jsonify({"error": str(error)}), 409
        
    # catch all other 4xx errors

# GET localhost/api/company/<external_guid>
# ↩ Get company
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

    return Response(
            CompanyViewModel.model_validate(company).model_dump_json(by_alias=True),  # indent optional for readability
            # company_to_viewmodel(company).model_dump_json(),  # indent optional for readability
            status=200,
            mimetype="application/json"
        )

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
        return Response(
            CompanyViewModel.model_validate(updated_company).model_dump_json(by_alias=True),  # indent optional for readability
            # company_to_viewmodel(updated_company).model_dump_json(),  # indent optional for readability
            status=200,
            mimetype="application/json"
        )

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

# POST localhost/api/company-transaction
# ✅ Create company transaction
@api.route("/company-transaction", methods=["POST"])
def request_create_company_transaction():
    # validate UUID format for sender and receiver
    # validate that amount is int not float or anything else (should be handled by pydantic, test this)
    try:
        dto_data = CreateCompanyTransactionDTO(**request.json)
        newLedgerEntry, newTransaction = create_company_transaction(dto_data)
        return Response(
            company_transaction_to_viewmodel(newLedgerEntry, newTransaction).model_dump_json(),  # indent optional for readability
            status=201,
            mimetype="application/json"
        )
    except ValidationError as error:
        return jsonify(error.errors()), 400
    except CompanyNotFoundError as error:
        return jsonify({"error": str(error)}), 404
    except InvalidTransactionAmountError as error:
        return jsonify({"error": str(error)}), 400
    except CompanyNotEnoughFundsError as error:
        return jsonify({"error": str(error)}), 400

# GET localhost/api/company-transaction/<external_guid>
# ↩ Get company transaction
@api.route("/company-transaction/<external_guid>", methods=["GET"])
def request_get_company_transaction(external_guid: str):
    try:
        # validate UUID format
        external_guid = str(uuid.UUID(external_guid))
    except ValueError:
        return jsonify({"error": "Invalid external_guid"}), 400
    try:
        newLedgerEntry, newTransaction = get_company_transaction_by_external_guid(external_guid)
    except LedgerEntryNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    return Response(
            company_transaction_to_viewmodel(newLedgerEntry, newTransaction).model_dump_json(),  # indent optional for readability
            status=201,
            mimetype="application/json"
        )

# POST localhost/api/check-transaction
# ✅ Create check transaction
@api.route("/check-transaction", methods=["POST"])
def request_create_check_transaction():
    # validate UUID format for sender and receiver
    # validate that amount is int not float or anything else (should be handled by pydantic, test this)
    try:
        dto_data = CreateCheckTransactionDTO(**request.json)
        newLedgerEntry, newTransaction = create_check_transaction(dto_data)
        return Response(
            check_transaction_to_viewmodel(newLedgerEntry, newTransaction).model_dump_json(),  # indent optional for readability
            status=201,
            mimetype="application/json"
        )
    except ValidationError as error:
        return jsonify(error.errors()), 400
    except CompanyNotFoundError as error:
        return jsonify({"error": str(error)}), 404
    except InvalidTransactionAmountError as error:
        return jsonify({"error": str(error)}), 400
    except CompanyNotEnoughFundsError as error:
        return jsonify({"error": str(error)}), 400

@api.errorhandler(500)
def handle_internal_error(e):
    current_app.logger.exception("Unexpected error in API")
    return jsonify({"error": "Internal server error"}), 500
