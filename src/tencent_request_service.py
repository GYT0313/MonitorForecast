# -*- coding: UTF-8 -*-
import json
from datetime import datetime

import requests

from db_request_service import get_most_new_data_by_last_update_time

"""
请求腾讯API获得疫情数据并保存到MySQL
"""
global_data_url = 'https://api.inews.qq.com/newsqa/v1/automation/modules/list?modules=FAutoCountryConfirmAdd,WomWorld,WomAboard'
global_daily_url = 'https://api.inews.qq.com/newsqa/v1/automation/modules/list?modules=FAutoGlobalStatis,FAutoContinentStatis,FAutoGlobalDailyList,FAutoCountryConfirmAdd'
china_url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'


def request_global_data_url():
    """
    全球疫情数据
    :return:
    """
    return request(global_data_url).text


def request_global_daily_url():
    """
    全球每日疫情数据变化
    :return:
    """
    return request(global_daily_url).text


def request_china_url():
    """
    国内疫情数据
    :return:
    """
    return request(china_url).text


def china_epidemic_situation():
    pass


def china_forecast():
    pass


def cumulative_distribution_by_continent():
    """
    各洲累计分布确诊
    :return:
    """
    pass


# ##############################################全球数据#################################################################

def save_global_data(db, GlobalWomWorld, GlobalWomAboard, GlobalDaily):
    """
    保存全球疫情相关数据到MySQL
    :return:
    """
    save_global_world_and_aboard(db=db, GlobalWomWorld=GlobalWomWorld, GlobalWomAboard=GlobalWomAboard)
    save_global_daily(db=db, GlobalDaily=GlobalDaily)


def save_global_world_and_aboard(db, GlobalWomWorld, GlobalWomAboard):
    """
    保存全球疫情相关数据到MySQL
    :return:
    """
    data = json.loads(request_global_data_url())
    save_global_wom_world(db, GlobalWomWorld, data)
    save_global_wom_aboard(db, GlobalWomAboard, data, get_most_new_data_by_last_update_time(GlobalWomWorld).id)


def save_global_daily(db, GlobalDaily):
    """

    :return:
    """
    global_daily_list = json.loads(request_global_daily_url()).get('data').get('FAutoGlobalDailyList')
    for global_daily in global_daily_list:
        all_data = global_daily.get("all")
        date_time = format_str_date(global_daily.get("y") + " " + global_daily.get("date"))

        db.session.add(GlobalDaily(
            confirm=all_data.get("confirm"),
            dead=all_data.get("dead"),
            heal=all_data.get("heal"),
            new_add_confirm=all_data.get("newAddConfirm"),
            dead_rate=all_data.get("deadRate"),
            heal_rate=all_data.get("healRate"),
            date_time=date_time))

    db.session.commit()
    db.session.close()


def save_global_wom_world(db, GlobalWomWorld, data):
    """
    全球疫情数据汇总保存到MySQL
    :return: 当前请求数据的更新时间
    """
    wom_world = data.get('data').get('WomWorld')
    db.session.add(GlobalWomWorld(
        now_confirm=wom_world.get("nowConfirm"),
        now_confirm_add=wom_world.get("nowConfirmAdd"),
        confirm=wom_world.get("confirm"),
        confirm_add=wom_world.get("confirmAdd"),
        heal=wom_world.get("heal"),
        heal_add=wom_world.get("healAdd"),
        dead=wom_world.get("dead"),
        dead_add=wom_world.get("deadAdd"),
        death_rate=wom_world.get("deathrate"),
        cure_rate=wom_world.get("curerate"),
        last_update_time=wom_world.get("lastUpdateTime")))
    db.session.commit()
    db.session.close()


def save_global_wom_aboard(db, GlobalWomAboard, data, global_wom_world_id):
    """
    各国疫情保存到MySQL
    :return:
    """
    wom_aboard_list = data.get('data').get('WomAboard')
    for wom_aboard in wom_aboard_list:
        db.session.add(GlobalWomAboard(
            continent=wom_aboard.get("continent"),
            name=wom_aboard.get("name"),
            confirm=wom_aboard.get("confirm"),
            confirm_add=wom_aboard.get("confirmAdd"),
            dead=wom_aboard.get("dead"),
            dead_compare=wom_aboard.get("deadCompare"),
            heal=wom_aboard.get("heal"),
            heal_compare=wom_aboard.get("healCompare"),
            now_confirm=wom_aboard.get("nowConfirm"),
            now_confirm_compare=wom_aboard.get("nowConfirmCompare"),
            global_wom_world_id=global_wom_world_id

        ))
    db.session.commit()
    db.session.close()


# ##############################################国内数据#################################################################

def save_china(db, ChinaTotal, ChinaCompareDaily, ChinaProvince, ChinaCity):
    """
    国内疫情数据保存到MySQL
    :return:
    """
    response = json.loads(request_china_url())

    # 响应成功
    if response.get('ret') == 0:
        data = json.loads(response.get('data'))
        last_update_time = data.get("lastUpdateTime")

        # 国内数据汇总和每日较上日数据变化
        save_china_total(db=db, ChinaTotal=ChinaTotal, data=data.get('chinaTotal'),
                         last_update_time=last_update_time)
        most_new_model_data_id = get_most_new_data_by_last_update_time(ChinaTotal).id

        save_china_daily(db=db, ChinaCompareDaily=ChinaCompareDaily, data=data.get('chinaAdd'),
                         date_time=get_date_by_last_update_time(last_update_time),
                         china_total_id=most_new_model_data_id)
        # 省和城市数据
        province_and_city_list = data.get('areaTree')[0].get('children')
        save_china_province_or_city(db=db, ChinaProvince=ChinaProvince, ChinaCity=ChinaCity,
                                    province_and_city_list=province_and_city_list,
                                    china_total_id=most_new_model_data_id)
    else:
        print("ERROR - 国内请求API没有数据")


def save_china_total(db, ChinaTotal, data, last_update_time):
    """
    保存国内数据汇总
    :return:
    """
    db.session.add(ChinaTotal(
        confirm=data.get("confirm"),
        heal=data.get("heal"),
        dead=data.get("dead"),
        now_confirm=data.get("nowConfirm"),
        suspect=data.get("suspect"),
        now_severe=data.get("nowSevere"),
        last_update_time=last_update_time
    ))

    db.session.commit()
    db.session.close()


def save_china_daily(db, ChinaCompareDaily, data, date_time, china_total_id):
    """
    保存国内每日数据变化到MySQL
    :return:
    """
    db.session.add(ChinaCompareDaily(
        confirm_compare=data.get("confirm"),
        heal_compare=data.get("heal"),
        dead_compare=data.get("dead"),
        now_confirm_compare=data.get("nowConfirm"),
        suspect_compare=data.get("suspect"),
        now_severe_compare=data.get("nowSevere"),
        date_time=date_time,
        china_total_id=china_total_id
    ))

    db.session.commit()
    db.session.close()


def save_china_province_or_city(db, ChinaProvince, ChinaCity, province_and_city_list, china_total_id):
    """
    保存省和城市数据到MySQL
    :return:
    """

    def save(name, ChinaProvinceOrCityClass, today, total):
        """
        省和城市数据结构相同, 可以使用一个方法保存
        :param name: 名称-省或城市
        :param ChinaProvinceOrCityClass: 省或城市模型类
        :param today: 今日数据较昨日变化
        :param total: 总的数据汇总
        :return:
        """
        db.session.add(ChinaProvinceOrCityClass(
            name=name,
            confirm=total.get("confirm"),
            heal=total.get("heal"),
            dead=total.get("dead"),
            now_confirm=total.get("nowConfirm"),
            confirm_compare=today.get("confirm"),
            china_total_id=china_total_id
        ))

        db.session.commit()
        db.session.close()

    for province_and_city_data in province_and_city_list:
        # 省
        save(name=province_and_city_data.get('name'), ChinaProvinceOrCityClass=ChinaProvince,
             today=province_and_city_data.get('today'), total=province_and_city_data.get('total'))
        # 城市
        city_data_list = province_and_city_data.get('children')
        for city_data in city_data_list:
            save(name=city_data.get('name'), ChinaProvinceOrCityClass=ChinaCity, today=city_data.get('today'),
                 total=city_data.get('total'))


def request(url):
    """
    请求第三方API
    :param url: API
    :return: 三方API响应
    """
    return requests.get(url=url)


def format_str_date(str_date):
    """
    将全球每日疫情数据中的字符串转为时间
    :return:
    """
    return datetime.strptime(str_date, '%Y %m.%d').date().__str__()


def get_date_by_last_update_time(last_update_time):
    """
    将last_update_time格式的时间返回年月日
    :param last_update_time:
    :return:
    """
    return datetime.strptime(last_update_time, '%Y-%m-%d %H:%M:%S').date().__str__()
