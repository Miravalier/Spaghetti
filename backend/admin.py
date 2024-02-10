from fastapi import APIRouter

from dependencies import AdminUser


router = APIRouter()


@router.get("/status")
async def get_status(user: AdminUser):
    return {"status": "success", "user": user.model_dump(exclude={"hashed_password"})}
