from sqlalchemy import Boolean, Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)

class Cedula(Base):
    __tablename__ = "cedulas"
    id = Column(Integer, primary_key=True, index=True)
    cedula_number = Column(String, unique=True, index=True)
