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

    _playload = {
        "exp": datetime.datetime.utcnow() + expire
    }
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

    refresh_playload = {
        "is_refresh_token": True
    }
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
        playload = jwt.decode(token, key=current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        if playload:
            # 获取token中的userid
            userid = playload.get("userid")
            # 从redis中查询该userid是否有允许的tokens列表
            tokens = redis_cluster.smembers(f"user:{userid}:tokens")
            # 如果token不在redis获取到的列表中，则直接返回空playload
            # 登录装饰器会根据playload来判断是否登录的。
            if not tokens or token not in tokens:
                playload = {}
            else:
                # 如果还要实现封禁用户，一般在登录的时候会校验用户的状态字段
                # 如果用户是在后台被封禁的，那么后台一般执行封禁的动作时就应该把用户的所有token清除掉。
                # 所以这里是没必要再去用userid来查询用户当前是否被禁用了！
                # 如果你非要再查一下可以这样做...
                # 从缓存类中拿到用户的状态，然后判断用户状态字段，不过这完全没必要的.,...
                # UserCache(userid).get()
                is_refresh_token = playload.get("is_refresh_token")
    except jwt.PyJWTError as e:
        playload = {}
    return playload, is_refresh_token
