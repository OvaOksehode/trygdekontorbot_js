from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from services.CompanyService import create_company, get_by_id

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
# - Create transaction  [ V ]
# - Read transaction    [  ]
# - [Admin] spawn money [  ]

# POST localhost/api/company
# ✅ Create company
@api.route("/company", methods=["POST"])
def request_create_company():
    try:
        data = CompanyDTO(**request.json).model_dump()
        create_company(data)
        return jsonify(data), 201
    except ValidationError as error:
        return jsonify(error.errors()), 400

# GET localhost/api/company/<company_guid>
# 📖 Read company by ID
@api.route("/company/<company_id>", methods=["GET"])
def request_get_company(company_id):
    company = get_by_id(company_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404
    return jsonify(company), 200


# ✏️ Update company by ID
@api.route("/company/<company_id>", methods=["PUT"])
def request_update_company(company_id):
    try:
        data = CompanyDTO(**request.json).model_dump()
        updated = update_company(company_id, data)
        if not updated:
            return jsonify({"error": "Company not found"}), 404
        return jsonify(updated), 200
    except ValidationError as error:
        return jsonify(error.errors()), 400


# ❌ Delete company by ID
@api.route("/company/<company_id>", methods=["DELETE"])
def request_delete_company(company_id):
    deleted = delete_company(company_id)
    if not deleted:
        return jsonify({"error": "Company not found"}), 404
    return jsonify({"message": "Company deleted"}), 200


# 💸 Claim trygd
@api.route("/company/<company_id>/claim-trygd", methods=["POST"])
def request_claim_trygd(company_id):
    try:
        result = claim_trygd(company_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ----------- Transaction Routes ----------- #

# ✅ Create transaction
@api.route("/transaction", methods=["POST"])
def request_create_transaction():
    try:
        data = TransactionDTO(**request.json).model_dump()
        create_transaction(data)
        return jsonify(data), 201
    except ValidationError as error:
        return jsonify(error.errors()), 400


# 📖 Read transaction by ID
@api.route("/transaction/<transaction_id>", methods=["GET"])
def request_get_transaction(transaction_id):
    tx = get_transaction(transaction_id)
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404
    return jsonify(tx), 200


# 🧙 Admin-only: Spawn money to a company
@api.route("/admin/spawn-money", methods=["POST"])
def request_spawn_money():
    try:
        company_id = request.json.get("company_id")
        amount = request.json.get("amount")
        if not company_id or not amount:
            return jsonify({"error": "Missing company_id or amount"}), 400
        result = spawn_money(company_id, int(amount))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400