
from pydantic import BaseModel, Field


class UserLookupRequest(BaseModel):
    username: str


class UserLookupResponse(BaseModel):
    found: bool
    user_id: int | None = None
    username: str | None = None
    display_name: str | None = None
    account_locked: bool | None = None


class VerificationStartRequest(BaseModel):
    user_id: int


class VerificationStartResponse(BaseModel):
    verification_id: str
    status: str


class VerificationConfirmRequest(BaseModel):
    verification_id: str
    code: str


class VerificationConfirmResponse(BaseModel):
    verified: bool
    verification_token: str | None = None


class PasswordResetRequest(BaseModel):
    user_id: int
    verification_token: str
    new_password: str = Field(min_length=8)


class PasswordResetResponse(BaseModel):
    success: bool
    message: str
