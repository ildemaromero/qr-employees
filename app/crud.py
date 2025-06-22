from sqlalchemy.orm import Session
from . import models, schemas, auth

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_cedula(db: Session, cedula: schemas.CedulaCreate):
    db_cedula = models.Cedula(cedula_number=cedula.cedula_number)
    db.add(db_cedula)
    db.commit()
    db.refresh(db_cedula)
    return db_cedula

def get_cedulas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Cedula).offset(skip).limit(limit).all()