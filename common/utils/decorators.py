import functools
from dataclasses import asdict

from flask import g

from utils.unionresult import GlobalStatusCode, JsonApiResult


def login_required_mixin(func):
    """强制登录装饰器"""

    @functools.wraps(func)
    def inner(*args, **kwargs):
        # 从g对象中取得userid
        # userid = g.get("userid")
        # is_refresh_token = g.get("is_refresh_token")
        is_login = g.get("is_login")

        # 先判断是否未refresh_token，如果是就等同于未登录。
        # 再判断有没有userid
        # if is_refresh_token or userid is None:
        if not is_login:
            return asdict(
                JsonApiResult(GlobalStatusCode.LOGIN_REQUIRED_ERR.code, GlobalStatusCode.LOGIN_REQUIRED_ERR.msg))

        # 调用原来的视图函数
        ret = func(*args, **kwargs)
        return ret

    return inner
