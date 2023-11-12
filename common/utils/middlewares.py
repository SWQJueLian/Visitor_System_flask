"""实现中间件，类似django的中间件"""

from flask import g, request
from utils.jwt_tools import verify_token


def get_userid():
    # 获取请求头中的token

    g.is_login = False
    g.userid = None
    g.is_refresh_token = None

    if request.authorization is not None:
        token = request.authorization.token

        # 调用token校验函数
        playload, is_refresh_token = verify_token(token)

        if playload:
            # 没有就没有吧，不要返回，后面有需要的函数再用装饰器去强制要求授权后才能使用视图
            # return {
            #     "code": "400888",
            #     "message": "用户未登录!"
            # }
            g.userid = playload.get("userid", None)
            g.is_refresh_token = is_refresh_token
            # 有userid 且 refresh_token不为True，则表示已经登录
            if bool(g.userid and (not g.is_refresh_token)):
                g.is_login = True
