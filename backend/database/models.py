from sqlalchemy import Column, Integer, String
from .config import Base
from ..security import hash_password
class User(Base):
    __tablename__ = "usuario"

    # Parametros de la base de datos
    id = Column(Integer, primary_key = true, index = True)
    name = Column(String, nullable = False)
    email = Column(String, nullable = False, unique = True)
    password = Column(String, nullable = False)
    
    # Constructor de la clase
    def __init__(self, email, username, password) -> None:
        self.__email = email
        self.__username = username
        self.__password = hash_password(password)

    # Metodos de la clase
    # Crear usuarios
    def create_user(self) -> self:
        db = SessionLocal()
        db.add(self)
        db.commit()
        db.refresh(self)
        db.close()
        return self

    # Obtener usuario por email
    def get_users_by_email(self, email: str):
        db = SessionLocal()
        user = db.query(User).filter(self.__email == email).first()
        db.close()
        return user
    def get_all_users(self):
        db = SessionLocal()
        user = db.query(User)
        db.close()
        return user
        
        
