# --- models/period.py ---

# modules
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Period(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: int
    season: int
    start_time: datetime
    end_time: datetime



from pydantic import BaseModel
from typing import Dict

class PeriodRequest(BaseModel):
    year: int
    season: int
    start_time: Dict[str, int]  # 辞書で受け取る
    end_time: Dict[str, int]    # 辞書で受け取る

