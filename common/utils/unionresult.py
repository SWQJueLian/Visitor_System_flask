from dataclasses import dataclass
from enum import Enum
from typing import Union, Any


@dataclass
class JsonApiResult:
    code: int
    message: Union[str, dict]
    data: Any = None


class GlobalStatusCode(Enum):
    """全局错误状态码枚举类"""

    OK = (0, "成功")
    ERROR = (-1, '错误')
    SERVER_ERR = (500, '服务器异常')

    # 业务异常默认
    BUSINESS_ERR = (40000, '业务异常')

    IMAGE_CODE_ERR = (40001, '图形验证码错误')
    THROTTLING_ERR = (40002, '访问过于频繁')
    NECESSARY_PARAM_ERR = (40003, '缺少必传参数')
    USER_ERR = (40004, '用户名错误')
    PWD_ERR = (40005, '密码错误')
    CPWD_ERR = (40006, '密码不一致')
    MOBILE_ERR = (40007, '手机号错误')
    SMS_CODE_ERR = (40008, '短信验证码有误')
    ALLOW_ERR = (40009, '未勾选协议')
    LOGIN_REQUIRED_ERR = (40010, '用户未登录')
    REGISTER_FAILED_ERR = (40011, '注册失败')
    SMS_CODE_HAS_SEND = (40012, '短信验证码已经发宋，请稍后再试')

    DB_ERR = (50000, '数据库错误')
    EMAIL_ERR = (50001, '邮箱错误')
    TEL_ERR = (50002, '固定电话错误')
    NODATA_ERR = (50003, '无数据')
    NEW_PWD_ERR = (50004, '新密码错误')
    OPENID_ERR = (50005, '无效的openid')
    PARAM_ERR = (50006, '参数错误')
    STOCK_ERR = (50007, '库存不足')

    @property
    def code(self):
        """返回错误码"""
        return self.value[0]

    @property
    def msg(self):
        """返回错误信息"""
        return self.value[1]


def unpack(enum: GlobalStatusCode):
    """
    传递GlobalStatusCode，组成 code, msg 元组后返回
    :param enum:
    :return:
    """
    return enum.code, enum.msg
