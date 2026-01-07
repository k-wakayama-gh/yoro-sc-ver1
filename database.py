# --- database.py ---

# modules
from sqlmodel import SQLModel, create_engine, Session
import os
import shutil
from datetime import datetime, timedelta


# env_docker = "IN_DOCKER_CONTAINER"
env_mount = "WEBSITES_ENABLE_APP_SERVICE_STORAGE"
env_db = "DB_CONNECTION_STRING"


# switch production and development
if env_mount in os.environ:
    db_dir = "/home/db_dir/"
else:
    db_dir = ""


db_file = f"{db_dir}database.sqlite"


if db_dir != "":
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)


# switch on database server and sqlite file
if env_db in os.environ:
    db_connection_string = os.getenv(env_db)
    connect_args={'check_same_thread': True}
else:
    db_connection_string = f"sqlite:///{db_file}"
    connect_args={'check_same_thread': False}


# database settings
engine = create_engine(db_connection_string, echo=False, connect_args=connect_args)


# def: create the database
def create_database():
    SQLModel.metadata.create_all(engine)


# def: database session for dependency injection
def get_session():
    with Session(engine) as session:
        yield session





# backup database.sqlite
def make_remote_db_dir():
    if env_mount in os.environ:
        backup_db_dir = "/mount/db_dir/"
        if not os.path.exists(backup_db_dir):
            os.makedirs(backup_db_dir)


# def override_current_db():
#     make_remote_db_dir()
#     backup_db_dir = "/mount/db_dir/"
#     if os.path.exists(backup_db_dir):
#         backup_db = f"{backup_db_dir}yoro-sc.sqlite"
#         current_db = db_file
#         shutil.copy2(backup_db, current_db)


def make_backup_db():
    backup_db_dir = "/mount/db_dir/"
    if os.path.exists(backup_db_dir) and env_mount in os.environ:
        current_datetime = (datetime.utcnow() + timedelta(hours=9)).strftime("%Y-%m-%dT%H-%M-%S")
        backup_db = f"{backup_db_dir}yoro-sc_{current_datetime}.sqlite"
        current_db = db_file
        shutil.copy2(current_db, backup_db)
    else:
        make_remote_db_dir()


