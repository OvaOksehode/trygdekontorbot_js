from typing import Annotated
from pydantic import BaseModel, Field

class TransactionPaginationParams(BaseModel):
    limit: Annotated[int, Field(strict=True, ge=1, le=100, default=20)]
    offset: Annotated[int, Field(strict=True, ge=0, default=0)]