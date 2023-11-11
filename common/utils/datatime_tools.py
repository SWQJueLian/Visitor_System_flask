from datetime import datetime
from typing import Union


def to_13bit_timestamp(p_datetime):
    """
    将给定的datatime类型返回13位时间戳
    :param p_datetime: datatime类型的实例
    :return: 字符串类型的13位时间戳
    """
    if not isinstance(p_datetime, datetime):
        raise ValueError("p_datetime not datetime")
    return "%.f" % (p_datetime.timestamp() * 1000)


def to_10bit_timestamp(timestamp: Union[str, float]):
    """
    将13位时间戳转换位10位
    :param timestamp: 时间戳，字符串或者浮点型
    :return: 字符串格类型的10位时间戳
    """
    return "%.f" % (float(timestamp) / 1000)


def timestamp_13bit_to_datatime(timestamp: Union[str, float]):
    """
    将时间戳转换为datetime类型
    :param timestamp:
    :return:
    """
    # python中是10位时间戳，要先转换位10后才能转换成datetime对象
    f = str(timestamp)
    size = len(f)
    if size > 10 and size == 13:
        f = to_10bit_timestamp(f)
    return datetime.fromtimestamp(float(f))
