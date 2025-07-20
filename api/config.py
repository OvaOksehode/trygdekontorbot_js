from pydantic_settings import BaseSettings
from pydantic import Field

from pydantic import ConfigDict


class Settings(BaseSettings):
    database_string: str = Field("sqlite:///database.db", json_schema_extra={"env": "DATABASE_STRING"})
    environment: str = Field("testing", json_schema_extra={"env": "ENVIRONMENT"})

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

