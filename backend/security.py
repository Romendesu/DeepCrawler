from passlib.context import CryptContext

# Contexto del cifrado
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Metodo para cifrar una contraseña
def hash_password(password:str) -> str:
    return pwd_context.hash(password)

# Metodo para verificar la contraseña cifrada
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)
