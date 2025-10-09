from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class JobOut(BaseModel):
    id: str
    prompt: str
    status: str
    result_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
