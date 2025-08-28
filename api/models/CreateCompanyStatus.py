from enum import Enum

class CreateCompanyStatus(str, Enum):
    CREATED = "created"
    ALREADY_EXISTS_WITH_SAME_NAME = "already_exists"
    ALREADY_EXISTS_WITH_SAME_OWNER_DISCORD_ID = "already_exists"
    INVALID = "invalid"
    ERROR = "error"
