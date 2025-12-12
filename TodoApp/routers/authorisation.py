from datetime import datetime, timedelta, timezone
import token
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import SessionLocal
from models import users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

router = APIRouter(prefix="/auth", tags=["Authorisation"])

SECRET_KEY = '2e6e825a91ddb2706c8b7b252f62ff9e09f43259f744bedf3630da14cb465c6b'
ALGORITHM = 'HS256'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class UserCreateRequest(BaseModel):
    username: str
    email: str  
    full_name: str
    is_active: bool
    password: str
    first_name: str
    last_name: str   

class Token(BaseModel):
    access_token: str
    token_type: str

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
    """
    Gets a database session.

    Yields a database session object.
    Ensures the database session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)] 

def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticates a user.

    Args:
        db (Session): The database session.
        username (str): The username to authenticate.
        password (str): The password to authenticate.

    Returns:
        bool: True if the user is authenticated, False otherwise.
    """
    user = db.query(users).filter(users.username == username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    """
    Creates an access token for a user.

    Args:
        username (str): The username to create the access token for.
        user_id (int): The user ID to create the access token for.
        expires_delta (timedelta): The time delta for when the access token will expire.

    Returns:
        str: The encoded access token.
    """
    to_encode = {"sub": username, "id": user_id, "exp": datetime.now(timezone.utc) + expires_delta}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# create a user
@router.post("/auth/", status_code=status.HTTP_201_CREATED)
def create_user(create_user_request: UserCreateRequest, db: db_dependency):
    """
    Creates a new user.

    Args:
        create_user_request (UserCreateRequest): The user create request.
        db (Session): The database session.

    Returns:
        User: The created user.
    """
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


# login to get access token
@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    """
    Logs in a user and returns an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The login form data.
        db (Session): The database session.

    Returns:
        Token: The access token.

    Raises:
        HTTPException: 401 Unauthorized if the username or password is incorrect.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token(form_data.username, user.id, timedelta(minutes=15))
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """
    Gets the current user.

    Args:
        token (str): The access token to validate.

    Returns:
        str: The username of the current user.

    Raises:
        HTTPException: 401 Unauthorized if the access token is invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise credentials_exception
        return {"username": username, "id": user_id} # username, user_id
    except JWTError:
        raise credentials_exception
    #    if username is None:
    #        raise credentials_exception
    #    return user