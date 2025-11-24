from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./usuarios.db"

# Motor de la base de datos
engine = create_engine(DATABASE_URL, connect_args = {"check_same_thread": False})

# Crear sesion de la base de datos
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# Base para los modelos
Base = declarative_base()
