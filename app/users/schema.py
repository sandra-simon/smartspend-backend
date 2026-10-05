from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    joined_at: datetime
    theme: str

class UserUpdateRequest(BaseModel):
    username: str | None = None
    theme: str | None = None