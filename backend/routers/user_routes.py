from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.config import get_db
from database.models.user_models import User
from schemas.user_schema import UserCreate, UserLogin, UserOut
from security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

# -------------------------------------------------------------
# REGISTER
# -------------------------------------------------------------
@router.post("/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    # Comprobar si existe username o email
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        profile_picture=user.profile_picture
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"status": "ok", "message": "Usuario registrado correctamente"}


# -------------------------------------------------------------
# LOGIN
# -------------------------------------------------------------
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    token = create_access_token({"sub": db_user.username})

    return {
        "status": "ok",
        "token": token,
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "profile_picture": db_user.profile_picture
        }
    }

