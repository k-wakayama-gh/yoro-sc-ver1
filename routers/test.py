# --- routers/test.py ---

# modules
from fastapi import FastAPI, APIRouter, Request, Header, Body, HTTPException, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, select
from typing import Optional, Annotated
from datetime import datetime
import shutil

# my modules
from database import engine, get_session
from models.users import User, UserCreate, UserRead, UserUpdate, UserDelete
from routers.auth import get_current_active_user

# FastAPI instance and API router
app = FastAPI()
router = APIRouter()

# templates settings
templates = Jinja2Templates(directory='templates')



# @router.get("/backupdatabase", tags=["manage"])
# def backup_database_file(current_user: Annotated[User, Depends(get_current_active_user)]):
#     username = current_user.username
#     if username != "user":
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#     source_file = "/home/db_dir/database.sqlite"
#     destination_file = "/mount/db_dir/yoro-sc" + ".sqlite"
#     try:
#         subprocess.run(["cp", source_file, destination_file])
#     except subprocess.CalledProcessError as error:
#         print("error on backup database file", error)
#     return {"backup database file": "done"}





