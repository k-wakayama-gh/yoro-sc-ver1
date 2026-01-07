# --- routers/items.py ---

# modules
from fastapi import FastAPI, APIRouter, Request, Header, Body, HTTPException, Depends, Query, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, select
from typing import Optional, Annotated

# my modules
from database import engine, get_session
from models.items import Item, ItemCreate, ItemRead, ItemUpdate, ItemDelete
from models.users import User, UserCreate, UserRead, UserUpdate, UserDelete

# API router
router = APIRouter()

# templates settings
templates = Jinja2Templates(directory='templates')

class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, offset: int = 0, limit: int = Query(default=100, le=100)):
        self.q = q
        self.offset = offset
        self.limit = limit




# create
@router.post("/items", response_model=ItemRead, tags=["Item"])
def create_item(*, session: Session = Depends(get_session), item: ItemCreate):
    # create_item(item: ItemCreate, session: Session = Depends(get_session)) 値持ちがあとなら*は不要
    #db_item = item => This doesnt work.
    #db_item = Item.model_validate(item) => requires SQLModel version above 0.0.14
    db_item = Item.from_orm(item)
    #db_item = Item(**item.dict()) => Uses pure python method.
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item



# read list
# @router.get("/items", response_model=list[ItemRead], tags=["Item"])
# def read_items_list(*, session: Session = Depends(get_session), offset: int = 0, limit: int = Query(default=100, le=100)):
#     items = session.exec(select(Item).offset(offset).limit(limit)).all()
#     if not items:
#         raise HTTPException(status_code=404, detail="Not found")
#     return items


# read list
@router.get("/items", response_model=list[ItemRead], tags=["Item"])
def read_items_list(commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)], session: Annotated[Session, Depends(get_session)]):
    #この場合はAnnotated[Any, Depends(CommonQueryParams)]でもAnnotated[CommonQueryParams, Depends()]でもいい
    items = session.exec(select(Item).offset(commons.offset).limit(commons.limit)).all()
    if not items:
        raise HTTPException(status_code=404, detail="Not found")
    return items




# read one
@router.get("/items/{item_id}", response_model=ItemRead, tags=["Item"])
def read_item(*, session: Session = Depends(get_session), item_id: int):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item



# update
@router.patch("/items/{item_id}", response_model=ItemRead, tags=["Item"])
def update_item(*, session: Session = Depends(get_session), item_id: int, item: ItemUpdate):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item



# delete
@router.delete("/items/{item_id}", tags=["Item"])
def delete_item(*, session: Session = Depends(get_session), item_id: int):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(item)
    session.commit()
    return {"ok": True}


