from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class User(UserCreate):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

class CedulaCreate(BaseModel):
    cedula_number: str

class Cedula(CedulaCreate):
    id: int

    class Config:
        from_attributes = True