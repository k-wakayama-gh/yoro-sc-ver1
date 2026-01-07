# routers/html.py

# modules
from fastapi import APIRouter, Request, Header, Body, HTTPException, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, select
from typing import Optional, Annotated
from datetime import datetime, timedelta
import json
from pathlib import Path

# my modules
from database import engine, get_session
from models.items import Item, ItemCreate, ItemRead, ItemUpdate, ItemDelete
from models.users import User, UserCreate, UserRead, UserUpdate, UserDelete
from models.todos import Todo, TodoCreate, TodoRead, TodoUpdate, TodoDelete
from routers.auth import get_current_active_user
from database import make_backup_db

# instance of API router and templates
router = APIRouter()
templates = Jinja2Templates(directory="templates")



# top page
@router.get("/", response_class=HTMLResponse, tags=["html"])
def get_index_html(request: Request):
    html_file = "index.html"
    context = {
        "request": request,
        "title": "ホーム｜(一社)養老スポーツクラブ",
    }
    return templates.TemplateResponse(html_file, context)



# my page
@router.get("/my", response_class=HTMLResponse, tags=["html"])
def get_my_html(request: Request):
    html_file = "my.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)



# user sign up page
@router.get("/users/signup", response_class=HTMLResponse, tags=["html"])
def get_user_signup_html(request: Request):
    html_file = "signup.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)



# after sign up complete page
@router.get("/signupcomplete", response_class=HTMLResponse, tags=["html"])
def get_signup_complete_html(request: Request):
    html_file = "signupcomplete.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)



# admin top page
@router.get("/admin", response_class=HTMLResponse, tags=["html"])
def get_admin_html(request: Request):
    html_file = "admin.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)




# # coffee page
# @router.get("/coffee", response_class=HTMLResponse, tags=["html"])
# def coffee(request: Request):
#     context = {
#         'request': request,
#     }
#     return templates.TemplateResponse('coffee.html', context)


# warm cold start
@router.get("/warmup")
def warmup():
    return {"warmup": "ok"}



# backup database.sqlite
@router.get("/backupdatabase")
def backup_database():
    make_backup_db()
    return {"backup database.sqlite to yoro-sc.sqlite": "ok"}



@router.get("/now", tags=["test"])
def show_current_datetime():
    current_datetime = (datetime.utcnow() + timedelta(hours=9)).strftime("%Y-%m-%dT%H-%M-%S")
    return {"now": current_datetime}


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return (
        "User-agent: *\n"
        "Disallow: /admin\n"
        "Disallow: /json\n"
    )


FILE_PATH = Path("logs.json")

@router.get("/json/admin/logs")
def get_logs_json(current_user: Annotated[Session, Depends(get_current_active_user)]):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authorized")
    """JSONファイルのログをすべて返す"""
    if FILE_PATH.exists():
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []
    return JSONResponse(content=logs)


@router.get("/admin/logs", response_class=HTMLResponse, tags=["html"])
def get_signup_complete_html(request: Request):
    html_file = "/admin/logs.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)

