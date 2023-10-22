from datetime import datetime

import pytz
from sqlalchemy_serializer import SerializerMixin
from app import db


class BaseModel(db.Model, SerializerMixin):
    ch_tz = pytz.timezone('Asia/Shanghai')
    __abstract__ = True  # 声明这是一个抽象的基类，不需要创建表
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(ch_tz))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(ch_tz), default=datetime.now(ch_tz))
