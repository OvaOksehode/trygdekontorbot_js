import uuid
from flask import Blueprint, Response, current_app, json, jsonify, request
from pydantic import TypeAdapter, ValidationError
from domain.models.CreateLedgerEntryDTO import CreateLedgerEntryDTO
from domain.models.LedgerEntryViewModel import LedgerEntryViewModel
from domain.models.CompanyTransactionDetailsViewModel import CompanyTransactionDetailsViewModel
from services import LedgerEntryService
import services.orchestrators.get_company_latest_transactions as orc
from domain.models.CompanyViewModel import CompanyViewModel
from domain.models.CompanyTransactionDetailsViewModel import CompanyTransactionDetailsViewModel
from services.mappers import check_transaction_to_viewmodel, company_to_viewmodel, company_transaction_to_viewmodel, ledger_entry_to_viewmodel
from services.LedgerEntryService import company_claim_cash, create_check_transaction, create_company_transaction, get_check_transaction_by_external_guid, get_company_transaction_by_external_guid, query_ledger_entries, query_ledger_entry_by_guid
from services.CompanyService import create_company, delete_company, get_company_by_external_guid, query_companies, update_company

from domain.models.Exceptions import CompanyAlreadyExistsError, CompanyNotEnoughFundsError, CompanyNotFoundError, InvalidTransactionAmountError, InvalidUpdateError, LedgerEntryNotFoundError, OwnerAlreadyHasCompanyError
from domain.models.CreateCheckTransactionDTO import CreateCheckTransactionDTO
from domain.models.CreateCompanyDTO import CreateCompanyDTO
from domain.models.CreateCompanyTransactionDTO import CreateCompanyTransactionDTO
from domain.models.UpdateCompanyDTO import UpdateCompanyDTO

api = Blueprint("api", __name__)

# POST localhost/api/company
# ✅ Create company
@api.route("/company", methods=["POST"])
def request_create_company():
    data = CreateCompanyDTO(**request.json)
    newCompany = create_company(data)
    return Response(
        CompanyViewModel.model_validate(newCompany).model_dump_json(by_alias=True),  # indent optional for readability
        status=201,
        mimetype="application/json"
    )

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
    
# GET localhost/api/company
# ↩ Get all companies, optionally filtered by query params
@api.route("/company", methods=["GET"])
def request_query_companies():

    # Extract query parameters that match the allowed ones
    filters = {
        key: value for key, value in request.args.items()
    }

    # 🔍 Fetch from your data layer (implement filtering in repository/service)
    companies = query_companies(filters)

    # Serialize to response models
    result = [
        CompanyViewModel.model_validate(company).model_dump(by_alias=True)
        for company in companies
    ]

    return jsonify(result), 200


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
    
# DELETE localhost/api/company/<external_guid>
# ❌ Delete company
@api.route("/company/<external_guid>", methods=["DELETE"])
def request_delete_company(external_guid: str):
    try:
        # validate UUID format
        external_guid = str(uuid.UUID(external_guid))
    except ValueError:
        return jsonify({"error": "Invalid external_guid"}), 400
    delete_company(external_guid)
    return Response(status=204)

# POST localhost/api/company-transaction
# ✅ Create company transaction
# TODO: unify ledgerEntry creation logic through one endpoint POST api/ledger-entry
@api.route("/company-transaction", methods=["POST"])
def request_create_company_transaction():
    # validate UUID format for sender and receiver
    # validate that amount is int not float or anything else (should be handled by pydantic, test this)
    try:
        dto_data = CreateCompanyTransactionDTO(**request.json)
        newTransaction = create_company_transaction(dto_data)
        return Response(
            CompanyTransactionDetailsViewModel.model_validate(newTransaction).model_dump_json(by_alias=True),  # indent optional for readability
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
        newLedgerEntry, newTransaction = query_ledger_entries(external_guid)
    except LedgerEntryNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    return Response(
            company_transaction_to_viewmodel(newLedgerEntry, newTransaction).model_dump_json(by_alias=True),  # indent optional for readability
            status=200,
            mimetype="application/json"
        )

# POST localhost/api/check-transaction
# ✅ Create check transaction
# TODO: unify ledgerEntry creation logic through one endpoint POST api/ledger-entry
@api.route("/check-transaction", methods=["POST"])
def request_create_check_transaction():
    # validate UUID format for sender and receiver
    # validate that amount is int not float or anything else (should be handled by pydantic, test this)
    try:
        dto_data = CreateCheckTransactionDTO(**request.json)
        newLedgerEntry, newTransaction = create_check_transaction(dto_data)
        return Response(
            check_transaction_to_viewmodel(newLedgerEntry, newTransaction).model_dump_json(by_alias=True),  # indent optional for readability
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

# GET localhost/api/check-transaction/<external_guid>
# ↩ Get check transaction
@api.route("/check-transaction/<external_guid>", methods=["GET"])
def request_get_check_transaction(external_guid: str):
    try:
        # validate UUID format
        external_guid = str(uuid.UUID(external_guid))
    except ValueError:
        return jsonify({"error": "Invalid external_guid"}), 400
    try:
        newLedgerEntry, newTransaction = orc.get_latest_transactions(external_guid)
    except LedgerEntryNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    return Response(
            check_transaction_to_viewmodel(newLedgerEntry, newTransaction).model_dump_json(by_alias=True),  # indent optional for readability
            status=200,
            mimetype="application/json"
        )
    
# POST localhost/api/company/<external_guid>/claim
# ✅ Claim cash with a given company
@api.route("/company/<external_guid>/claim", methods=["POST"])
def request_claim_cash(external_guid: str):
    try:
        # validate UUID format
        external_guid = str(uuid.UUID(external_guid))
    except ValueError:
        return jsonify({"error": "Invalid external_guid"}), 400
    try:
        newLedgerEntry, newTransaction = company_claim_cash(external_guid)
        return Response(
            check_transaction_to_viewmodel(newLedgerEntry, newTransaction).model_dump_json(by_alias=True),  # indent optional for readability
            status=201,
            mimetype="application/json"
        )
    except LedgerEntryNotFoundError as error:
        return jsonify({"error": str(error)}), 404
    
@api.route("/company/<company_uuid>/latest-transactions", methods=["GET"])
def get_latest_transactions(company_uuid: str):
    # Validate limit parameter
    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400

    # Step 1: orchestrator fetches latest ledger entries + subtype details
    try:
        entries_with_details = orc.get_latest_transactions(
            receiver_company_id=company_uuid,
            limit=limit
        )
    except LedgerEntryNotFoundError:
        return jsonify({"error": "No ledger entries found for this company"}), 404

    # Step 2: prepare response
    response = {
        "totalCount": len(entries_with_details),
        "checkTransactions": [],
        "companyTransactions": []
    }

    for entry, detail in entries_with_details:
        if detail is None:
            # Skip generic entries if you want; or include them in a "genericLedgerEntries" list
            continue
        elif hasattr(detail, "sender_authority"):  # CheckTransactionDetails
            response["checkTransactions"].append(
                check_transaction_to_viewmodel(entry, detail).model_dump(by_alias=True)
            )
        elif hasattr(detail, "receiver_company_uuid"):  # CompanyTransactionDetails
            response["companyTransactions"].append(
                company_transaction_to_viewmodel(entry, detail).model_dump(by_alias=True)
            )

    return jsonify(response), 200

@api.route("/ledger-entry", methods=["GET"])
def request_query_ledger_entries():

    filters = dict(request.args)
    entries = query_ledger_entries(filters)

    adapter = TypeAdapter(list[LedgerEntryViewModel])

    payload = adapter.dump_json(
        [LedgerEntryViewModel.model_validate(e) for e in entries],
        by_alias=True,
        exclude_none=True
    )

    return Response(
        payload,
        mimetype="application/json",
        status=200
    )

@api.route("/ledger-entry/<external_guid>", methods=["GET"])
def request_get_ledger_entry(external_guid: str):
    entry = query_ledger_entry_by_guid(external_guid)

    vm = LedgerEntryViewModel.model_validate(entry)
    # Use model_dump to get a dict and exclude None values
    payload = vm.model_dump_json(by_alias=True, exclude_none=True)

    # return jsonify(payload)
    # or:
    return Response(
        payload,
        mimetype="application/json",
        status=200
        )
    
# TODO: Finish centralized ledger entry creation with server layer class delegation (iykwim)
@api.route("/ledger-entry", methods=["POST"])
def request_create_ledger_entry():
    # 1️⃣ Parse the request into a DTO
    dto = CreateLedgerEntryDTO(**request.json)

    # 2️⃣ Delegate creation to the service layer
    entry = LedgerEntryService.create_ledger_entry(dto)

    # 3️⃣ Convert the domain object to a viewmodel for serialization
    vm = LedgerEntryViewModel.model_validate(entry)

    # 4️⃣ Serialize to JSON, excluding None values
    payload = vm.model_dump_json(by_alias=True, exclude_none=True)

    # 5️⃣ Return clean HTTP response
    return Response(payload, mimetype="application/json", status=201)