from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    joined_at: datetime
    theme: str

class UserUpdateRequest(BaseModel):
    username: str | None = None
    theme: str | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError("Username cannot be empty.")

            if len(value) > 50:
                raise ValueError("Username must be 50 characters or fewer.")

        return value