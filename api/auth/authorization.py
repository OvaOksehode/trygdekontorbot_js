import json
from functools import wraps
import logging
from flask import request, jsonify
from jose import jwt

from config import Settings

settings = Settings()

with open(settings.policies_path) as f:
    POLICIES = json.load(f)

def verify_token(token):
    try:
        payload = jwt.decode(token, settings.keycloak_public_key, algorithms=[settings.keycloak_algorithm], issuer=settings.keycloak_issuer, audience="account")
        return payload
    except jwt.JWTError as e:
        logging.error(f"Exception: {e}")
        return None

def extract_roles(payload):
    roles = set(payload.get("realm_access", {}).get("roles", []))
    for client in payload.get("resource_access", {}).values():
        roles.update(client.get("roles", []))
    return list(roles)

def enforce_policy(action):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or malformed Authorization header"}), 401

            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            if not payload:
                return jsonify({"error": "Invalid or expired token"}), 401

            username = payload.get("preferred_username")
            roles = extract_roles(payload)
            policy = POLICIES.get(action)

            if not policy:
                return jsonify({"error": "No policy found"}), 403

            if username in policy.get("denied_users", []):
                return jsonify({"error": "Access denied (user)"}), 403

            if not any(role in roles for role in policy.get("allowed_roles", [])):
                return jsonify({"error": "Access denied (role)"}), 403

            request.user = {
                "username": username,
                "roles": roles,
                "sub": payload.get("sub")
            }

            return f(*args, **kwargs)
        return wrapper
    return decorator
