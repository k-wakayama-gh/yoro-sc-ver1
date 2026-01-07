# --- models/lessons.py ---

# modules
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# my modules
from models import link_table

if TYPE_CHECKING:
    import users



# base model
class LessonBase(SQLModel):
    year: int
    season: int
    number: int
    title: str
    teacher: str
    day: str
    time: str
    price: int
    description: Optional[str]
    capacity: Optional[int]
    lessons: Optional[int]



# table
class Lesson(LessonBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    capacity_left: Optional[int] = Field(default=None)
    
    users: List["users.User"] = Relationship(back_populates="lessons", link_model=link_table.UserLessonLink)
    user_children: List["users.UserChild"] = Relationship(back_populates="lessons", link_model=link_table.UserChildLessonLink)



# create
class LessonCreate(LessonBase):
    pass



# read or out
class LessonRead(LessonBase):
    id: int
    capacity_left: Optional[int]



# update: independent SQLModel model: Optional[...] = None works properly with Patch requests
class LessonUpdate(SQLModel):
    year: Optional[int] = None
    season: Optional[int] = None
    number: Optional[int] = None
    title: Optional[str] = None
    teacher: Optional[str] = None
    day: Optional[str] = None
    time: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    capacity: Optional[int] = None
    lessons: Optional[int] = None



# delete
class LessonDelete(LessonBase):
    pass


