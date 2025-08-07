from config import Settings
import pytest
from flask import Flask
from routes.api import api  # Adjust import as needed
from unittest.mock import patch
from jose import jwt
import datetime

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(api, url_prefix="/api")
    return app

@pytest.fixture
def client(app):
    return app.test_client()

settings = Settings()

# --------------------------------------
# Generate a dummy JWT with required claims
# --------------------------------------
@pytest.fixture
def token():
    secret = settings.keycloak_public_key  # Replace with your public/private test key setup
    payload = {
        "sub": "user-id-123",
        "preferred_username": "tester",
        "realm_access": {
            "roles": ["bot", "create_company"]  # <- Required role for policy
        },
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        "iat": datetime.datetime.utcnow(),
        "aud": "account",  # Match your Keycloak audience
        "iss": "http://localhost:8080/realms/Trygdekontorbot",
    }
    token = jwt.encode(payload, secret, algorithm="RS256")  # RS256 if you're verifying against public key
    return token

# --------------------------------------
# Inject valid token into request header
# --------------------------------------
def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }

# --------------------------------------
# Actual test using authentication
# --------------------------------------
def test_create_company_success_authenticated(client, token):
    payload = {
        "name": "Test Company"
    }

    with patch("routes.api.create_company") as mock_create:
        mock_create.return_value = True

        response = client.post(
            "/api/company",
            json=payload,
            headers=auth_headers(token)
        )

        assert response.status_code == 201
        assert response.get_json()["name"] == "Test Company"
