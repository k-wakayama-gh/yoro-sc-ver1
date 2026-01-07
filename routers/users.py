# routers/users.py

# modules
from fastapi import APIRouter, Request, Header, Body, HTTPException, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, select
from typing import Optional, Annotated
from sqlalchemy.orm import selectinload

# my modules
from database import engine, get_session
from models.items import Item, ItemCreate, ItemRead, ItemUpdate, ItemDelete
from models.users import User, UserCreate, UserRead, UserUpdate, UserDelete, UserIn, UserInDB, UserDetail, UserWithUserDetailCreate, UserDetailRead, UserDetailUsernameRead, UserDetailCreate, UserChild, UserChildCreate, UserChildRead
from routers.auth import get_hashed_password
from routers.auth import get_current_active_user

# instance of API router and templates
router = APIRouter()
templates = Jinja2Templates(directory="templates")



# create User model from UserIn model converting plain password into hashed password
def create_db_user(user_in: UserIn):
    hashed_password = get_hashed_password(user_in.plain_password)
    db_user = User(**user_in.model_dump(), hashed_password=hashed_password)
    # db_user = User(**user_in.dict(), hashed_password=hashed_password) # dict() => model_dump()
    return db_user



# # create: user without details
# @router.post("/users", response_model=UserRead, tags=["User"])
# def create_user(user_in: UserIn):
#     with Session(engine) as session:
#         db_user = create_db_user(user_in)
#         session.add(db_user)
#         session.commit()
#         session.refresh(db_user)
#         return db_user



# create: user with user_details
@router.post("/users/signup", response_model=UserRead, tags=["User"])
def create_user_with_details(session: Annotated[Session, Depends(get_session)], user_in: UserWithUserDetailCreate):
    username = user_in.username
    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="The username already exists")
    db_user = create_db_user(user_in)
    db_user_details = create_db_user_details(user_in)
    db_user.user_details = db_user_details
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    db_user.user_details.user_id = db_user.id
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# create user with details converting plain password into hashed password
def create_db_user_with_details(user_in: UserWithUserDetailCreate):
    hashed_password = get_hashed_password(user_in.plain_password)
    db_user = User(**user_in.model_dump(), hashed_password=hashed_password)
    return db_user

# return user details
def create_db_user_details(user_in: UserWithUserDetailCreate):
    db_user_details = UserDetail(**user_in.model_dump())
    return db_user_details



# admin: read: children
@router.get("/user/{user_id}/children", tags=["User"])
def admin_read_user_children(session: Annotated[Session, Depends(get_session)], user_id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    operating_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not operating_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    user = session.exec(select(User).where(User.id == user_id)).one()
    children = user.user_children
    return children



# create: my user children
@router.post("/my/children", tags=["User"])
def create_my_user_children(session: Annotated[Session, Depends(get_session)], children: list[UserChildCreate], current_user: Annotated[User, Depends(get_current_active_user)]):
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    for child in children:
        child = UserChild.model_validate(child)
        user.user_children.append(child)
    session.add(user)
    session.commit()
    session.refresh(user)
    for child in user.user_children:
        child.user_id = user.id
    session.add(user)
    session.commit()
    session.refresh(user)
    return children



# delete: my user children
@router.delete("/my/children{child_id}", tags=["User"])
def delete_my_user_children(session: Annotated[Session, Depends(get_session)], child_id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Require login")
    child = session.exec(select(UserChild).where(UserChild.id == child_id and UserChild.user_id == user.id)).first()
    if child is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    session.delete(child)
    session.commit()
    return {"removed": "done"}


# admin: delete: children
@router.delete("/user/{user_id}/children/{child_id}", tags=["User"])
def admin_delete_user_children(session: Annotated[Session, Depends(get_session)], user_id: int, child_id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    operating_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not operating_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    user = session.exec(select(User).where(User.id == user_id)).one()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    child = session.exec(select(UserChild).where(UserChild.id == child_id and UserChild.user_id == user.id)).first()
    session.delete(child)
    session.commit()
    return {"removed": "done"}



# json: admin: read user list
@router.get("/json/admin/users", response_model=list[UserRead], tags=["User"])
def read_users_list(*, offset: int = 0, limit: int = Query(default=100, le=100), session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    operating_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not operating_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    # if not users:
    #     raise HTTPException(status_code=404, detail="Not found") # rather than this it should return empty list if no users
    return users



# json: admin: read user list with data
@router.get("/json/admin/users-full", tags=["User"])
def read_users_list(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    operating_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not operating_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    users = session.exec(select(User)).all()
    result = []
    for user in users:
        one = {"id": user.id,
               "username": user.username,
               "name": user.user_details.last_name + user.user_details.first_name,
               "furigana": user.user_details.last_name_furigana + user.user_details.first_name_furigana,
               "tel": user.user_details.tel,
               "lessons": len(user.lessons),
               }
        result.append(one)
    return result



# read one
@router.get("/user/{username}", response_model=UserRead, tags=["User"])
def read_user(session: Annotated[Session, Depends(get_session)], username: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    user = session.exec(select(User).where(User.username == username)).one()
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    if current_user.username != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return user



# json: admin: read user with user details
@router.get("/json/admin/users/details/{username}", response_model=UserDetailUsernameRead, tags=["User"])
def read_user_details(username: str, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    operating_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not operating_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    user = session.exec(select(User).where(User.username == username)).one()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    user_details = user.user_details
    user_details_dict = user_details.model_dump()
    user_details_dict["username"] = user.username
    return user_details_dict



# admin: patch: username password and is_admin
@router.patch("/admin/users/{username}", response_model=UserRead, tags=["User"])
def patch_user(session: Annotated[Session, Depends(get_session)], username: str, user_update: UserUpdate, current_user: Annotated[User, Depends(get_current_active_user)]):
    operating_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not operating_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    # db_user = session.get(User, user_id)
    user = session.exec(select(User).where(User.username == username)).one()
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    user_update_dict = user_update.model_dump(exclude_unset=True) # pydantic型をdict型に変換してNULLなデータを除外する
    if user_update.plain_password:
        hashed_password = get_hashed_password(user_update.plain_password)
        user_update_dict.pop("plain_password")
        user_update_dict["hashed_password"] = hashed_password
    for key, value in user_update_dict.items():
        setattr(user, key, value) # user_dataのkey, valueをdb_userに割り当てる => 送られてきたuser_updateでNULLでないデータだけを上書きする
    session.add(user)
    session.commit()
    session.refresh(user)
    return user



# admin: patch: user details
@router.patch("/admin/userdetails/{username}", tags=["User"], response_model=UserDetailUsernameRead)
def patch_userdetails(username: str, new_user_details: UserDetailCreate, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    operating_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not username == current_user.username and not operating_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    user = session.exec(select(User).where(User.username == username)).one()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_details = user.user_details
    proper_new_user_details = new_user_details.model_dump(exclude_unset=True)
    for key, value in proper_new_user_details.items():
        setattr(user_details, key, value)
    session.add(user)
    session.commit()
    session.refresh(user_details)
    user_details_out = user_details.model_dump()
    user_details_out["username"] = username
    return user_details_out


# patch: my user details
@router.patch("/my/userdetails", tags=["User"], response_model=UserDetailUsernameRead)
def patch_my_userdetails(new_user_details: UserDetailCreate, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    # operating_user = session.exec(select(User).where(User.username == current_user.username)).one()
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    user_details = user.user_details
    db_new_user_details = new_user_details.model_dump(exclude_unset=True)
    for key, value in db_new_user_details.items():
        setattr(user_details, key, value)
    session.add(user)
    session.commit()
    session.refresh(user_details)
    user_details_out = user_details.model_dump()
    user_details_out["username"] = current_user.username
    return user_details_out



# delete: user with details
@router.delete("/users/delete/{username}", tags=["User"])
def delete_user(username: str, session:Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    operating_user = session.exec(select(User).where(User.username == current_user.username)).one()
    if current_user.username != username and not operating_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    user = session.exec(select(User).where(User.username == username)).one()
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    user_details = session.exec(select(UserDetail).where(UserDetail.user_id == user.id)).one()
    session.delete(user)
    session.delete(user_details)
    session.commit()
    return {"deleted": user.username}





# json: return username
@router.get("/my/username", tags=["User"])
def get_username(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    username = current_user.username
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return username




# json: get my user details
@router.get("/json/my/userdetails", tags=["User"], response_model=UserDetailUsernameRead)
def json_get_my_userdetails(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    user_details = session.exec(select(UserDetail).where(UserDetail.user_id == user.id)).one()
    user_details_dict = user_details.model_dump() # dict型に変更
    user_details_dict["username"] = current_user.username
    return user_details_dict



# json: get my user children
@router.get("/json/my/children", tags=["User"], response_model=list[UserChildRead])
def json_get_my_children(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    children = session.exec(select(UserChild).where(UserChild.user_id == user.id)).all()
    return children



# display user details
@router.get("/my/userdetails", response_class=HTMLResponse, tags=["html"])
def get_my_user_details_html(request: Request):
    html_file = "my/userdetails.html"
    context = {
        'request': request,
    }
    return templates.TemplateResponse(html_file, context)



# children signup page
@router.get("/my/childrensignup", response_class=HTMLResponse, tags=["html"])
def get_children_signup_page_html(request: Request):
    html_file = "my/childrensignup.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)



# admin: display: users
@router.get("/admin/users", response_class=HTMLResponse, tags=["html"])
def get_users_html_admin(request: Request):
    html_file = "admin/users.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)



@router.get("/json/admin/users", tags=["User"])
def admin_get_user_list_json(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)]):
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    user_details = session.exec(select(UserDetail)).all()
    return user_details


@router.get("/json/admin/users/search_pre", tags=["User"])
def  admin_user_search_pre(session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_active_user)], last_name_furigana: str = None, first_name_furigana: str = None):
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
    if last_name_furigana and not first_name_furigana:
        user_details = session.exec(select(UserDetail).where(UserDetail.last_name_furigana == last_name_furigana)).all()
    elif not last_name_furigana and first_name_furigana:
        user_details = session.exec(select(UserDetail).where(UserDetail.first_name_furigana == first_name_furigana)).all()
    elif last_name_furigana and first_name_furigana:
        user_details = session.exec(select(UserDetail).where(UserDetail.last_name_furigana == last_name_furigana and UserDetail.first_name_furigana == first_name_furigana)).all()
    return user_details



@router.get("/json/admin/users/search", tags=["User"])
def admin_user_search(
    session: Annotated[Session, Depends(get_session)], 
    current_user: Annotated[User, Depends(get_current_active_user)], 
    last_name_furigana: str = None, 
    first_name_furigana: str = None
):
    # 現在のユーザーが管理者であることを確認
    user = session.exec(select(User).where(User.username == current_user.username)).one()
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")

    # UserDetailのリストを取得する
    if last_name_furigana and not first_name_furigana:
        user_details = session.exec(select(UserDetail).where(UserDetail.last_name_furigana == last_name_furigana)).all()
    elif not last_name_furigana and first_name_furigana:
        user_details = session.exec(select(UserDetail).where(UserDetail.first_name_furigana == first_name_furigana)).all()
    elif last_name_furigana and first_name_furigana:
        user_details = session.exec(select(UserDetail).where(UserDetail.last_name_furigana == last_name_furigana and UserDetail.first_name_furigana == first_name_furigana)).all()

    # 各UserDetailのuser_idを使って対応するUserを取得し、必要な情報を追加
    response = []
    for detail in user_details:
        # user_idを使ってUserを取得
        user = session.exec(select(User).where(User.id == detail.user_id)).one_or_none()

        if user:
            # Userの情報をUserDetailに追加
            user_info = {
                "user_id": detail.user_id,
                "username": user.username,
                "user_children": [
                    {"user_child_id": child.id, "first_name": child.child_first_name, "last_name": child.child_last_name}
                    for child in user.user_children
                ] if user.user_children else []
            }
            
            # UserDetailの他の情報を追加
            user_info.update({
                "email": detail.email,
                "first_name": detail.first_name,
                "last_name": detail.last_name,
                "first_name_furigana": detail.first_name_furigana,
                "last_name_furigana": detail.last_name_furigana,
                "tel": detail.tel,
                "postal_code": detail.postal_code,
                "address": detail.address,
                "created_time": detail.created_time,
                "lessons": len(user.lessons)
            })

            # レスポンスリストに追加
            response.append(user_info)
    
    return response




# admin: user serch page
@router.get("/admin/user_search", response_class=HTMLResponse, tags=["html"])
def get_user_search_html_admin(request: Request):
    html_file = "admin/user_search.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)



# edit my user details information
@router.get("/my/userdetails/edit", response_class=HTMLResponse, tags=["html"])
def get_edit_my_userdetails_html(request: Request):
    html_file = "my/userdetails/edit.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)


