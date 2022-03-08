# -*- coding: UTF-8 -*-
import json

import requests

from app import get_db, GlobalWomAWorld

"""
    请求处理
"""
global_url = 'https://api.inews.qq.com/newsqa/v1/automation/modules/list?modules=FAutoCountryConfirmAdd,WomWorld,WomAboard'


def global_epidemic_situation():
    return request(global_url).text


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


def save_wom_world():
    data = json.loads(global_epidemic_situation())
    wom_world = data.get('data').get('WomWorld')
    global_wom_world = GlobalWomAWorld(
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
        last_update_time=wom_world.get("lastUpdateTime")
    )
    db = get_db()
    db.session.add(global_wom_world)
    db.session.commit()


def request(url):
    """
        请求第三方API
    :param url: API
    :return: 三方API响应
    """
    return requests.get(url=url)
