# Dependencias del proyecto
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class UserModel(Base):
    # Tabla de usuarios
    __tablename__ = "users"

    # Atributos de la base de datos
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, nullable = False)
    email = Column(String, nullable = False, unique = True)
    password =Column(String, nullable = False)
    profile_picture = Column(Text, nullable = False)            # Conversion a Base64
    
