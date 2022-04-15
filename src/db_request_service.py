# -*- coding: UTF-8 -*-
import json

import pandas as pd
from sqlalchemy import and_, desc

from common_config import *
from common_util import *
from forecast_codv19 import *

"""
从MySQL获取数据并处理服务
"""


def get_most_new_data_by_last_update_time(ModelClassType):
    """
    根据last_update_time返回最新的数据: 仅限有last_update_time的模型类
    :return:
    """
    return ModelClassType.query.order_by(desc(ModelClassType.last_update_time)).limit(1).all()[0]


def get_most_new_data_by_last_update_time_and_name(ModelClassType, name):
    """
    根据last_update_time 和name返回最新的数据: 仅限有last_update_time 和name的模型类
    :return:
    """
    return \
        ModelClassType.query.filter(ModelClassType.name == name).order_by(desc(ModelClassType.last_update_time)).limit(
            1).all()[0]


def get_province_data_by_name_and_china_total_id(ChinaProvince, province_name, china_total_id):
    """
    根据省名称和国内总数据id查询省的数据
    :return:
    """
    return ChinaProvince.query.filter(
        and_(ChinaProvince.name == province_name, ChinaProvince.china_total_id == china_total_id)).all()[0]


def get_global_data(GlobalWomWorld, ChinaTotal):
    """
    获取全球数据: 全球+中国
    :param GlobalWomWorld:
    :param ChinaTotal:
    :return:
    """
    new_most_global_world = get_most_new_data_by_last_update_time(GlobalWomWorld)
    new_most_china_total = get_most_new_data_by_last_update_time(ChinaTotal)
    return json.dumps({
        "confirm": new_most_global_world.confirm + new_most_china_total.confirm,
        "heal": new_most_global_world.heal + new_most_china_total.heal,
        "dead": new_most_global_world.dead + new_most_china_total.dead
    }, ensure_ascii=False)


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
    return json.dumps(inner_get_china_province(ChinaTotal, ChinaProvince), ensure_ascii=False)


def inner_get_china_province(ChinaTotal, ChinaProvince):
    """
    获取最新国内各省数据
    :return:
    """
    return list(map(lambda x: x.__self_dict__(),
                    ChinaProvince.query.filter(
                        ChinaProvince.china_total_id == get_most_new_data_by_last_update_time(
                            ChinaTotal).id).all()))


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


def get_china_compare_daily(ChinaCompareDaily):
    """
    获取国内较昨日疫情变化趋势数据
    :param ChinaCompareDaily:
    :return:
    """
    return json.dumps(list(map(lambda x: x.__self_dict__(), ChinaCompareDaily.query.all())), ensure_ascii=False)


def get_china_province_head_fifteen(ChinaTotal, ChinaProvince):
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


def get_china_region(ChinaTotal, ChinaProvince):
    """
    国内各地区数据饼图 - 如华南、华北等
    :param ChinaTotal:
    :param ChinaProvince:
    :return:
    """
    df_province = pd.DataFrame(inner_get_china_province(ChinaTotal, ChinaProvince))
    # 新增region列
    df_province['region'] = df_province.apply(lambda row: region_map[row[1]], axis=1)
    # 分组求和
    return df_province.groupby(by=['region'], as_index=False).sum().to_json(orient='records')


def get_china_province_of_city(ChinaTotal, ChinaProvince, ChinaCity, params):
    """
    获取指定省份的所有城市数据
    :return:
    """
    most_new_china_total = get_most_new_data_by_last_update_time(ChinaTotal)
    province_of_city = ChinaProvince.query.filter(
        and_(ChinaProvince.name == params['province'],
             ChinaProvince.china_total_id == most_new_china_total.id)).all()[0]
    return json.dumps(list(map(lambda x: x.__self_dict__(),
                               ChinaCity.query.filter(ChinaCity.china_province_id == province_of_city.id).all())),
                      ensure_ascii=False)


def get_china_province_of_city_json(ChinaTotal, ChinaProvince, ChinaCity):
    """
    获取各省对应城市json
    :param ChinaTotal:
    :param ChinaProvince:
    :param ChinaCity:
    :return:
    """
    result = []
    most_new_china_total = get_most_new_data_by_last_update_time(ChinaTotal)
    province_list = ChinaProvince.query.filter(ChinaProvince.china_total_id == most_new_china_total.id).all()
    for province in province_list:
        # 跳过港澳台
        if province.name in special_province:
            continue
        city_list = ChinaCity.query.filter(ChinaCity.china_province_id == province.id).all()
        cities = []
        for city in city_list:
            # 跳过城市为'境外输入', '地区待确认'
            if city.name in special_cities:
                continue
            cities.append({"name": city.name})
        result.append({
            "name": province.name,
            "cities": cities
        })

    return json.dumps({
        "provinces": result
    }, ensure_ascii=False)


def get_china_province_of_cities_json(ChinaTotal, ChinaProvince, ChinaCity):
    """
    获取各省对应城市json
    :param ChinaTotal:
    :param ChinaProvince:
    :param ChinaCity:
    :return:
    """
    result = []
    most_new_china_total = get_most_new_data_by_last_update_time(ChinaTotal)
    province_list = ChinaProvince.query.filter(ChinaProvince.china_total_id == most_new_china_total.id).all()
    for province in province_list:
        city_list = ChinaCity.query.filter(ChinaCity.china_province_id == province.id).all()
        cities = []
        for city in city_list:
            # 跳过城市为'境外输入', '地区待确认'
            if city.name in special_cities:
                continue
            cities.append({"name": city.name})
        result.append({
            "name": province.name,
            "cities": cities
        })

    return json.dumps({
        "provinces": result
    }, ensure_ascii=False)


def get_province_daily(ChinaProvince, province_name):
    """
    省份每日数据变化趋势
    :param ChinaProvince:
    :param province_name:
    :return:
    """
    # 省的每日数据需要返回日期, 所以使用__self_dict_and_date_time__()
    return json.dumps(
        list(map(lambda x: x.__self_dict_and_date_time__(),
                 ChinaProvince.query.filter(ChinaProvince.name == province_name).all())))


def china_province_city_head_fifteen(ChinaTotal, ChinaProvince, ChinaCity, params):
    """
    根据省份名称查询累计确诊数前五的城市
    :return:
    """
    cities_dict = get_china_province_of_city(ChinaTotal, ChinaProvince, ChinaCity, params)
    return pd.DataFrame(json.loads(cities_dict)).sort_values(by="confirm", ascending=False)[:15].to_json(
        orient='records')


def get_china_province_by_name(ChinaTotal, ChinaProvince, province_name):
    """
    根据省份名称获取最新的数据
    :param ChinaTotal:
    :param ChinaProvince:
    :param province_name:
    :return:
    """
    most_new_china_total = get_most_new_data_by_last_update_time(ChinaTotal)
    return json.dumps(ChinaProvince.query.filter(
        and_(ChinaProvince.name == province_name,
             ChinaProvince.china_total_id == most_new_china_total.id)).first().__self_dict__(), ensure_ascii=False)


def get_china_total_by_date_time(ChinaTotal, date_time):
    """
    根据时间查询国内汇总数据
    :param ChinaTotal:
    :param date_time:
    :return:
    """
    return ChinaTotal.query.filter(ChinaTotal.date_time == get_standard_time_by_date_time(date_time)).first()


def get_china_province_by_time(ChinaTotal, ChinaProvince, province_name, start_time, end_time, forecast_nums):
    """
    预测- 根据开始结束时间查询省的数据
    """
    # 获得要预测的时间, 第二个参数可以设置未来那几天的值, 1 - forecast_time = [end_time+1],  2 - forecast_time = [end_time+1, end_time+2]
    forecast_time = get_feature_time(end_time, int(forecast_nums))

    # 根据时间查询国内汇总数据的id
    start_china_total_id = get_china_total_by_date_time(ChinaTotal, start_time).id
    end_china_total_id = get_china_total_by_date_time(ChinaTotal, end_time).id

    # start ~ end time历史数据
    res = json.dumps(list(map(lambda x: x.__self_dict_and_date_time__(), ChinaProvince.query.filter(
        and_(ChinaProvince.name == province_name,
             ChinaProvince.china_total_id >= start_china_total_id,
             ChinaProvince.china_total_id <= end_china_total_id)).all())),
                     ensure_ascii=False)

    # 准备历史数据横纵值
    df = pd.DataFrame(json.loads(res))
    df['index'] = df.index
    # x从0开始对应历史数据的时间
    xy_df = pd.DataFrame()
    xy_df['x'] = df['index']

    str_forecast = '_forecast'
    # 预测累计确诊
    confirm_name = 'confirm'
    k_confirm_name = confirm_name + str_forecast
    xy_df['y'] = df[confirm_name]
    df_confirm_forecast, confirm_src = get_forecast(xy_df, k_confirm_name, len(forecast_time))

    # 预测累计治愈
    heal_name = 'heal'
    k_heal_name = heal_name + str_forecast
    xy_df['y'] = df[heal_name]
    df_heal_forecast, heal_src = get_forecast(xy_df, k_heal_name, len(forecast_time))

    # 预测累计死亡
    dead_name = 'dead'
    k_dead_name = dead_name + str_forecast
    xy_df['y'] = df[dead_name]
    df_dead_forecast, dead_src = get_forecast(xy_df, k_dead_name, len(forecast_time))

    # 预测现有确诊
    now_confirm_name = 'now_confirm'
    k_now_confirm_name = now_confirm_name + str_forecast
    xy_df['y'] = df[now_confirm_name]
    df_now_confirm_forecast, now_confirm_src = get_forecast(xy_df, k_now_confirm_name, len(forecast_time))

    # 预测较昨日确诊
    confirm_compare_name = 'confirm_compare'
    k_confirm_compare_name = confirm_compare_name + str_forecast
    xy_df['y'] = df[confirm_compare_name]
    df_confirm_compare_forecast, confirm_compare_src = get_forecast(xy_df, k_confirm_compare_name, len(forecast_time))

    # 增加行 - 未来日期
    for f_date_time in forecast_time:
        df = pd.concat([df, pd.DataFrame({"date_time": get_date_by_standard_time(f_date_time)}, index=[0])], axis=0,
                       ignore_index=True)

    df = pd.concat([df, df_confirm_forecast, df_heal_forecast, df_dead_forecast, df_now_confirm_forecast,
                    df_confirm_compare_forecast], axis=1)

    res = {
        "data": json.loads(df.to_json(orient='records')),
        "src_png": [confirm_src, heal_src, dead_src, now_confirm_src, confirm_compare_src]
    }
    return json.dumps(res, ensure_ascii=False)


def get_forecast(xy_df, k_name, feature_nums):
    """
    预测疫情数据
    :return:
    """
    k_a = k_name + "_a"
    k_b = k_name + "_b"
    a, b, x, y_prod, src_dict = forecast(pd.DataFrame(xy_df[['x', 'y']]), feature_nums, k_name)
    print('y = ' + str(a) + ' + ' + str(b) + 'x')

    return pd.DataFrame(list(map(lambda v: {
        k_name: v,
        k_a: a,
        k_b: b
    }, y_prod))), src_dict


def get_forecast_support_time(ChinaTotal):
    """
    查询MySQL中数据最早时间和最新时间
    :param ChinaTotal:
    :return:
    """
    # 降序查询
    china_total_all = ChinaTotal.query.order_by(desc(ChinaTotal.date_time)).all()
    end_time = china_total_all[0].date_time.date().__str__()
    start_time = china_total_all[-1].date_time.date().__str__()
    return json.dumps(
        {
            "start_time": start_time,
            "end_time": end_time
        },
        ensure_ascii=False
    )


def calculate_now_confirm_compare(ChinaCompareDaily):
    """

    :param ChinaCompareDaily:
    :return:
    """
    list_china_compare_daily = list(map(lambda x: x.__self_dict__(), ChinaCompareDaily.query.all()))
    pd_china_compare_daily = pd.DataFrame(list_china_compare_daily)
    pd_china_compare_daily['calculate_now_confirm_compare'] = list(
        (map(lambda x: x['confirm_compare'] - x['heal_compare'] - x['dead_compare'], list_china_compare_daily)))
    return pd_china_compare_daily.to_json(orient='records')
