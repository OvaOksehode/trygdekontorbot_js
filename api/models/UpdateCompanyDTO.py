from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, constr

class UpdateCompanyDTO(BaseModel):
    name: Optional[Annotated[str, constr(min_length=3)]] = None
    
    model_config = ConfigDict(extra="forbid")  # Reject unexpected fields