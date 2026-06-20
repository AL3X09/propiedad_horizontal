from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DomainConfigBase(BaseModel):
    domain: str
    is_active: bool = True

class DomainConfigCreate(DomainConfigBase):
    pass

class DomainConfigUpdate(BaseModel):
    domain: Optional[str] = None
    is_active: Optional[bool] = None

class DomainConfigRead(DomainConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)