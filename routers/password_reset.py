# routers/password_reset.py

# modules
from fastapi import APIRouter, Request, Header, Body, HTTPException, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, select
from typing import Optional, Annotated
from datetime import datetime, timedelta, timezone

import base64
import hashlib
import hmac
import json
from pydantic import BaseModel

# my modules
from database import engine, get_session
from models.lessons import Lesson, LessonCreate, LessonRead, LessonUpdate, LessonDelete
from models.users import User, UserCreate, UserRead, UserUpdate, UserDelete, UserChild
from routers.auth import get_current_active_user, get_hashed_password


# instance of API router and templates
router = APIRouter()
templates = Jinja2Templates(directory="templates")


# パスワードリセットリクエスト用のモデル
class PasswordResetRequest(BaseModel):
    username: str

# パスワードリセット用のモデル
class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


SECRET_KEY = "tempura"
EXPIRATION_DAYS = 3


def generate_reset_token(username: str) -> str:
    # username と timestamp を含むトークンを生成
    timestamp = int((datetime.utcnow() + timedelta(days=EXPIRATION_DAYS)).timestamp())
    data = json.dumps({"username": username, "exp": timestamp})
    data_bytes = data.encode("utf-8")
    signature = hmac.new(SECRET_KEY.encode(), data_bytes, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(data_bytes + signature).decode("utf-8")
    return token



def verify_reset_token(token: str):
    # トークンを検証し、username を取得
    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8"))
        data_bytes, signature = decoded[:-32], decoded[-32:]
        expected_signature = hmac.new(SECRET_KEY.encode(), data_bytes, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid signature")
        data = json.loads(data_bytes.decode("utf-8"))
        if datetime.utcnow().timestamp() > data["exp"]:
            raise ValueError("Token expired")
        return data["username"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid token or expired: {str(e)}")




@router.post("/request-password-reset/", tags=["PasswordReset"])
def request_password_reset(request: PasswordResetRequest, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not user.is_admin:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authorized")
    username = request.username
    token = generate_reset_token(username)
    reset_link = f"https://yoro-sc.azurewebsites.net/password_reset?token={token}"
    return JSONResponse(content={"message": "Reset link generated", "reset_link": reset_link, "username": username})





@router.post("/reset-password/", tags=["PasswordReset"])
def reset_password(request: PasswordResetConfirm, session: Annotated[Session, Depends(get_session)]):
    token = request.token
    new_password = request.new_password
    if len(new_password) < 4 or not new_password.isalnum():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="this password does not pass the requirements")
    # トークンを検証し、新しいパスワードを設定
    username = verify_reset_token(token)
    if username is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    hashed_password = get_hashed_password(new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return {"message": "Password has been reset successfully", "username": username}




@router.get("/password_reset", response_class=HTMLResponse, tags=["html"])
def get_password_reset_html(request: Request):
    html_file = "password_reset.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)



# admin
@router.get("/admin/password_reset", response_class=HTMLResponse, tags=["html"])
def get_password_reset_html_admin(request: Request):
    html_file = "admin/password_reset.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)


