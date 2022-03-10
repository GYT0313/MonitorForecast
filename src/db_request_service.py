# -*- coding: UTF-8 -*-
import json

import pandas as pd

"""
从MySQL获取数据并处理服务
"""
contents_name_list = ['亚洲', '非洲', '欧洲', '北美洲', '南美洲', '大洋洲', '其他']


def get_global_aboard(GlobalWomWorld, GlobalWomAboard):
    """
    获取各国数据
    :return:
    """
    # 获取最近更新数据的时间
    most_new_last_update_time = GlobalWomWorld.query.order_by('last_update_time').limit(1).all()[0].last_update_time
    # 获取最新的各国数据, 将属性提取出来
    return list(map(lambda x: x.__self_dict__(),
                    GlobalWomAboard.query.filter(GlobalWomAboard.last_update_time == most_new_last_update_time).all()))


def get_global_continent(GlobalWomWorld, GlobalWomAboard):
    """
    全球各大洲疫情数据获取
    :return:
    """
    df = pd.DataFrame(get_global_aboard(GlobalWomWorld, GlobalWomAboard))
    # 将continent为空的记录替换为'其他'
    df['continent'].replace('', contents_name_list[-1], inplace=True)

    # 统计求和各洲数据, 并以json返回
    return df.groupby(['continent'], as_index=False).sum().to_json(orient='records')


def get_global_map(GlobalWomWorld, GlobalWomAboard):
    """
    全球各国数据-map地图
    :return:
    """
    # 只取name和累计确诊人数, map中日本为'日本本土', 需要进行替换, 否则无法显示
    df = pd.DataFrame(get_global_aboard(GlobalWomWorld, GlobalWomAboard))[['name', 'confirm']]
    df['name'].replace('日本', '日本本土', inplace=True)
    return df.to_json(orient='records')


def get_global_daily_list(GlobalDailyList):
    """
    全球每日疫情数据
    :param GlobalDailyList:
    :return:
    """
    return json.dumps(list(map(lambda x: x.__self_dict__(), GlobalDailyList.query.all())), ensure_ascii=False).__str__()


def get_global_head_fifteen(GlobalWomWorld, GlobalWomAboard):
    """
    各国确诊数前15
    :return:
    """
    # 降序排序后前15条数据
    return pd.DataFrame(get_global_aboard(GlobalWomWorld, GlobalWomAboard)).sort_values(
        by="confirm", ascending=False)[:15].to_json(orient='records')
