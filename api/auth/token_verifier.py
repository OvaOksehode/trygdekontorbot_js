from flask import request, jsonify
from authlib.jose import jwt, JsonWebKey
import requests
from config import Settings  # Pydantic BaseSettings

settings = Settings()  # Lag én instans som kan gjenbrukes

# Hent og cache JWK-sett én gang ved oppstart
jwks = JsonWebKey.import_key_set(requests.get(settings.jwks_url).json())


def verify_token(token):
    try:
        claims = jwt.decode(token, key=jwks)
        claims.validate()
        if claims["iss"] != settings.issuer:
            raise ValueError("Invalid issuer")
        if settings.keycloak_audience not in claims.get("aud", []):
            raise ValueError("Invalid audience")
        return claims
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def require_role(*roles_required):
    def decorator(f):
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"error": "Unauthorized"}), 401
            token = auth.split()[1]
            claims = verify_token(token)
            if not claims:
                return jsonify({"error": "Invalid or expired token"}), 401
            token_roles = claims.get("realm_access", {}).get("roles", [])
            if not any(role in token_roles for role in roles_required):
                return jsonify({
                    "error": f"Requires one of roles: {roles_required}"
                }), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator
