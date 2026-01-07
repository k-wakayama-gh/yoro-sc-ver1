# --- models/auth.py ---

# modules
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship



# token
class Token(SQLModel):
    access_token: str
    token_type: str


# token data
class TokenData(SQLModel):
    username: Optional[str] = None


