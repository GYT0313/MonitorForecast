# -*- coding: UTF-8 -*-


from datetime import datetime

"""
通用公共工具方法
"""


def get_date_by_standard_time(standard_time):
    """
    将yyyy-MM-DD HH:mm:ss格式的时间返回年月日
    :param standard_time:
    :return:
    """
    return datetime.strptime(standard_time, '%Y-%m-%d %H:%M:%S').date().__str__()


def get_standard_time_by_date_time(date_time):
    """
    根据年-月-日 返回 年-月-日 00:00:00
    :param date_time:
    :return:
    """
    return datetime.strptime(date_time, '%Y-%m-%d').__str__()
