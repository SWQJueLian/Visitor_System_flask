import shortuuid
import sqlalchemy as sa

from app import db
from app.api.models import BaseModel


class Invite(BaseModel):
    class Status:
        NOT_VISITED = 0  # 未到访
        VISITED = 1  # 已到访
        EXPIRED = 2  # 已过期

    __tablename__ = "t_invite"

    id = sa.Column(sa.String(100), primary_key=True, default=shortuuid.uuid)
    # 关联关系
    employee_id = sa.Column(sa.String(100), sa.ForeignKey("t_employee.employee_id"))
    employee = db.relationship("Employee", back_populates="invites")
    visitor_name = sa.Column(sa.String(20), nullable=False)
    visitor_mobile = sa.Column(sa.String(11), nullable=False)
    visitor_num = sa.Column(sa.SmallInteger, default=1, nullable=False)
    visit_date = sa.Column(sa.DateTime, nullable=False)
    visitor_car_number = sa.Column(sa.String(10), nullable=True)
    visitor_reason = sa.Column(sa.String(50), nullable=True)
    visitor_unit = sa.Column(sa.String(20), nullable=True)
    status = sa.Column(sa.SmallInteger, default=Status.NOT_VISITED)


class Employee(BaseModel):
    __tablename__ = "t_employee"

    # 这个必须排除，不然会递归序列化，然后就崩了
    serialize_rules = ("-invites",)

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    employee_id = sa.Column(
        sa.String(100),
        nullable=False,
        unique=True,
        index=True,
        doc="员工ID",
        comment="员工ID",
    )
    employee_name = sa.Column(sa.String(20), nullable=False, doc="员工姓名", comment="员工姓名")
    employee_department = sa.Column(
        sa.String(20), nullable=False, doc="员工所属部门名", comment="员工所属部门名"
    )

    # 关联关系
    invites = db.relationship("Invite", back_populates="employee")
