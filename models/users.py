# --- models/users.py ---

# modules
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
# from pydantic import EmailStr
from datetime import datetime, timedelta

# my modules
from models import link_table

if TYPE_CHECKING:
    import lessons, todos



# base model
class UserBase(SQLModel):
    username: str = Field(unique=True, min_length=4)


# do not return this out!
class UserIn(UserBase):
    plain_password: str = Field(min_length=4)


# never return this out!
class UserInDB(UserBase):
    hashed_password: str



# table: do not return this out!
class User(UserInDB, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_active: Optional[bool] = Field(default=True)
    is_admin: Optional[bool] = Field(default=False)
    
    lessons: List["lessons.Lesson"] = Relationship(back_populates="users", link_model=link_table.UserLessonLink)
    todos: List["todos.Todo"] = Relationship(back_populates="users", link_model=link_table.UserTodoLink)
    user_details: Optional["UserDetail"] = Relationship(back_populates="user", link_model=link_table.UserUserDetailLink)
    user_children: List["UserChild"] = Relationship(back_populates="user", link_model=link_table.UserUserChildLink)



# create: do not return this out!
class UserCreate(UserBase):
    plain_password: str



# read
class UserRead(SQLModel):
    id: int
    username: str
    is_admin: Optional[bool]


# read: username
class UserUsername(SQLModel):
    username: str


# patch
class UserUpdate(SQLModel):
    username: Optional[str] = Field(default=None, unique=True, min_length=4)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    plain_password: Optional[str] = Field(default=None, min_length=4)



# delete
class UserDelete(UserBase):
    pass



# user details

class UserDetailBase(SQLModel):
    email: Optional[str] = Field(default=None)
    first_name: str
    last_name: str
    first_name_furigana: str
    last_name_furigana: str
    tel: str
    postal_code: str
    address: str



class UserDetail(UserDetailBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="user_details", link_model=link_table.UserUserDetailLink)
    created_time: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=9))



class UserDetailCreate(SQLModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    first_name_furigana: Optional[str] = None
    last_name_furigana: Optional[str] = None
    tel: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None


class UserWithUserDetailCreate(UserIn, UserDetailCreate):
    pass



class UserDetailRead(UserDetailBase):
    pass


class UserDetailUsernameRead(UserDetailBase):
    username: str


class UserWithUserDetailRead(UserRead, UserDetailRead):
    pass




# user children

class UserChildBase(SQLModel):
    child_first_name: str
    child_last_name: str
    child_first_name_furigana: str
    child_last_name_furigana: str


class UserChild(UserChildBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="user_children", link_model=link_table.UserUserChildLink)
    lessons: List["lessons.Lesson"] = Relationship(back_populates="user_children", link_model=link_table.UserChildLessonLink)



# class UserChildCreate(SQLModel):
#     user_children: List["UserChildBase"]

class UserChildCreate(UserChildBase):
    pass

class UserChildRead(UserChildBase):
    id: int

