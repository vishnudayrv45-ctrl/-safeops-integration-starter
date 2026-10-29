from pydantic import BaseModel, Field
from typing import Optional

class IncidentIn(BaseModel):
    service: str = Field(min_length=1, max_length=100)
    status: str = Field(min_length=1, max_length=40)
    http_status: Optional[int] = None
    error: Optional[str] = Field(default=None, max_length=2000)
    source: str = Field(default="monitoring-agent", max_length=100)
