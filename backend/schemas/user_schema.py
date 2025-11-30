from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str
    profile_picture: str | None = None  # Base64

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    profile_picture: str | None = None

    class Config:
        orm_mode = True

