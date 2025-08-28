from flask import Blueprint, jsonify, request
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
@api.route("/company", methods=["GET"])
def request_create_company():
    try:
        data = CompanyDTO(**request.json).model_dump()
        create_company(data)
        return jsonify(data), 201
    except ValidationError as error:
        return jsonify(error.errors()), 400