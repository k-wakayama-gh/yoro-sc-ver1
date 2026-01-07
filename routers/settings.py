# routers/period.py

# modules
from fastapi import APIRouter, Request, Header, Body, HTTPException, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, select
from typing import Optional, Annotated, Dict
from datetime import datetime, timedelta, timezone

# my modules
from database import engine, get_session
from models.users import User
from routers.auth import get_current_active_user
from models.settings import Period, PeriodRequest

# instance of API router and templates
router = APIRouter()
templates = Jinja2Templates(directory="templates")



# 期間情報取得
@router.get("/admin/period", response_model=Period)
def get_period(session: Annotated[Session, Depends(get_session)]):
    period = session.exec(select(Period)).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    
    # # JSTのタイムゾーンを追加する（コピーを作って返す）
    # JST = timezone(timedelta(hours=9))
    # period.start_time = period.start_time.astimezone(JST)
    # period.end_time = period.end_time.astimezone(JST)
    # # print(period.start_time, period.start_time.tzinfo)

    # JSTに変換（タイムゾーン情報なし）
    period.start_time = (period.start_time + timedelta(hours=9)).replace(tzinfo=None)
    period.end_time = (period.end_time + timedelta(hours=9)).replace(tzinfo=None)
    return period



def dict_to_datetime(date_dict: Dict[str, int]) -> datetime:
    JST = timezone(timedelta(hours=9))  # JST (UTC +9) のタイムゾーンを定義
    # JSTで日時を作成し、それをUTCに変換
    dt = datetime(
        date_dict["year"],
        date_dict["month"],
        date_dict["day"],
        date_dict["hour"],
        date_dict["minute"],
        tzinfo=JST
    )
    return dt.astimezone(timezone.utc)  # UTCに変換



# 期間情報設定
@router.put("/admin/period", response_model=PeriodRequest)
def upsert_period(
    period_request: PeriodRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    # 現在のユーザーが管理者かをチェック
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    
    # start_timeとend_timeをdatetimeに変換
    start_time = dict_to_datetime(period_request.start_time)
    end_time = dict_to_datetime(period_request.end_time)

    # Periodモデルに変換
    period = Period(
        year=period_request.year,
        season=period_request.season,
        start_time=start_time,
        end_time=end_time
    )

    # 既存の期間情報を取得
    db_period = session.exec(select(Period)).first()

    if db_period:  # 既存データを更新
        db_period.year = period.year
        db_period.season = period.season
        db_period.start_time = period.start_time
        db_period.end_time = period.end_time
    else:  # 新規データを挿入
        db_period = period
        session.add(db_period)

    try:
        session.commit()  # コミット
        session.refresh(db_period)  # 更新後のデータを再取得
    except Exception as e:
        session.rollback()  # エラー時はロールバック
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return period_request  # クライアントに送るレスポンスとしてPeriodRequestを返す




# admin: period setting page
@router.get("/admin/settings", response_class=HTMLResponse, tags=["html"])
def get_period_html_admin(request: Request):
    html_file = "admin/settings.html"
    context = {
        "request": request,
    }
    return templates.TemplateResponse(html_file, context)


