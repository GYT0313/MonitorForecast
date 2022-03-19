# -*- coding: UTF-8 -*-
import json
from datetime import datetime

import requests
from sqlalchemy import and_

from db_request_service import get_most_new_data_by_last_update_time, get_province_data_by_name_and_china_total_id

"""
请求腾讯API获得疫情数据并保存到MySQL
"""
global_data_url = 'https://api.inews.qq.com/newsqa/v1/automation/modules/list?modules=FAutoCountryConfirmAdd,' \
                  'WomWorld,WomAboard'
global_daily_url = 'https://api.inews.qq.com/newsqa/v1/automation/modules/list?modules=FAutoGlobalStatis,' \
                   'FAutoContinentStatis,FAutoGlobalDailyList,FAutoCountryConfirmAdd'
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
    is_add_or_update = save_global_world_and_aboard(db=db, GlobalWomWorld=GlobalWomWorld,
                                                    GlobalWomAboard=GlobalWomAboard)
    if is_add_or_update:
        save_global_daily(db=db, GlobalDaily=GlobalDaily)
        print('全球数据-已更新.')
        return True
    else:
        print('全球数据-未更新.')
        return False


def save_global_world_and_aboard(db, GlobalWomWorld, GlobalWomAboard):
    """
    保存全球疫情相关数据到MySQL
    :return:
    """
    data = json.loads(request_global_data_url())
    is_add_or_update = save_global_wom_world(db, GlobalWomWorld, data)
    # 如果全球数据新增或更新了, 才进行各国、daily数据添加
    if is_add_or_update:
        save_global_wom_aboard(db, GlobalWomAboard, data, get_most_new_data_by_last_update_time(GlobalWomWorld).id)
    return is_add_or_update


def save_global_daily(db, GlobalDaily):
    """

    :return:
    """
    try:
        global_daily_list = json.loads(request_global_daily_url()).get('data').get('FAutoGlobalDailyList')
        for global_daily in global_daily_list:
            all_data = global_daily.get("all")
            date_time = format_str_date(global_daily.get("y") + " " + global_daily.get("date"))
            global_daily = GlobalDaily(
                confirm=all_data.get("confirm"),
                dead=all_data.get("dead"),
                heal=all_data.get("heal"),
                new_add_confirm=all_data.get("newAddConfirm"),
                dead_rate=all_data.get("deadRate"),
                heal_rate=all_data.get("healRate"),
                date_time=date_time)
            # 全球疫情数据只更新到了2021年9月1日，所以如果已有数据直接break
            has_data_list = GlobalDaily.query.filter(GlobalDaily.date_time == date_time).all()
            if len(has_data_list) != 0:
                break
            else:
                db.session.add(global_daily)
        db.session.commit()
    except BaseException:
        # 全球疫情数据只更新到了2021年9月1日，所以重复时不回滚，也不抛出异常
        # db.session.rollback()
        # raise Exception('数据新增异常!')
        pass


def save_global_wom_world(db, GlobalWomWorld, data):
    """
    全球疫情数据汇总保存到MySQL
    :return: 是否是添加或更新了数据: 是-True, 否-False
    """
    try:
        wom_world = data.get('data').get('WomWorld')
        global_wom_world = GlobalWomWorld(
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
            last_update_time=wom_world.get("lastUpdateTime"),
            date_time=get_date_by_last_update_time(wom_world.get("lastUpdateTime")))
        # 为实现每天数据只有一条记录: 如果存在年-月-日相等, 并且时-分-秒不相等的数据，存在则更新, 否则添加
        # 根据年-月-日查询是否有今日的数据
        is_add_or_update = True
        has_today_data = GlobalWomWorld.query.filter(
            GlobalWomWorld.date_time == get_date_by_last_update_time(wom_world.get("lastUpdateTime"))).all()
        # 如果存在今日数据，判断是否时-分-秒相等，如果不相同则更新
        if len(has_today_data) > 0:
            is_update_num = GlobalWomWorld.query.filter(
                and_(GlobalWomWorld.date_time == get_date_by_last_update_time(wom_world.get("lastUpdateTime")),
                     GlobalWomWorld.last_update_time != wom_world.get("lastUpdateTime"))).update(
                pop_id_and_date_time(global_wom_world.__self_dict__()))
            # 如果返回值>0 表示进行数据的更新, 如果<=0，表示此数据没有变化, 不更新也不新增
            if is_update_num <= 0:
                is_add_or_update = False
        else:
            db.session.add(global_wom_world)

        db.session.commit()
        return is_add_or_update
    except BaseException:
        db.session.rollback()
        raise Exception('全球数据新增异常!')


def save_global_wom_aboard(db, GlobalWomAboard, data, global_wom_world_id):
    """
    各国疫情保存到MySQL
    :return:
    """
    try:
        wom_aboard_list = data.get('data').get('WomAboard')
        for wom_aboard in wom_aboard_list:
            global_wom_aboard = GlobalWomAboard(
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
            )
            # 如果存在则更新
            is_update_num = GlobalWomAboard.query.filter(
                and_(GlobalWomAboard.name == wom_aboard.get("name"),
                     GlobalWomAboard.global_wom_world_id == global_wom_world_id)).update(
                pop_id(global_wom_aboard.__self_dict__()))
            # 否则新增
            if is_update_num <= 0:
                db.session.add(global_wom_aboard)

        db.session.commit()
    except BaseException:
        db.session.rollback()
        raise Exception('全球数据新增异常!')


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
        is_add_or_update = save_china_total(db=db, ChinaTotal=ChinaTotal, data=data.get('chinaTotal'),
                                            last_update_time=last_update_time)
        # 如果国内汇总数据更新时间未变化, 不进行其他数据添加
        if is_add_or_update:
            most_new_model_data_id = get_most_new_data_by_last_update_time(ChinaTotal).id

            save_china_daily(db=db, ChinaCompareDaily=ChinaCompareDaily, data=data.get('chinaAdd'),
                             date_time=get_date_by_last_update_time(last_update_time),
                             china_total_id=most_new_model_data_id)
            # 省和城市数据
            province_and_city_list = data.get('areaTree')[0].get('children')
            save_china_province_or_city(db=db, ChinaProvince=ChinaProvince, ChinaCity=ChinaCity,
                                        province_and_city_list=province_and_city_list,
                                        china_total_id=most_new_model_data_id)
            print('国内数据-已更新.')
            return True
        else:
            print('国内数据-未更新.')
            return False
    else:
        print("国内请求API没有数据")


def save_china_total(db, ChinaTotal, data, last_update_time):
    """
    保存国内数据汇总
    :return:
    """
    try:
        china_total = ChinaTotal(
            confirm=data.get("confirm"),
            heal=data.get("heal"),
            dead=data.get("dead"),
            now_confirm=data.get("nowConfirm"),
            suspect=data.get("suspect"),
            now_severe=data.get("nowSevere"),
            last_update_time=last_update_time,
            date_time=get_date_by_last_update_time(last_update_time)
        )
        # 为实现每天数据只有一条记录: 如果存在年-月-日相等, 并且时-分-秒不相等的数据，存在则更新, 否则添加
        # 根据年-月-日查询是否有今日的数据
        is_add_or_update = True
        has_today_data = ChinaTotal.query.filter(
            ChinaTotal.date_time == get_date_by_last_update_time(last_update_time)).all()
        # 如果存在今日数据，判断是否时-分-秒相等，如果不相同则更新
        if len(has_today_data) > 0:
            is_update_num = ChinaTotal.query.filter(
                and_(ChinaTotal.date_time == get_date_by_last_update_time(last_update_time),
                     ChinaTotal.last_update_time != last_update_time)).update(
                pop_id_and_date_time(china_total.__self_dict__()))
            # 如果返回值>0 表示进行数据的更新, 如果<=0，表示此数据没有变化, 不更新也不新增
            if is_update_num <= 0:
                is_add_or_update = False
        else:
            db.session.add(china_total)

        db.session.commit()
        return is_add_or_update
    except BaseException:
        db.session.rollback()
        raise Exception('国内汇总数据新增异常!')


def save_china_daily(db, ChinaCompareDaily, data, date_time, china_total_id):
    """
    保存国内每日数据变化到MySQL
    :return:
    """
    try:
        china_compare_daily = ChinaCompareDaily(
            confirm_compare=data.get("confirm"),
            heal_compare=data.get("heal"),
            dead_compare=data.get("dead"),
            now_confirm_compare=data.get("nowConfirm"),
            suspect_compare=data.get("suspect"),
            now_severe_compare=data.get("nowSevere"),
            date_time=date_time,
            china_total_id=china_total_id
        )
        # 如果存在则更新, 否则添加
        is_update_num = ChinaCompareDaily.query.filter(
            and_(ChinaCompareDaily.date_time == date_time)).update(pop_id(china_compare_daily.__self_dict__()))
        if is_update_num <= 0:
            db.session.add(china_compare_daily)
        db.session.commit()
    except BaseException:
        db.session.rollback()
        raise Exception('国内每日数据变化新增异常!')


def save_china_province_or_city(db, ChinaProvince, ChinaCity, province_and_city_list, china_total_id):
    """
    保存省和城市数据到MySQL
    :return:
    """
    try:
        def save_province(name, today, total):
            """
            省数据保存
            :param name: 名称-省或城市
            :param today: 今日数据较昨日变化
            :param total: 总的数据汇总
            :return:
            """
            china_province = ChinaProvince(
                name=name,
                confirm=total.get("confirm"),
                heal=total.get("heal"),
                dead=total.get("dead"),
                now_confirm=total.get("nowConfirm"),
                confirm_compare=today.get("confirm"),
                china_total_id=china_total_id
            )
            # 如果存在则更新
            is_update_num = ChinaProvince.query.filter(
                and_(ChinaProvince.name == name, ChinaProvince.china_total_id == china_total_id)).update(
                pop_id(china_province.__self_dict__()))
            # 否则新增
            if is_update_num <= 0:
                db.session.add(china_province)
            db.session.commit()

        def save_city(name, today, total, china_province_id):
            """
            省数据保存
            :param name: 名称-省或城市
            :param today: 今日数据较昨日变化
            :param total: 总的数据汇总
            :param china_province_id: 省数据的id
            :return:
            """
            china_city = ChinaCity(
                name=name,
                confirm=total.get("confirm"),
                heal=total.get("heal"),
                dead=total.get("dead"),
                now_confirm=total.get("nowConfirm"),
                confirm_compare=today.get("confirm"),
                china_province_id=china_province_id
            )
            # 如果存在则更新
            is_update_num = ChinaCity.query.filter(
                and_(ChinaCity.name == name, ChinaCity.china_province_id == china_province_id)).update(
                pop_id(china_city.__self_dict__()))
            # 否则新增
            if is_update_num <= 0:
                db.session.add(china_city)

        for province_and_city_data in province_and_city_list:
            # 省
            save_province(name=province_and_city_data.get('name'), today=province_and_city_data.get('today'),
                          total=province_and_city_data.get('total'))
            # 城市
            city_data_list = province_and_city_data.get('children')
            for city_data in city_data_list:
                save_city(name=city_data.get('name'), today=city_data.get('today'),
                          total=city_data.get('total'),
                          china_province_id=get_province_data_by_name_and_china_total_id(
                              ChinaProvince,
                              province_and_city_data.get('name'),
                              china_total_id).id)

        db.session.commit()
    except BaseException:
        db.session.rollback()
        raise Exception('国内省、城市数据新增异常!')


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


def pop_id_and_date_time(data_dict):
    """
    把id、date_time字段去除
    :param dat_dict:
    :return:
    """
    data_dict.pop('id')
    data_dict.pop('date_time')
    return data_dict


def pop_id(data_dict):
    """
    把id字段去除
    :return:
    """
    data_dict.pop('id')
    return data_dict
