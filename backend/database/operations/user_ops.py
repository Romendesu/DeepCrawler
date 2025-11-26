import os
import random
import base64
from database.config import SessionLocal
from database.models.user_models import User
from ..security import hash_password

PROFILE_PICS_PATH = "static/profile_pictures"

# Codificar la imagen en base64
def encode_image_to_base64(file_path):
    """Lee un archivo de imagen y lo convierte a base64"""
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return encoded

# Crear usuario dentro de la base de datos
def create_user(username: str, email: str, password: str):
    db = SessionLocal()

    # Comprobar si ya existe ese usuario
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        db.close()
        return None

    # Elegir imagen aleatoria
    pics = os.listdir(PROFILE_PICS_PATH)
    selected_pic_file = random.choice(pics) if pics else "default.png"
    selected_pic_path = os.path.join(PROFILE_PICS_PATH, selected_pic_file)

    # Codificar imagen a base64
    encoded_pic = encode_image_to_base64(selected_pic_path)

    new_user = User(
        username=username,
        email=email,
        password=hash_password(password),
        profile_picture=encoded_pic
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    return new_user

def update_user(user_id: int, username: str = None, email: str = None,
                password: str = None, profile_picture_file: str = None):
    """
    Actualiza los datos de un usuario.
    Solo actualiza los campos que se pasen como argumento.
    
    profile_picture_file: ruta de la nueva imagen (opcional)
    """
    db = SessionLocal()
    user = db.query(User).filter_by(id=user_id).first()

    if not user:
        db.close()
        return None  # Usuario no encontrado

    # Actualizar campos si se proporcionan
    if username:
        user.username = username
    if email:
        user.email = email
    if password:
        user.password = hash_password(password)  # En producción, aplicar hash
    if profile_picture_file:
        if os.path.exists(profile_picture_file):
            user.profile_picture = encode_image_to_base64(profile_picture_file)

    db.commit()
    db.refresh(user)
    db.close()
    return user
