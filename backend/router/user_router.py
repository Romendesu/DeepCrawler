from fastapi import APIRouter, HTTPException
from database.operations.user_ops import create_user
from schemas.user_schema import UserRegister

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register")
def register_user(user_data: UserRegister):
    """
    Registra un usuario nuevo en la base de datos.
    """
    user = create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        profile_picture_file=user_data.profile_picture_file
    )

    if not user:
        raise HTTPException(status_code=400, detail="El usuario o email ya existen")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "profile_picture": user.profile_picture
    }

