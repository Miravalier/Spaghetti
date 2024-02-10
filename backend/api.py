from fastapi import APIRouter

from dependencies import AuthorizedUser


router = APIRouter()


@router.get("/status")
async def get_status(user: AuthorizedUser):
    return {"status": "success", "user": user.model_dump(exclude={"hashed_password"})}
