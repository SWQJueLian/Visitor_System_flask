from datetime import datetime

from pytz import timezone
from sqlalchemy_serializer import SerializerMixin

from app import db


class BaseModel(db.Model, SerializerMixin):
    tz_shanghai = timezone("Asia/Shanghai")
    __abstract__ = True  # 声明这是一个抽象的基类，不需要创建表
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(tz_shanghai), timezone=True)
    updated_at = db.Column(
        db.DateTime, onupdate=datetime.now(tz_shanghai), default=datetime.now(tz_shanghai), timezone=True
    )
