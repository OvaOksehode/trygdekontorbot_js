from pydantic_settings import BaseSettings
from pydantic import Field

from pydantic import ConfigDict


class Settings(BaseSettings):
    # Environment and db
    database_string: str = Field("sqlite:///database.db", json_schema_extra={"env": "DATABASE_STRING"})
    environment: str = Field("testing", json_schema_extra={"env": "ENVIRONMENT"})
    
    # Keycloak settings
    keycloak_public_key: str = Field("-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----", json_schema_extra={"env": "KEYCLOAK_PUBLIC_KEY"})
    keycloak_issuer: str = Field("http://localhost:8080/realms/Trygdekontorbot", json_schema_extra={"env": "KEYCLOAK_ISSUER"})
    keycloak_algorithm: str = Field("RS256", json_schema_extra={"env": "KEYCLOAK_ALGORITHM"})

    # Authorization
    policies_path: str = Field("auth/policies.json", json_schema_extra={"env": "POLICIES_PATH"})

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

