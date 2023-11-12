from datetime import timedelta

import sqlalchemy as sa
from utils.jwt_tools import generate_token

from app import db
from app.modules.invite.models import Employee
from app.modules.oauth.tools.wxwork_tools import WXWorkApi


def wxwork_get_userinfo(code: str):
    wxwork_api = WXWorkApi()

    # 1. 获取用户信息
    userid = wxwork_api.get_basic_userinfo(code).get("UserId")
    if userid is None:
        raise Exception("获取用户基本信息userid出错")

    # 拿到userid后就可以获取用户详情信息，
    # 1.1 获取用户的主部门id
    userinfo_detail_data = wxwork_api.get_detail_userinfo(userid)
    department_id = userinfo_detail_data.get("main_department")
    if department_id is None:
        raise Exception("获取用户基本信息department_id出错")
    # 1.2 获取用户姓名
    username = userinfo_detail_data.get("name")
    if department_id is None:
        raise Exception("获取用户基本信息username出错")
    # 2. 获取部门名称
    department_name = wxwork_api.get_detail_department(department_id).get("department").get("name")
    if department_name is None:
        raise Exception("获取用户基本信息department_name出错")

    ret_data = {
        "employee_id": userid,
        "employee_department": department_name,
        "employee_name": username,
    }

    return ret_data


def wxwork_generator_access_token(employee_data):
    # 创建绑定用户关系
    # 能获取到data就表示成功了，此时可以颁发一个token一同返回。
    # 前端后面都需要拿着token来发送请求，然后校验token，返回user对象。
    # token校验成功的user对象中取出userid,（只信任从token中取出的user_id）
    employee_id = employee_data.pop("employee_id")

    employee = db.session.scalar(sa.select(Employee).where(Employee.employee_id == employee_id))
    # 不存在直接创建
    if employee is None:
        employee = Employee(employee_id=employee_id, **employee_data)
        db.session.add(employee)
        db.session.commit()

    # 生成token， payload中携带user_id
    userinfo = {"userid": employee_id}
    return generate_token(playload=userinfo, expire=timedelta(hours=2))
