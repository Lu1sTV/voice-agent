
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db, get_user_by_username
from app.schemas import UserLookupRequest, UserLookupResponse


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
    return {"status": "ok"}


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
