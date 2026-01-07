# --- main.py ---

# frameworks and libraries
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from alembic import command
from alembic.config import Config

# my modules
from database import engine, create_database
import routers.html, routers.items, routers.users, routers.lessons, routers.auth, routers.todos, routers.test, routers.password_reset, routers.settings
from force_sqlite import force_sqlite

# FastAPI instance
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# migrate database
def migrate_database():
    if "WEBSITES_ENABLE_APP_SERVICE_STORAGE" in os.environ:
        alembic_cfg = Config("alembic_product.ini")
        command.upgrade(alembic_cfg, "head")

# include API routers
app.include_router(routers.html.router)
app.include_router(routers.items.router)
app.include_router(routers.users.router)
app.include_router(routers.lessons.router)
app.include_router(routers.auth.router)
app.include_router(routers.todos.router)
app.include_router(routers.test.router)
app.include_router(routers.password_reset.router)
app.include_router(routers.settings.router)


# static files settings
app.mount('/static', StaticFiles(directory='static'), name='static')

# create database on startup
@app.on_event("startup")
def on_startup():
    create_database()

@app.on_event("shutdown")
def on_shutdown():
    pass

# run on local
if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)


# --- security for docs ---

# username and password for docs
env_my_secret_username = "MY_SECRET_USERNAME"
env_my_secret_password = "MY_SECRET_PASSWORD"

if env_my_secret_username in os.environ:
    MY_SECRET_USERNAME = os.getenv(env_my_secret_username)
else:
    MY_SECRET_USERNAME = "user"

if env_my_secret_password in os.environ:
    MY_SECRET_PASSWORD = os.getenv(env_my_secret_password)
else:
    MY_SECRET_PASSWORD = ""


# modules
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials


security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, MY_SECRET_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, MY_SECRET_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/docs")
async def get_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json")
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title = "FastAPI", version="0.1.0", routes=app.routes)


