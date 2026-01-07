# --- routers/todos.py ---

# modules
from fastapi import FastAPI, APIRouter, Request, Header, Body, HTTPException, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, select
from typing import Optional, Annotated

# my modules
from database import engine, get_session
from models.todos import Todo, TodoCreate, TodoRead, TodoUpdate, TodoDelete, ToDoUpdateIsDone
from models.users import User, UserCreate, UserRead, UserUpdate, UserDelete
from routers.auth import get_current_active_user

# FastAPI instance and API router
app = FastAPI()
router = APIRouter()

# templates settings
templates = Jinja2Templates(directory='templates')

# database session
# session = Session(engine)

# common query parameters
class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, offset: int = 0, limit: int = Query(default=100, le=100)):
        self.q = q
        self.offset = offset
        self.limit = limit




# create
@router.post("/todos", response_model=TodoRead, tags=["Todo"])
def create_todo(session: Annotated[Session, Depends(get_session)], todo: TodoCreate):
    db_todo = Todo.model_validate(todo) # <= from_orm(...) on SQLModel version older than 0.0.14
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo



# display todos with jinja: sync
@router.get("/todos_jinja", response_class=HTMLResponse, tags=["html"], response_model=list[TodoRead])
def display_todos(session: Annotated[Session, Depends(get_session)], commons: Annotated[CommonQueryParams, Depends()], request: Request):
    todos = session.exec(select(Todo).offset(commons.offset).limit(commons.limit)).all() # Todo here must be a database model i.e. table: not TodoRead model
    # if not todos:
    #     raise HTTPException(status_code=404, detail="Not found")
    # dont raise error but send the empty json if there is no record
    context = {
        "request": request,
        "todos": todos,
    }
    return templates.TemplateResponse("todos_jinja.html", context) # this context includes todo.id even if it is not loaded in the html



# display todos async
@router.get("/todos", response_class=HTMLResponse, tags=["Todo"], response_model=list[TodoRead])
def display_todos(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("todos.html", context)



# read list
@router.get("/todos/json", response_model=list[TodoRead], tags=["Todo"])
def read_todos_list(*, session: Session = Depends(get_session), offset: int = 0, limit: int = Query(default=100, le=100)):
    todos = session.exec(select(Todo).offset(offset).limit(limit)).all()
    if not todos:
        raise HTTPException(status_code=404, detail="Not found")
    return todos




# read one
@router.get("/todos/json/{todo_id}", response_model=TodoRead, tags=["Todo"])
def read_todo(*, session: Session = Depends(get_session), todo_id: int):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Not found")
    return todo




# patch
@router.patch("/todos/{todo_id}", response_model=TodoRead, tags=["Todo"])
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    session: Session = Depends(get_session)
    ):
    
    db_todo = session.get(Todo, todo_id)# todoテーブルをTodo.idで検索する
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_data = todo_update.model_dump(exclude_unset=True) # <= dict(...) on SQLModel version older than 0.0.14
    
    for field, value in todo_data.items():
        setattr(db_todo, field, value)
    
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo



# patch: is_done
@router.patch("/todos/is-done/{todo_id}", response_model=TodoRead, tags=["Todo"])
def update_todo(todo_id: int, todo_update: ToDoUpdateIsDone):
    with Session(engine) as session:
        db_todo = session.get(Todo, todo_id)# todoテーブルをTodo.idで検索する
        if not db_todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        todo_data = todo_update.model_dump(exclude_unset=True) # <= dict(...) on SQLModel version older than 0.0.14
        
        for key, value in todo_data.items():
            setattr(db_todo, key, value)
        
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)
        return db_todo



# delete
@router.delete("/todos/{todo_id}", tags=["Todo"])
def delete_todo(session: Annotated[Session, Depends(get_session)], todo_id: int):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(todo)
    session.commit()
    return {"deleted": todo}



@router.get("/my/todos/json", response_model=list[TodoRead], tags=["Todo"])
def read_my_todos(current_user: Annotated[UserRead, Depends(get_current_active_user)]):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == current_user.username)).one()
        my_todos = user.todos
        return my_todos



@router.post("/my/todos", response_model=list[TodoRead], tags=["Todo"])
def create_my_todos(current_user: Annotated[UserRead, Depends(get_current_active_user)], todo_create: TodoCreate):
    with Session(engine) as session:
        new_todo = Todo.model_validate(todo_create)
        user = session.exec(select(User).where(User.username == current_user.username)).one()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
        user.todos.append(new_todo)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user.todos


