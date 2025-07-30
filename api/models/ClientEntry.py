from pydantic import BaseModel
from typing import List

class ClientEntry(BaseModel):
    username: str | None = None
    secret: str
    claims: List[str]
