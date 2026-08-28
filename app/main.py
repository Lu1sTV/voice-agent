        
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.database import (
    init_db,
    get_user_by_username,
    get_user_by_id,
    create_verification,
    confirm_verification,
    reset_password,
)

from app.schemas import (
    UserLookupRequest,
    UserLookupResponse,
    VerificationStartRequest,
    VerificationStartResponse,
    VerificationConfirmRequest,
    VerificationConfirmResponse,
    PasswordResetRequest,
    PasswordResetResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Voice API",
    lifespan=lifespan
)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post(
    "/users/lookup",
    response_model=UserLookupResponse
)
def lookup_user(request: UserLookupRequest):
    user = get_user_by_username(request.username)

    if user is None:
        return UserLookupResponse(
            found=False
        )

    return UserLookupResponse(
        found=True,
        user_id=user["id"],
        username=user["username"],
        display_name=user["display_name"],
        account_locked=bool(user["account_locked"])
    )


@app.post(
    "/verification/start",
    response_model=VerificationStartResponse
)
def start_verification(
    request: VerificationStartRequest
):
    user = get_user_by_id(request.user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    verification_id = create_verification(
        request.user_id
    )

    return VerificationStartResponse(
        verification_id=verification_id,
        status="verification_started"
    )


@app.post(
    "/verification/confirm",
    response_model=VerificationConfirmResponse
)
def verify_code(
    request: VerificationConfirmRequest
):
    token = confirm_verification(
        request.verification_id,
        request.code
    )

    if token is None:
        return VerificationConfirmResponse(
            verified=False
        )

    return VerificationConfirmResponse(
        verified=True,
        verification_token=token
    )


@app.post(
    "/password-reset",
    response_model=PasswordResetResponse
)
def change_password(
    request: PasswordResetRequest
):
    success = reset_password(
        user_id=request.user_id,
        verification_token=request.verification_token,
        new_password=request.new_password
    )

    if not success:
        raise HTTPException(
            status_code=403,
            detail="Invalid or already used verification"
        )

    return PasswordResetResponse(
        success=True,
        message="Password changed successfully"
    )
