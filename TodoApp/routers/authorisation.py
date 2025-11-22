from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import SessionLocal
from models import users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreateRequest(BaseModel):
    username: str
    email: str  
    full_name: str
    is_active: bool
    password: str
    first_name: str
    last_name: str   

class UserUpdateRequest(BaseModel):
    username: str
    email: str  
    full_name: str
    is_active: bool
    password: str
    first_name: str
    last_name: str
    role: str

# Get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]    


@router.get("/auth")
def get_user():
    return {"user": "authenticated"}

# get all Users
@router.get("/auth/users", status_code=status.HTTP_200_OK)
def get_all_users(db: db_dependency):
    return db.query(users).all()


# create a user
@router.post("/auth/", status_code=status.HTTP_201_CREATED)
def create_user(create_user_request: UserCreateRequest, db: db_dependency):
    create_user_model = users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        full_name=create_user_request.full_name,
        is_active=True,
        hashed_password=pwd_context.hash(create_user_request.password) 
    )

    # add to the database    
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return create_user_model

# update a user
@router.put("/auth/{user_id}")
def update_user(user_id: int, update_user_request: UserUpdateRequest, db: db_dependency):
    user_model = db.query(users).filter(users.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update fields directly
    user_model.username = update_user_request.username
    user_model.email = update_user_request.email
    user_model.first_name = update_user_request.first_name
    user_model.last_name = update_user_request.last_name
    user_model.full_name = update_user_request.full_name
    user_model.is_active = update_user_request.is_active
    user_model.hashed_password = pwd_context.hash(update_user_request.password)
    user_model.role = update_user_request.role
    
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return user_model