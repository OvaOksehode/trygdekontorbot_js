from flask import Blueprint, jsonify, redirect, request
from pydantic import ValidationError
from services.CompanyService import create_company
from auth.authorization import enforce_policy
import requests

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
# - Create transaction  [ V ]
# - Read transaction    [  ]
# - [Admin] spawn money [  ]

@api.route("/login", methods=["GET"])
def request_login():
    keycloak_auth_url = (
        "http//localhost:8080/realms/Trygdekontorbot/protocol/openid-connect/auth"
        "?client_id=trygdekontorbot-api"
        "&redirect_uri=http://localhost:5000/api/auth/callback"
        "&response_type=code"
        "&scope=openid"
    )
    return redirect(keycloak_auth_url)

@api.route("/auth/callback")
def auth_callback():
    code = request.args.get("code")

    token_url = "http://localhost:8080/realms/Trygdekontorbot/protocol/openid-connect/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:5000/auth/callback",
        "client_id": "trygdekontorbot-api",
        "client_secret": "u4KQdy5za79HJ82VvQbh8WOlYspQ3kl9"
    }

    resp = requests.post(token_url, data=data)
    tokens = resp.json()
    return tokens
    
# POST localhost/api/company
# ✅ Create company
@api.route("/company", methods=["POST"])
@enforce_policy("create_company")
def request_create_company():
    try:
        data = CompanyDTO(**request.json).model_dump()
        success, message = create_company(data)

        if success:
            return jsonify(data), 201
        else:
            return jsonify({"error": message}), 400
    except ValidationError as error:
        return jsonify(error.errors()), 400

