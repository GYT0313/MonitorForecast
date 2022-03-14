# -*- coding: UTF-8 -*-
import json

import pandas as pd
from sqlalchemy import and_, desc

"""
从MySQL获取数据并处理服务
"""
contents_name_list = ['亚洲', '非洲', '欧洲', '北美洲', '南美洲', '大洋洲', '其他']


def get_most_new_data_by_last_update_time(ModelClassType):
    """
    根据last_update_time返回最新的数据: 仅限有last_update_time的模型类
    :return:
    """
    return ModelClassType.query.order_by(desc(ModelClassType.last_update_time)).limit(1).all()[0]


def get_province_data_by_name_and_china_total_id(ChinaProvince, province_name, china_total_id):
    """
    根据省名称和国内总数据id查询省的数据
    :return:
    """
    return ChinaProvince.query.filter(
        and_(ChinaProvince.name == province_name, ChinaProvince.china_total_id == china_total_id)).all()[0]


# def get_data_by_global_wom_world_id(ModelTypeClass, global_wom_world_id):
#     """
#     根据global_wom_world_id查询此数据是否已经保存
#     :param ModelTypeClass:
#     :param global_wom_world_id:
#     :return:
#     """
#     data_in_mysql_list = ModelTypeClass.query.filter(
#         ModelTypeClass.global_wom_world_id == global_wom_world_id).all()
#     if len(data_in_mysql_list) > 0:
#         return data_in_mysql_list[0]
#     else:
#         return None


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


def get_china_total(ChinaTotal, ChinaCompareDaily):
    """
    国内疫情数据
    :return:
    """
    # 获取最新的数据 汇总数据+较昨日数据变化
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
    根据最新国内汇总数据的id, 获取较昨日变化数据
    :return:
    """
    # 获取最新的各国数据, 将属性提取出来
    return list(map(lambda x: x.__self_dict__(),
                    ChinaCompareDaily.query.filter(ChinaCompareDaily.china_total_id == china_total_id).all()))[0]


def get_china_province(ChinaTotal, ChinaProvince):
    """
    获取最新国内各省数据
    :return:
    """
    return json.dumps(list(map(lambda x: x.__self_dict__(),
                               ChinaProvince.query.filter(
                                   ChinaProvince.china_total_id == get_most_new_data_by_last_update_time(
                                       ChinaTotal).id).all())), ensure_ascii=False)


def get_china_all_city(ChinaTotal, ChinaProvince, ChinaCity):
    """
    获取国内各城市数据
    :return:
    """
    # 最新各省数据的id
    province_id_list = list(map(lambda x: x['id'], json.loads(get_china_province(ChinaTotal, ChinaProvince))))

    return json.dumps(list(map(lambda x: x.__self_dict__(),
                               ChinaCity.query.filter(
                                   ChinaCity.china_province_id.in_(province_id_list)).all())), ensure_ascii=False)


def get_china_city_by_province_id(ChinaCity, china_province_id):
    """
    根据省份id获取最新的城市数据
    :return:
    """
    return json.dumps(list(map(lambda x: x.__self_dict__(),
                               ChinaCity.query.filter(
                                   and_(ChinaCity.china_province_id == china_province_id)).all())), ensure_ascii=False)


def get_china_compare_daily(ChinaCompareDaily):
    """
    获取国内较昨日疫情变化趋势数据
    :param ChinaCompareDaily:
    :return:
    """
    # 将datetime 转为 str
    result = []
    for item in list(map(lambda x: x.__self_dict__(), ChinaCompareDaily.query.all())):
        item['date_time'] = str(item['date_time'].date())
        result.append(item)
    return json.dumps(result, ensure_ascii=False)


def china_province_head_fifteen(ChinaTotal, ChinaProvince):
    """
    各省累计确诊前15数据
    :param ChinaTotal:
    :param ChinaProvince:
    :return:
    """
    most_new_china_total = get_most_new_data_by_last_update_time(ChinaTotal)
    return pd.DataFrame(list(map(lambda x: x.__self_dict__(), ChinaProvince.query.filter(
        ChinaProvince.china_total_id == most_new_china_total.id).all()))).sort_values(by="confirm", ascending=False)[
           :15].to_json(orient='records')
