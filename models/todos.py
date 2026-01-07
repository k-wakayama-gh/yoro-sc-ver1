# --- models/todos.py ---

# modules
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# my modules
from models import link_table

if TYPE_CHECKING:
    import users



# base model
class TodoBase(SQLModel):
    title: str
    content: Optional[str] = Field(default=None)
    is_done: bool = Field(default=False) #is_done: bool = Noneにすると、patchでも空のリクエストがあるたびにboolの値をFalseにしようとする。Fieldを使うと最初だけFalseにしようとする。



# table
class Todo(TodoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    users: List["users.User"] = Relationship(back_populates="todos", link_model=link_table.UserTodoLink)



# create
class TodoCreate(TodoBase):
    pass



# read
class TodoRead(TodoBase):
    id: int



# update: independent SQLModel models for each: Optional[...] = None works properly for Patch requests
class TodoUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None


class ToDoUpdateIsDone(SQLModel):
    is_done: bool


# delete
class TodoDelete(TodoBase):
    pass


