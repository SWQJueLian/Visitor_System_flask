from datetime import datetime

from app import db


class BaseModel(db.Model):
    __abstract__ = True  # 声明这是一个抽象的基类，不需要创建表
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
