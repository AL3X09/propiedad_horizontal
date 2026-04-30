from pydantic import BaseModel, Field
from typing import List

class UserPermissionsSet(BaseModel):
    permissions: List[str] = Field(default_factory=list)  # lista de codes