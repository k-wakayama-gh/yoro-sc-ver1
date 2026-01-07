# routers/auth.py

# modules
from fastapi import APIRouter, Request, Header, Body, HTTPException, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session, select
from typing import Optional, Annotated, Union
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# my modules
from database import engine, get_session
from models.auth import Token, TokenData
from models.users import User, UserCreate, UserRead, UserUpdate, UserDelete, UserInDB, UserUsername

# instance of API router and templates
router = APIRouter()
templates = Jinja2Templates(directory="templates")


# auth scheme and hash scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

env_my_secret_key = "MY_SECRET_KEY"
if env_my_secret_key in os.environ:
    MY_SECRET_KEY = os.getenv(env_my_secret_key)
else:
    MY_SECRET_KEY = "fakesecretkey"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 * 30 * 12




# verify password with hashed password
def verify_password(plain_password, hashed_password):
    plain_password = plain_password.encode("utf-8")[:72]
    return pwd_context.verify(plain_password, hashed_password)



# make hashed password
def get_hashed_password(password):
    password = password.encode("utf-8")[:72]
    return pwd_context.hash(password)



# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)



# get user by username
def get_user(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).one()
    return user



# verify username and password
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user



# create access token expecting {"sub": username} and expiring time
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, MY_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# get user from access token
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, MY_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user



# eliminate inactive user
def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



# login to get access token by sending username and password as a form data
@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}



# @router.get("/users/me", response_model=UserRead, tags=["User"])
# def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
#     return current_user



# @router.get("/users/me/items/")
# def read_own_items(current_user: Annotated[UserRead, Depends(get_current_active_user)]):
#     return [{"item_id": "Foo", "owner": current_user.username}]


