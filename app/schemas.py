from pydantic import BaseModel

class UserLookupRequest(BaseModel):
	username: str

class UserLookupResponse(BaseModel):
	found: bool
	user_id: int | None = None
	username: str | None = None
	display_name: str | None = None
	account_locked: bool | None = None
