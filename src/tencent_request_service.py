# -*- coding: UTF-8 -*-
import json
from datetime import datetime

import requests

"""
请求腾讯API获得疫情数据并保存到MySQL
"""
global_data_url = 'https://api.inews.qq.com/newsqa/v1/automation/modules/list?modules=FAutoCountryConfirmAdd,WomWorld,WomAboard'
global_daily_list_url = 'https://api.inews.qq.com/newsqa/v1/automation/modules/list?modules=FAutoGlobalStatis,FAutoContinentStatis,FAutoGlobalDailyList,FAutoCountryConfirmAdd'


def request_global_data_url():
    """
    全球疫情数据
    :return:
    """
    return request(global_data_url).text


def request_global_daily_list_url():
    """
    全球每日疫情数据变化
    :return:
    """
    return request(global_daily_list_url).text


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


def save_global_data(db, GlobalWomWorld, GlobalWomAboard):
    """
    保存全球疫情相关数据到MySQL
    :return:
    """
    data = json.loads(request_global_data_url())
    last_update_time = save_global_wom_world(db, GlobalWomWorld, data)
    save_global_wom_aboard(db, GlobalWomAboard, data, last_update_time)


def save_global_daily_list(db, GlobalDailyList):
    """

    :return:
    """
    global_daily_list = json.loads(request_global_daily_list_url()).get('data').get('FAutoGlobalDailyList')
    for global_daily in global_daily_list:
        all_data = global_daily.get("all")
        date_time = format_str_date(global_daily.get("y") + " " + global_daily.get("date"))

        db.session.add(GlobalDailyList(
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

    return wom_world.get("lastUpdateTime")


def save_global_wom_aboard(db, GlobalWomAboard, data, last_update_time):
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
            last_update_time=last_update_time
        ))
    db.session.commit()
    db.session.close()


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
