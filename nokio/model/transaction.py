from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime, date


class Transaction(BaseModel):
    # org_nr: str
    date: date
    name: str
    description: Optional[str] = None
    recorded_at: datetime
    account: Dict[str, float]
    verificate: Optional[int] = None
    frozen: Optional[bool] = None
