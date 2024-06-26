import os
import time
from datetime import date, timedelta, datetime, timezone
from decimal import Decimal
from io import BytesIO
from typing import Annotated

import xlsxwriter
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette.responses import Response

from data.models import User, Order
from data.schemas import OrderSchema, OrderStatusUpdateSchema, StatsAggregateSchema
from utils import crud
from utils.dependencies import get_current_user, get_db

router = APIRouter()


@router.get("/settings/update", response_model=str)
def update_settings(key: str, value: str, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if "admin.manage" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.update_settings(db, key, value)


@router.get("/orders/available", response_model=list[OrderSchema])
def available_orders(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if "admin.manage" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.get_available_orders(db)


@router.patch("/order", response_model=OrderSchema)
def update_order_status(data: OrderStatusUpdateSchema, user: Annotated[User, Depends(get_current_user)],
                        db: Session = Depends(get_db)):
    order = crud.ensure_not_none(crud.get_order(db, data.id))
    if "admin.manage" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    crud.update_order_status(db, order, data.status)
    return order


stats_last_cached = {"day": 0, "week": 0, "month": 0, "year": 0, "individual": 0}
stats_cache = {"day": None, "week": None, "month": None, "individual": None}
stats_last_limit = 0


def get_statistics(by: str, limit: int, db: Session) -> StatsAggregateSchema:
    global stats_last_cached, stats_cache, stats_last_limit
    if time.time() - stats_last_cached[by] < 1200 and stats_cache[by] is not None and stats_last_limit == limit:
        return stats_cache[by]
    stats_last_limit = limit

    def get_start_of_week(date):
        return date - timedelta(days=date.weekday())

    def get_start_of_month(date):
        return datetime(date.year, date.month, 1)

    if by == "week":
        get_start_date = get_start_of_week
    elif by == "month":
        get_start_date = get_start_of_month
    else:  # Default to by day
        get_start_date = lambda x: x

    orders = db.query(Order).filter(Order.createdTime >= (datetime.now() - timedelta(days=limit))).order_by(
        Order.createdTime.desc()).all()
    revenue = {}
    orders_count = {}
    unique_users = {}
    cups = {}
    for order in orders:
        if by == "individual":
            day = order.createdTime.strftime("%Y-%m-%d %H:%M:%S")
        else:
            day = get_start_date(order.createdTime).strftime("%Y-%m-%d")
        if day in revenue:
            revenue[day] += order.totalPrice
        else:
            revenue[day] = Decimal(order.totalPrice)

        if day in orders_count:
            orders_count[day] += 1
        else:
            orders_count[day] = 1

        cup = 0
        for item in order.items:
            cup += item.amount
        if day in cups:
            cups[day] += cup
        else:
            cups[day] = cup

        if day not in unique_users:
            unique_users[day] = set()
        unique_users[day].add(order.userId)

    for day, users in unique_users.items():
        unique_users[day] = len(users)

    today = date.today()

    start_of_day = datetime.combine(date.today(), datetime.min.time())
    end_of_day = datetime.combine(date.today(), datetime.max.time())
    start_of_week = get_start_of_week(today)
    end_of_week = start_of_week + timedelta(days=6)

    today_revenue = 0
    today_orders = 0
    today_cups = 0
    today_unique_users = set()
    week_revenue = 0

    for order in db.query(Order).filter(Order.createdTime >= start_of_day, Order.createdTime <= end_of_day).all():
        today_revenue += order.totalPrice
        today_orders += 1
        for item in order.items:
            today_cups += item.amount
        today_unique_users.add(order.userId)

    for order in db.query(Order).filter(Order.createdTime >= start_of_week, Order.createdTime <= end_of_week).all():
        week_revenue += order.totalPrice

    stats_last_cached[by] = time.time()
    stats_cache[by] = StatsAggregateSchema(
        todayRevenue=today_revenue,
        todayOrders=today_orders,
        todayCups=today_cups,
        todayUniqueUsers=len(today_unique_users),
        weekRevenue=week_revenue,
        weekRevenueRange=f"{start_of_week.strftime('%Y-%m-%d')} - {end_of_week.strftime('%Y-%m-%d')}",
        revenue=revenue,
        orders=orders_count,
        cups=cups,
        uniqueUsers=unique_users
    )
    return stats_cache[by]


@router.get("/statistics/export/token", response_model=str)
def statistics_export_token(by: str, limit: int, user: Annotated[User, Depends(get_current_user)]):
    if "admin.statistics" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    return jwt.encode({"type": "statsExport", "by": by, "limit": limit, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}, key=os.environ["JWT_SECRET_KEY"], algorithm="HS256")


@router.get("/statistics/export")
def statistics_export(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, os.environ["JWT_SECRET_KEY"], algorithms=["HS256"])
        if payload["type"] != "statsExport":
            raise HTTPException(status_code=403, detail="Invalid export token")
        by = payload["by"]
        limit = payload["limit"]
    except JWTError | KeyError:
        raise HTTPException(status_code=403, detail="Invalid export token")
    stats = get_statistics(by, limit, db)

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    revenue = workbook.add_worksheet("Total Revenue")
    orders = workbook.add_worksheet("Orders")
    cups = workbook.add_worksheet("Cups")
    unique_users = workbook.add_worksheet("Unique Users")

    row = 1
    revenue.write(0, 0, "Total Revenue (From start of each time interval)")
    for ts, r in stats.revenue.items():
        revenue.write(row, 0, ts)
        revenue.write(row, 1, str(r))
        row += 1

    row = 1
    orders.write(0, 0, "Orders (From start of each time interval)")
    for ts, o in stats.orders.items():
        orders.write(row, 0, ts)
        orders.write(row, 1, str(o))
        row += 1

    row = 1
    cups.write(0, 0, "Cups (From start of each time interval)")
    for ts, c in stats.cups.items():
        cups.write(row, 0, ts)
        cups.write(row, 1, str(c))
        row += 1

    row = 1
    unique_users.write(0, 0, "Unique Users (From start of each time interval)")
    for ts, u in stats.uniqueUsers.items():
        unique_users.write(row, 0, ts)
        unique_users.write(row, 1, str(u))
        row += 1

    workbook.close()
    return Response(
        output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "inline; filename=\"exported-stats.xlsx\""
        }
    )


@router.get("/statistics", response_model=StatsAggregateSchema)
def statistics(by: str, user: Annotated[User, Depends(get_current_user)], limit: int = 90, db: Session = Depends(get_db)):
    if "admin.statistics" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    return get_statistics(by, limit, db)
