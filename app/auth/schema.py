from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class RegisterResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str


class PasswordUpdateRequest(BaseModel):
    current_password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )
    reset_token: str | None = None
    new_password: str = Field(
        min_length=8,
        max_length=128,
    )