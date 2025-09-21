from pydantic_settings import BaseSettings
from pydantic import Field

from pydantic import ConfigDict


class Settings(BaseSettings):
    database_string: str = Field("sqlite:///database.db", json_schema_extra={"env": "DATABASE_STRING"})
    environment: str = Field("testing", json_schema_extra={"env": "APP_ENV"})

    # app settings

    starter_cash: int = Field("100", json_schema_extra={"env": "STARTER_CASH"})
    default_check_authority: str = Field("Trygdekontoret Ændal", json_schema_extra={"env": "DEFAULT_CHECK_AUTHORITY"})

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()