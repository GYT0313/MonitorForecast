# -*- coding: UTF-8 -*-
import json

import pandas as pd

"""
从MySQL获取数据并处理服务
"""
contents_name_list = ['亚洲', '非洲', '欧洲', '北美洲', '南美洲', '大洋洲', '其他']


def get_most_new_data_by_last_update_time(ModelClassType):
    """
    根据last_update_time返回最新的数据: 仅限有last_update_time的模型类
    :return:
    """
    return ModelClassType.query.order_by('last_update_time').limit(1).all()[0]


def get_global_aboard(GlobalWomWorld, GlobalWomAboard):
    """
    获取各国数据
    :return:
    """
    # 获取最新的数据
    most_new_global_wom_world_data = get_most_new_data_by_last_update_time(GlobalWomWorld)
    # 获取最新的各国数据, 将属性提取出来
    return list(map(lambda x: x.__self_dict__(),
                    GlobalWomAboard.query.filter(
                        GlobalWomAboard.global_wom_world_id == most_new_global_wom_world_data.id).all()))


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
    return pd.DataFrame(get_global_aboard(GlobalWomWorld, GlobalWomAboard)).to_json(orient='records')


def get_global_daily(GlobalDaily):
    """
    全球每日疫情数据
    :param GlobalDaily:
    :return:
    """
    return json.dumps(list(map(lambda x: x.__self_dict__(), GlobalDaily.query.all())), ensure_ascii=False).__str__()


def get_global_head_fifteen(GlobalWomWorld, GlobalWomAboard):
    """
    各国确诊数前15
    :return:
    """
    # 降序排序后前15条数据
    return pd.DataFrame(get_global_aboard(GlobalWomWorld, GlobalWomAboard)).sort_values(
        by="confirm", ascending=False)[:15].to_json(orient='records')


def get_china_total_and_daily(ChinaTotal, ChinaCompareDaily):
    """
    国内疫情数据
    :return:
    """
    # 获取最新的数据
    most_new_china_total_data = get_most_new_data_by_last_update_time(ChinaTotal)
    most_new_china_compare_data = get_most_new_china_compare_daily(ChinaCompareDaily, most_new_china_total_data.id)
    return json.dumps({
        'continent': '亚洲',
        'name': '中国',
        'confirm': most_new_china_total_data.confirm,
        'confirm_add': most_new_china_compare_data["confirm_compare"],
        'dead': most_new_china_total_data.dead,
        'dead_compare': most_new_china_compare_data["dead_compare"],
        'heal': most_new_china_total_data.heal,
        'heal_compare': most_new_china_compare_data["heal_compare"],
        'now_confirm': most_new_china_total_data.now_confirm,
        'now_confirm_compare': most_new_china_compare_data["now_confirm_compare"],
        'suspect': most_new_china_total_data.suspect,
        'suspect_compare': most_new_china_compare_data["suspect_compare"],
        'now_severe': most_new_china_total_data.now_severe,
        'now_severe_compare': most_new_china_compare_data["now_severe_compare"]
    }, ensure_ascii=False)


def get_most_new_china_compare_daily(ChinaCompareDaily, china_total_id):
    """
    根据最新国内汇总数据的id获取最新的较上日数据
    :return:
    """
    # 获取最新的各国数据, 将属性提取出来
    return list(map(lambda x: x.__self_dict__(),
                    ChinaCompareDaily.query.filter(ChinaCompareDaily.china_total_id == china_total_id).all()))[0]
