# --- routers/lessons.py ---

# modules
from fastapi import APIRouter, Request, Header, Body, HTTPException, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, select
from typing import Optional, Annotated
from datetime import datetime, timedelta, timezone
import os

# my modules
from database import engine, get_session
from models.lessons import Lesson, LessonCreate, LessonRead, LessonUpdate, LessonDelete
from models.users import User, UserCreate, UserRead, UserUpdate, UserDelete, UserChild, UserChildRead
from routers.auth import get_current_active_user
from models.settings import Period
from logs import add_log

# instance of API router and templates
router = APIRouter()
templates = Jinja2Templates(directory="templates")


# common query parameters
class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, offset: int = 0, limit: int = Query(default=100, le=100)):
        self.q = q
        self.offset = offset
        self.limit = limit



# temporary date time
class TemporaryCurrentPeriod:
    year = 2025
    season = 1
    start_time = datetime(year=2025, month=4, day=9, hour=7, minute=0, second=0, tzinfo=timezone(timedelta(hours=9)))
    test_start_time = datetime(year=2024, month=4, day=9, hour=22, minute=30, second=0, tzinfo=timezone(timedelta(hours=9)))
    notification_time = datetime(year=2025, month=4, day=29, hour=0, minute=0, second=0, tzinfo=timezone(timedelta(hours=9)))

# for test
# CurrentPeriod.start_time = CurrentPeriod.test_start_time

if "PUBLIC_API_KEY" in os.environ:
    PUBLIC_API_KEY = os.getenv("PUBLIC_API_KEY")
else:
    PUBLIC_API_KEY = "fake_key"


# create a lesson: this is not used now
@router.post("/lessons", response_model=LessonRead, tags=["Lesson"])
def create_lesson(session: Annotated[Session, Depends(get_session)], lesson_create: LessonCreate):
    db_lesson = Lesson.model_validate(lesson_create)
    session.add(db_lesson)
    session.commit()
    session.refresh(db_lesson)
    return db_lesson



# jinja: display lessons synced: this is not used now
@router.get("/jinja/lessons", response_class=HTMLResponse, tags=["html"], response_model=list[LessonRead])
def display_lessons_sync(session: Annotated[Session, Depends(get_session)], query: Annotated[CommonQueryParams, Depends()], request: Request):
    html_file = "lessons.html"
    lessons = session.exec(select(Lesson).offset(query.offset).limit(query.limit)).all()
    context = {
        "request": request,
        "lessons": lessons,
        "title": "教室一覧",
    }
    return templates.TemplateResponse(html_file, context)




# display lessons async
@router.get("/lessons", response_class=HTMLResponse, response_model=list[LessonRead], tags=["Lesson"])
def get_lessons_html(request: Request):
    html_file = "lessons.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)




# # json: get lesson list
# @router.get("/json/lessons", response_model=list[LessonRead], tags=["Lesson"])
# def read_lesson_list_json(session:Annotated[Session, Depends(get_session)]):
#     current_time = (datetime.utcnow() + timedelta(hours=9)).replace(tzinfo=timezone(timedelta(hours=9)))
#     # utcnow()はタイムゾーン情報なしで現在のUTC時刻を取得する。9時間進めてJST時刻にして、その後タイムゾーン情報(JSTであること)を追加している。
#     if current_time < CurrentPeriod.start_time:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="lesson signup is not allowed yet")
#     lessons = session.exec(select(Lesson).where(Lesson.year == CurrentPeriod.year, Lesson.season == CurrentPeriod.season)).all()
#     return lessons



# get current lesson period infomation
def get_current_period(session: Session):
    db_period = session.exec(select(Period)).first()
    if not db_period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Period not found in the database")
    return db_period



# json: get lesson list
@router.get("/json/lessons", response_model=list[LessonRead], tags=["Lesson"])
def read_lesson_list_json(session: Annotated[Session, Depends(get_session)]):
    current_period = get_current_period(session)
    current_time = datetime.utcnow()
    if current_time < current_period.start_time:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lesson signup is not allowed yet")
    lessons = session.exec(select(Lesson).where(Lesson.year == current_period.year, Lesson.season == current_period.season)).all()
    return lessons




# json admin: get lesson list
@router.get("/json/admin/lessons", response_model=list[LessonRead], tags=["Lesson"])
def read_lesson_list_json_admin(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    current_time = datetime.utcnow()
    current_period = get_current_period(session)
    # if current_time < current_period.start_time:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="it is before test start time")
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authorized")
    lessons = session.exec(select(Lesson).where(Lesson.year == current_period.year, Lesson.season == current_period.season)).all()
    return lessons




# get: read a lesson
@router.get("/lessons/{lesson_id}", response_model=LessonRead, tags=["Lesson"])
def read_lesson(session: Annotated[Session, Depends(get_session)], lesson_id: int):
    lesson = session.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Not found")
    return lesson



# patch: update lesson information
@router.patch("/lessons/{lesson_id}", response_model=LessonRead, tags=["Lesson"])
def update_lesson(session: Annotated[Session, Depends(get_session)], lesson_id: int, lesson_update: LessonUpdate, current_user: Annotated[User, Depends(get_current_active_user)]):
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    db_lesson = session.get(Lesson, lesson_id)
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Not found")
    
    lesson_update_dict = lesson_update.model_dump(exclude_unset=True)
    
    for key, value in lesson_update_dict.items():
        setattr(db_lesson, key, value)
        
    session.add(db_lesson)
    session.commit()
    session.refresh(db_lesson)
    return db_lesson



# delete: cancel a lesson
@router.delete("/lessons/{lesson_id}", tags=["Lesson"])
def delete_lesson(session: Annotated[Session, Depends(get_session)], lesson_id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.username != "user":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed")
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(lesson)
    session.commit()
    return {"deleted": lesson}




# get: read my lessons
@router.get("/json/my/lessons", response_model=list[LessonRead], tags=["Lesson"])
def read_my_lessons(session: Annotated[Session, Depends(get_session)], current_user: Annotated[UserRead, Depends(get_current_active_user)]):
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    my_lessons = user.lessons
    return my_lessons



# post: sign up to a lessons
@router.post("/lessons/{id}", response_model=list[LessonRead], tags=["Lesson"])
def create_my_lessons(session: Annotated[Session, Depends(get_session)], current_user: Annotated[UserRead, Depends(get_current_active_user)], id: int):
    current_time = datetime.utcnow()
    current_period = get_current_period(session)
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    if current_time < current_period.start_time and not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="lesson signup is not allowed yet")
    new_lesson = session.exec(select(Lesson).where(Lesson.id == id)).one()
    if new_lesson.year != current_period.year or new_lesson.season != current_period.season:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    if not new_lesson in user.lessons:
        user.lessons.append(new_lesson)
        session.add(user)
        session.commit()
        session.refresh(user)
    if new_lesson.number == 1: # subject to change: lessons for children
        user_children = session.exec(select(UserChild).where(UserChild.user_id == user.id)).all()
        for child in user_children:
            if not new_lesson in child.lessons:
                child.lessons.append(new_lesson)
        new_lesson.capacity_left = new_lesson.capacity - len(new_lesson.user_children)
        session.add(new_lesson)
        session.commit()
        session.refresh(new_lesson)
    else:
        new_lesson.capacity_left = new_lesson.capacity - len(new_lesson.users)
        session.add(new_lesson)
        session.commit()
        session.refresh(new_lesson)
    my_lessons = user.lessons
    add_log(
        user_name=user.user_details.last_name + "　" + user.user_details.first_name,
        user_tel=user.user_details.tel,
        user_address=user.user_details.address,
        lesson_number=new_lesson.number,
        lesson_title=new_lesson.title,
        action="apply"
    )
    return my_lessons




class ChildrenIdsRequest(SQLModel):
    children_ids: list[int]


@router.post("/lessons_for_children/{lesson_id}")
def create_my_lessons_for_children(
    lesson_id: int,
    children_ids_request: ChildrenIdsRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    lesson = session.exec(select(Lesson).where(Lesson.id == lesson_id)).one()
    if lesson.number != 1:
        raise HTTPException(status_code=400, detail="invalid lesson number")

    current_period = get_current_period(session)
    if lesson.year != current_period.year or lesson.season != current_period.season:
        raise HTTPException(status_code=403, detail="invalid year or season")
    
    if len(children_ids_request.children_ids) == 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="no children selected")

    for child_id in children_ids_request.children_ids:
        user_child = session.exec(select(UserChild).where(UserChild.id == child_id)).first()
        if not user_child:
            raise HTTPException(status_code=404, detail="user child not found")
        if user_child.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="invalid child id")
        
        if not lesson in user_child.lessons:
            user_child.lessons.append(lesson)
    
    # current_user.lessons.append(lesson)
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    user.lessons.append(lesson)

    lesson.capacity_left = lesson.capacity - len(lesson.user_children)
    
    session.add(lesson)
    session.commit()
    session.refresh(lesson)
    
    add_log(
        user_name=user.user_details.last_name + "　" + user.user_details.first_name,
        user_tel=user.user_details.tel,
        user_address=user.user_details.address,
        lesson_number=lesson.number,
        lesson_title=lesson.title,
        action="apply"
    )

    return {"success": "children signed up to the lesson"}




# display my lessons async
@router.get("/my/lessons", response_class=HTMLResponse, response_model=list[LessonRead], tags=["html"])
def get_my_lessons_html(request: Request):
    html_file = "my/lessons.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)



# admin: display admin lessons async for management
@router.get("/admin/lessons", response_class=HTMLResponse, response_model=list[LessonRead], tags=["html"])
def get_admin_lessons_html(request: Request):
    html_file = "admin/lessons.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)



# delete: cancel a lesson
@router.delete("/my/lessons/{lesson_id}", tags=["Lesson"])
def delete_my_lesson(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)], lesson_id: int):
    cancel_lesson = session.get(Lesson, lesson_id)
    if not cancel_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    current_period = get_current_period(session)
    if cancel_lesson.year != current_period.year or cancel_lesson.season != current_period.season:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Outdated")
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user in cancel_lesson.users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not signed up")
    if cancel_lesson in user.lessons:
        user.lessons.remove(cancel_lesson)
        session.add(user)
        session.commit()
        session.refresh(user)
    if cancel_lesson.number == 1: # subject to change: lessons for children
        user_children = session.exec(select(UserChild).where(UserChild.user_id == user.id)).all()
        for child in user_children:
            if cancel_lesson in child.lessons:
                child.lessons.remove(cancel_lesson)
        cancel_lesson.capacity_left = cancel_lesson.capacity - len(cancel_lesson.user_children)
        session.add(cancel_lesson)
        session.commit()
        session.refresh(cancel_lesson)
        add_log(
            user_name=user.user_details.last_name + "　" + user.user_details.first_name,
            user_tel=user.user_details.tel,
            user_address=user.user_details.address,
            lesson_number=cancel_lesson.number,
            lesson_title=cancel_lesson.title,
            action="cancel"
        )
        return {"removed": cancel_lesson}
    else:
        cancel_lesson.capacity_left = cancel_lesson.capacity - len(cancel_lesson.users)
        session.add(cancel_lesson)
        session.commit()
        session.refresh(cancel_lesson)
        add_log(
            user_name=user.user_details.last_name + "　" + user.user_details.first_name,
            user_tel=user.user_details.tel,
            user_address=user.user_details.address,
            lesson_number=cancel_lesson.number,
            lesson_title=cancel_lesson.title,
            action="cancel"
        )
        return {"removed": cancel_lesson}




# admin: read user list of a lesson
@router.get("/json/admin/lessons/{lesson_id}/users", response_model=list[UserRead], tags={"Lesson"})
def admin_json_read_users_of_a_lesson(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)], lesson_id: int):
    operating_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not operating_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    # using session below
    lesson = session.exec(select(Lesson).where(Lesson.id == lesson_id)).one()
    lesson_member = lesson.users
    return lesson_member




# admin: json: read lesson member list
@router.get("/json/admin/lessons/users", tags={"Lesson"})
def admin_json_read_users_of_every_lessons(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    # if current_user.username != "user":
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    accessing_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if accessing_user.is_admin != True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    current_period = get_current_period(session)
    lessons = session.exec(select(Lesson).where(Lesson.year == current_period.year, Lesson.season == current_period.season)).all()
    lessons_users_list = []
    for lesson in lessons:
        users = []
        if lesson.number == 1:
            for child in lesson.user_children:
                parent = session.exec(select(User).where(User.id == child.user_id)).one()
                child_dict = child.model_dump()
                parent_name = parent.user_details.last_name + "　" + parent.user_details.first_name
                parent_tel = parent.user_details.tel
                parent_postal_code = parent.user_details.postal_code
                parent_address = parent.user_details.address
                child_dict["parent_name"] = parent_name
                child_dict["parent_tel"] = parent_tel
                child_dict["parent_postal_code"] = parent_postal_code
                child_dict["parent_address"] = parent_address
                users.append(child_dict)
        else:
            for user in lesson.users:
                user_details = user.user_details
                users.append(user_details)
        lessons_users_dict = {"lesson_number": lesson.number, "lesson_title": lesson.title, "users": users}
        lessons_users_list.append(lessons_users_dict)
    return lessons_users_list




# admin: display lesson member list
@router.get("/admin/lessons/users", tags={"Lesson"})
def admin_display_users_of_every_lessons(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("admin/lessonmember.html", context)




# admin: delete: remove a user from a lesson
@router.delete("/admin/users/{username}/remove/{lesson_id}", tags=["Lesson"])
def admin_remove_lesson_member(session: Annotated[Session, Depends(get_session)], username: str, lesson_id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    operating_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not operating_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    lesson = session.exec(select(Lesson).where(Lesson.id == lesson_id)).one()
    lesson_title = lesson.title
    lesson_member = lesson.users
    user = session.exec(select(User).where(User.username == username)).one()
    user_details = (user.user_details).model_dump()
    user_fullname = user_details["last_name"] + "　" + user_details["first_name"]
    if user in lesson_member:
        lesson_member.remove(user)
    # user_children = session.exec(select(UserChild).where(UserChild.user_id == user.id)).all()
    if lesson.number == 1:
        for child in user.user_children:
            if lesson in child.lessons:
                child.lessons.remove(lesson)
    session.add(lesson)
    session.commit()
    session.refresh(lesson)
    message = f"{username}：{user_fullname}を「{lesson_title}」から削除しました。"
    return {"removed done": message}



# read: lesson signup position
@router.get("/json/my/lessons/{lesson_id}/position", tags=["Lesson"])
def json_read_lesson_signup_position(session: Annotated[Session, Depends(get_session)], lesson_id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    lesson = session.exec(select(Lesson).where(Lesson.id == lesson_id)).one()
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    lesson_member = lesson.users
    if not user in lesson_member:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not signed up to this lesson")
        user_position = 0
    else:
        user_position = lesson_member.index(user) + 1
    return user_position



# read: lesson signup position
@router.get("/json/my/lessons/position", tags=["Lesson"])
def json_read_lesson_signup_position_all(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    current_period = get_current_period(session)
    lessons = session.exec(select(Lesson).where(Lesson.year == current_period.year, Lesson.season == current_period.season)).all()
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    position_list = []
    for lesson in lessons:
        lesson_member = lesson.users
        if not user in lesson_member:
            user_position = 0
        elif lesson.number != 1:
            user_position = lesson_member.index(user) + 1
        elif lesson.number == 1:
            user_children = session.exec(select(UserChild).where(UserChild.user_id == user.id)).all()
            user_position = 0
            for child in user_children:
                if child in lesson.user_children:
                    user_position = lesson.user_children.index(child) + 1
        positioon_dict = {"lesson_id": lesson.id, "user_position": user_position}
        position_list.append(positioon_dict)
    return position_list




# admin: read: lesson list of a user signed up
@router.get("/json/admin/user/{user_id}/lessons", tags=["Lesson"])
def admin_json_read_user_lesson_list(session: Annotated[Session, Depends(get_session)], user_id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    target_user = session.get(User, user_id)
    user_lessons = target_user.lessons
    return user_lessons



# admin: sign up to a lessons
@router.post("/admin/user/{user_id}/lessons/{lesson_id}", response_model=list[LessonRead], tags=["Lesson"])
def create_my_lessons(session: Annotated[Session, Depends(get_session)], current_user: Annotated[UserRead, Depends(get_current_active_user)], user_id: int, lesson_id: int):
    current_time = (datetime.utcnow() + timedelta(hours=9)).replace(tzinfo=timezone(timedelta(hours=9)))
    accessing_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not accessing_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authorized")
    new_lesson = session.exec(select(Lesson).where(Lesson.id == lesson_id)).one()
    # if new_lesson.year != 2024 or new_lesson.season != 1:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    user = session.exec(select(User).where(User.id == user_id)).one()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    if not new_lesson in user.lessons:
        user.lessons.append(new_lesson)
        session.add(user)
        session.commit()
        session.refresh(user)
    new_lesson.capacity_left = new_lesson.capacity - len(new_lesson.users)
    session.add(new_lesson)
    session.commit()
    session.refresh(new_lesson)
    user_lessons = user.lessons
    return user_lessons




# admin: temorary function
@router.get("/admin/user/{user_id}/lesson/{lesson_id}/enter-children", tags=["Lesson"])
def admin_add_children_into_lesson(session: Annotated[Session, Depends(get_session)], user_id: int, lesson_id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.username != "user":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    if lesson_id != 1:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="lesson_id must be 1")
    # using session below
    user = session.get(User, user_id)
    user_children = user.user_children
    lesson = session.get(Lesson, lesson_id)
    if user in lesson.users:
        for child in user_children:
            if not child in lesson.user_children:
                child.lessons.append(lesson)
        lesson.capacity_left = lesson.capacity - len(lesson.user_children)
        session.add(lesson)
        session.commit()
        session.refresh(lesson)
        return {"children signed up to the lesson": "done"}
    else:
        return {"parent user has not signed up to the lesson": "ignored"}



# admin: temorary function username ver
@router.get("/admin/user/{username}/lesson/{lesson_id}/enter-children-username-ver", tags=["Lesson"])
def admin_add_children_into_lesson_username_ver(session: Annotated[Session, Depends(get_session)], username: str, lesson_id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.username != "user":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    if lesson_id != 1:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="lesson_id must be 1")
    # using session below
    user = session.exec(select(User).where(User.username == username)).one()
    user_children = user.user_children
    lesson = session.get(Lesson, lesson_id)
    if user in lesson.users:
        for child in user_children:
            if not child in lesson.user_children:
                child.lessons.append(lesson)
        lesson.capacity_left = lesson.capacity - len(lesson.user_children)
        session.add(lesson)
        session.commit()
        session.refresh(lesson)
        return {"children signed up to the lesson": "done"}
    else:
        return {"parent user has not signed up to the lesson": "ignored"}




# get: refresh lesson capacity
@router.get("/lessons/refresh/capacity", tags=["Lesson"])
def refresh_lesson_capacity_left(session: Annotated[Session, Depends(get_session)]):
    current_period = get_current_period(session)
    lessons = session.exec(select(Lesson).where(Lesson.year == current_period.year, Lesson.season == current_period.season)).all()
    for lesson in lessons:
        if lesson.number == 1:
            lesson.capacity_left = lesson.capacity - len(lesson.user_children)
        else:
            lesson.capacity_left = lesson.capacity - len(lesson.users)
        session.add(lesson)
    session.commit()
    for lesson in lessons:
        session.refresh(lesson)
    return lessons



# get: json list of lesson applicants
@router.get("/json/lessons/{lesson_id}/applicants", tags=["Lesson"])
def json_read_lesson_applicants(lesson_id: int, session: Annotated[Session, Depends(get_session)], key: str = None):
    if key is None or not key == PUBLIC_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authorized")
    lesson = session.exec(select(Lesson).where(Lesson.id == lesson_id)).one()
    result = []
    if lesson.number == 1:
        children = lesson.user_children
        counter = 1
        for child in children:
            user_details = child.user.user_details
            child_details_out = {
                "No.": counter,
                "name": child.child_last_name + "　" + child.child_first_name,
                "furigana": child.child_last_name_furigana + "　" + child.child_first_name_furigana,
                "parent": user_details.last_name + "　" + user_details.first_name,
                "tel": user_details.tel,
                "address": user_details.address
                }
            counter = counter + 1
            result.append(child_details_out)
    else:
        users = lesson.users
        counter = 1
        for user in users:
            user_details = user.user_details
            user_details_out = {"No.": counter, "name": (user_details.last_name + "　" + user_details.first_name), "tel": user_details.tel, "address": user_details.address}
            counter = counter + 1
            result.append(user_details_out)
    return result



# get: json list of lessons that each user signed up
@router.get("/json/users/lessons", tags=["Lesson"])
def json_read_lessons_each_user_applied(session: Annotated[Session, Depends(get_session)], key: str = None):
    if key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authorized")
    elif not key == PUBLIC_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authorized")
    users = session.exec(select(User)).all()
    result = []
    for user in users:
        user_details = user.user_details
        lessons = user.lessons
        lessons_out = []
        for lesson in lessons:
            one_lesson = str(lesson.number) + ":" + lesson.title + "(" + str(lesson.year) + "_" + str(lesson.season) + ")"
            lessons_out.append(one_lesson)
        lessons_season1 = [lesson for lesson in lessons if lesson.season == 1]
        lessons_season2 = [lesson for lesson in lessons if lesson.season == 2]
        one_user = {"#": user.id,
                    "名前": (user_details.last_name + "　" + user_details.first_name),
                    "ふりがな": (user_details.last_name_furigana + "　" + user_details.first_name_furigana),
                    "前期": len(lessons_season1),
                    "後期": len(lessons_season2),
                    "Tel": user_details.tel,
                    "住所": user_details.address,
                    "申し込んだ教室": str(lessons_out),
                    }
        result.append(one_user)
    return result






# post: admin: create lessons via spreadsheet GAS API
@router.post("/json/admin/lessons/create")
def json_admin_create_lessons(lessons_create: list[LessonCreate], session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if user is None or not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authorized")
    # print(lessons_create)
    # session.add_all(lessons_create) # this fails
    for lesson_create in lessons_create:
        db_lesson = Lesson.model_validate(lesson_create)
        session.add(db_lesson)
    session.commit()
    return {"ok": "done"}




# json: get my user children in current lesson
@router.get("/json/my/children_in_current_lesson", tags=["Lesson"], response_model=list[UserChildRead])
def json_get_my_children_in_current_lesson(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_active_user)]
    ):
    current_period = get_current_period(session)
    children = session.exec(select(UserChild).where(UserChild.user_id == current_user.id)).all()
    children_in_current_lesson = []
    for child in children:
        for lesson in child.lessons:
            if lesson.year == current_period.year and lesson.season == current_period.season:
                children_in_current_lesson.append(child)
    return children_in_current_lesson




# json send message to lesson applicants
@router.get("/json/confirmation_message/lesson/{lesson_number}")
def json_confirmation_message_lesson(
    session: Annotated[Session, Depends(get_session)],
    lesson_number: int,
    key: str = None
):
    if key != PUBLIC_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authorized")
    current_period = get_current_period(session)
    lesson = session.exec(select(Lesson).where(Lesson.year == current_period.year, Lesson.season == current_period.season, Lesson.number == lesson_number)).first()
    user_list = lesson.users
    child_list = []
    if lesson.number == 1:
        child_list = lesson.user_children
    message_list = []
    number_symbol = ["None","①", "②", "③", "④", "⑤", "⑥", "⑦","⑧", "⑨", "⑩", "⑪", "⑫", "⑬"]
    first_date_list = ["初回日", "10/10(金)", "10/8(水)", "10/8(水)", "10/2(木)", "10/9(木)", "10/9(木)", "10/10(金)", "10/2(木)", "10/9(木)", "10/2(木)13:30", "10/2(木)14:30", "10/9(木)13:30", "10/9(木)14:30"]
    # print(lesson.number, lesson_number)
    for user in user_list:
        lesson_title = number_symbol[lesson.number] + lesson.title
        first_date = first_date_list[lesson.number]
        lesson_children = [child.child_last_name + " " + child.child_first_name for child in child_list if child.user_id == user.id]
        lesson_price_str = str(lesson.price) + "円x" + str(len(lesson_children)) + "人分" if lesson.number == 1 else str(lesson.price) + "円"
        message_format = {
            "name": user.user_details.last_name + " " + user.user_details.first_name,
            "tel": user.user_details.tel,
            "lesson_title": lesson_title,
            "fee": lesson_price_str,
            "children": lesson_children,
            "message": "後期教室" + lesson_title + "が" + first_date + "から始まります。初回に参加費" + lesson_price_str + "をお願いします。\n養老スポーツクラブ　若山"
        }
        message_list.append(message_format)
    return message_list

