from datetime import datetime

import pytz
import sqlalchemy as sa
from flask_restful import abort
from sqlalchemy.orm import load_only

from app import db
from app.modules.invite.models import Invite


def invite_get_all(filter_data):
    """根据搜索关键词、时间、员工id列出邀请"""
    filter_kw = [Invite.employee_id == filter_data["employee_id"]]
    # 如果有时间日期过滤就加上。
    # 这里要用来做下拉刷新和上拉瀑布流加载
    if filter_data.get("datetime"):
        filter_kw.append(Invite.created_at < filter_data.get("datetime"))
    # 如果有关键词过滤就加上。

    filter_or_kw = []
    if filter_data.get("keyword"):
        filter_or_kw = [
            Invite.visitor_name.contains(filter_data.get("keyword")),
            Invite.visitor_mobile.contains(filter_data.get("keyword")),
        ]

    # 减少不必要的字段查询
    invite_list = db.session.scalars(
        sa.select(Invite)
        .where(*filter_kw, sa.or_(*filter_or_kw))
        .limit(filter_data.get("limit", 20))
        .options(
            load_only(
                Invite.id,
                Invite.visitor_name,
                Invite.visitor_mobile,
                Invite.visit_date,
                Invite.created_at,
                Invite.status,
            )
        )
    ).all()

    return invite_list


def invite_save(employee_id, validated_data: dict):
    """添加邀请"""
    invite = Invite(**validated_data, employee_id=employee_id)

    db.session.add(invite)
    db.session.commit()

    return invite


def invite_update_by_employee(employee_id, invite_id, validated_data: dict):
    """根据员工id更新邀请信息"""
    db.session.execute(
        sa.update(Invite).where(Invite.id == invite_id, Invite.employee_id == employee_id).values(**validated_data)
    )
    db.session.commit()


def invite_visitor_arrive(invite_id):
    """访客到达，更新邀请中的状态信息"""
    invite: Invite = db.session.execute(
        sa.select(Invite).where(Invite.id == invite_id).options(load_only(Invite.status, Invite.visit_date))
    ).scalar()

    if invite is None:
        abort(404)

    ch_tz = pytz.timezone("Asia/Shanghai")
    # 把时区添加上去，因为取出来又不带时区信息。
    if ch_tz.localize(invite.visit_date).date() != datetime.now(ch_tz).date():
        raise Exception("来访日期与当前日期不相等")
    # 访客到达不应该从前端中接受status作为arg进行更新数据库中的状态，而且用从类似常量的方式读取并写入
    invite.status = Invite.Status.VISITED
    db.session.commit()

    return invite
