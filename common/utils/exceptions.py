from dataclasses import asdict

from sqlalchemy.exc import OperationalError
from werkzeug.exceptions import HTTPException

from utils.unionresult import JsonApiResult, GlobalStatusCode, unpack


class DBException(HTTPException):
    """数据库异常类"""
    code = 507
    msg = "后端数据库执行异常"


def database_error(e: DBException):
    return {
        "code": e.code,
        "message": e.msg
    }


def operational_error(e: OperationalError):
    print(e.args)
    return asdict(JsonApiResult(*unpack(GlobalStatusCode.DB_ERR)))
