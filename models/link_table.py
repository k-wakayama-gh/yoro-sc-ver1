# --- models/link_table.py ---

# modules
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    import users, lessons, todos



class UserLessonLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    lesson_id: Optional[int] = Field(default=None, foreign_key="lesson.id", primary_key=True)



class UserTodoLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    todo_id: Optional[int] = Field(default=None, foreign_key="todo.id", primary_key=True)


class UserUserDetailLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    user_details_id: Optional[int] = Field(default=None, foreign_key="userdetail.id", primary_key=True)


class UserUserChildLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    user_children_id: Optional[int] = Field(default=None, foreign_key="userchild.id", primary_key=True)
    # later to change user_children_id to user_child_id


class UserChildLessonLink(SQLModel, table=True):
    user_child_id: Optional[int] = Field(default=None, foreign_key="userchild.id", primary_key=True)
    lesson_id: Optional[int] = Field(default=None, foreign_key="lesson.id", primary_key=True)

