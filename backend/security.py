from passlib.context import CryptContext
import jwts
from datetime import datetime, timedelta
from passlib.context import CryptContext

SECRET_KEY = "bfd678496eb42a69afeab62864d099518df582d5"
ALGORITHM = "HS256"

# Contexto del cifrado
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Metodo para cifrar una contraseña
def hash_password(password:str) -> str:
    return pwd_context.hash(password)

# Metodo para verificar la contraseña cifrada
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# Metodo para generar tokens
def generate_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
