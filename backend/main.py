from fastapi import FastAPI
from routers import user_routes, chat_routes
from database.config import Base, engine
from database.models import *

# Crear tablas si no existen
Base.metadata.create_all(engine)

app = FastAPI(title="DeepCrawler")

# Incluir routers
app.include_router(user_routes.router)


