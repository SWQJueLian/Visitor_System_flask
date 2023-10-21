import imghdr
import re


def is_image(value):
    try:
        pic_type = imghdr.what(value)
        if not pic_type == "png" or pic_type == "jpeg":
            raise ValueError("图片格式必须是png或者jpg、jpeg")
        return value
    except Exception as e:
        # 日志记录

        # 重新抛出
        raise e


def not_allow_empty_text(value):
    """
    校验是否为空文本，空文本直接抛出异常
    :param value:
    :return: 返回一个去掉首部空格的字符串
    """
    value = str(value)
    match = re.match(r'^\s*$', value)
    if match is not None:
        raise ValueError("不允许添加空文本")
    return value.lstrip()
