"""jwt token工具类"""
import datetime

import jwt
from flask import current_app


def generate_token(playload, expire: datetime.timedelta):
    """
    :param playload:
    :param expire:
    :return:
    """
    if not isinstance(expire, datetime.timedelta):
        raise jwt.PyJWTError("生成token过期时间必须是timedelta类型")

    _playload = {"exp": datetime.datetime.utcnow() + expire}
    # 更新字典
    _playload.update(playload)

    key = current_app.config["JWT_SECRET_KEY"]

    token = jwt.encode(_playload, key)

    userid = _playload.get("userid")
    if not userid:
        raise ValueError("无法从playload中获取userid，请确定playload中存在userid")

    # 保存用户的token到redis中，可用用于后台可以方便的禁用token
    # redis_cluster.sadd(f"user:{userid}:tokens", token)
    # redis_cluster.expire(f"user:{userid}:tokens", expire)

    return token


def generate_refresh_token(playload, expire: datetime.timedelta):
    """生成带有标志位is_refresh_token的JWT TOKEN"""

    refresh_playload = {"is_refresh_token": True}
    refresh_playload.update(playload)

    return generate_token(refresh_playload, expire)


def verify_token(token):
    """
    校验token并返回playload
    :param token:
    :return: playload, is_refresh_token; 如果出现异常回playload返回空，所以记得要判断一下是否为空
    """
    is_refresh_token = None
    try:
        playload = jwt.decode(
            token, key=current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
        )
        if playload:
            is_refresh_token = playload.get("is_refresh_token")
    except jwt.PyJWTError as e:
        playload = {}
    return playload, is_refresh_token
