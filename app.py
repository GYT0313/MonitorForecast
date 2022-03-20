# -*- coding: UTF-8 -*-
from datetime import timedelta

import pymysql
from flask import Flask, request
from flask import redirect, url_for
from flask import render_template
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy

from common_util import *
from src import database_config, tencent_request_service, db_request_service

pymysql.install_as_MySQLdb()

# app
app = Flask(__name__)

# MySQL数据库相关设置
app.config.from_object(database_config.DatabaseConfig)
db = SQLAlchemy(app)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=3)


@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('index'))


@app.route('/index', methods=['GET'])
def index():
    return render_template("index.html")


# ###############################全球################################
@app.route('/global/data', methods=['GET'])
def global_data():
    """
    全球疫情数据(包含中国)
    :return:
    """
    return db_request_service.get_global_data(GlobalWomWorld, ChinaTotal)


@app.route('/global/continent', methods=['GET'])
def global_continent():
    """
    各州累计确诊分布(海外)
    :return:
    """
    return db_request_service.get_global_continent(
        GlobalWomWorld, GlobalWomAboard)


@app.route('/global/map', methods=['GET'])
def global_map():
    """
    全球各国数据-map地图
    :return:
    """
    return db_request_service.get_global_map(GlobalWomWorld, GlobalWomAboard)


@app.route('/global/daily', methods=['GET'])
def global_daily():
    """
    全球每日疫情数据-疫情趋势图
    :return:
    """
    return db_request_service.get_global_daily(GlobalDaily)


@app.route('/global/head', methods=['GET'])
def global_head_fifteen():
    """
    各国确诊数前15
    :return:
    """
    return db_request_service.get_global_head_fifteen(
        GlobalWomWorld, GlobalWomAboard)


# ###############################国内################################

@app.route('/china/total', methods=['GET'])
def china_total():
    """
    国内汇总数据
    :return:
    """
    return db_request_service.get_china_total(
        ChinaTotal, ChinaCompareDaily)


@app.route('/china/province', methods=['GET'])
def china_province():
    """
    国内各省数据
    :return:
    """
    return db_request_service.get_china_province(ChinaTotal, ChinaProvince)


@app.route('/china/daily', methods=['GET'])
def china_compare_daily():
    """
    国内较昨日变化趋势数据
    :return:
    """
    return db_request_service.get_china_compare_daily(ChinaCompareDaily)


@app.route('/china/province/head', methods=['GET'])
def china_province_head_fifteen():
    """
    各省前15数据
    :return:
    """
    return db_request_service.get_china_province_head_fifteen(ChinaTotal, ChinaProvince)


@app.route('/china/region', methods=['GET'])
def china_region():
    """
    国内各地区数据饼图 - 如华南、华北等
    :return:
    """
    return db_request_service.get_china_region(ChinaTotal, ChinaProvince)


# ###############################城市################################
@app.route('/china/province/city/json', methods=['GET'])
def china_province_of_city_json():
    """
    获取各省对应的城市json
    :return:
    """
    return db_request_service.get_china_province_of_city_json(ChinaTotal, ChinaProvince, ChinaCity)


@app.route('/china/province/city', methods=['GET'])
def china_province_of_city():
    """
    根据省名获取城市数据
    :return:
    """
    params = request.args.to_dict()
    return db_request_service.get_china_province_of_city(ChinaTotal, ChinaProvince, ChinaCity, params)


@app.route('/china/province/daily', methods=['GET'])
def china_province_daily():
    """
    省份每日数据趋势
    :return:
    """
    province_name = request.args.to_dict()['province']
    return db_request_service.get_province_daily(ChinaProvince, province_name)


@app.route('/china/province/city/head', methods=['GET'])
def china_province_city_head_fifteen():
    """
    根据省份名称查询累计确诊数前五的城市
    :return:
    """
    params = request.args.to_dict()
    return db_request_service.china_province_city_head_fifteen(ChinaTotal, ChinaProvince, ChinaCity, params)


@app.route('/china/province/new', methods=['GET'])
def china_province_by_name():
    """
    根据省份名称获取最新的数据
    :return:
    """
    province_name = request.args.to_dict()['province']
    return db_request_service.get_china_province_by_name(ChinaTotal, ChinaProvince, province_name)


# ###############################预测################################
@app.route('/forecast/china/province', methods=['GET'])
def forecast_china_province():
    """
    预测- 根据开始结束时间查询省的数据
    :return:
    """
    province_name = request.args.to_dict()['province']
    start_time = request.args.to_dict()['start_time']
    end_time = request.args.to_dict()['end_time']
    return db_request_service.get_china_province_by_time(ChinaTotal, ChinaProvince, province_name, start_time, end_time)


# ##############
@app.route('/pull', methods=['GET'])
def pull():
    """
    调用接口进行手动数据更新
    :return:
    """
    global_str = "<h1 style='color: green; text-align: center'>全球数据-已更新!</h1>"
    china_str = "<h1 style='color: green; text-align: center'>国内数据-已更新!</h1>"
    global_is_add_or_update = Jobs.pull_global()
    if global_is_add_or_update is False:
        global_str = "<h1 style='color: orange; text-align: center'>全球数据-无更新!</h1>"
    china_is_add_or_update = Jobs.pull_china()
    if china_is_add_or_update is False:
        china_str = "<h1 style='color: orange; text-align: center'>国内数据-无更新!</h1>"
    return global_str + china_str


@app.errorhandler(Exception)
def handler_exception(err):
    app.logger.error(str(err))
    return str(err)


# #############################################################################################

class Jobs(object):
    """
    定时任务
    """

    @staticmethod
    def pull_global():
        """
        从腾讯API拉取全球数据并保持
        :return:
        """
        is_add_or_update = tencent_request_service.save_global_data(
            db=db,
            GlobalWomWorld=GlobalWomWorld,
            GlobalWomAboard=GlobalWomAboard,
            GlobalDaily=GlobalDaily)
        db.session.close()
        return is_add_or_update

    @staticmethod
    def pull_china():
        """
        从腾讯API拉取国内数据并保持
        :return:
        """
        is_add_or_update = tencent_request_service.save_china(
            db,
            ChinaTotal=ChinaTotal,
            ChinaCompareDaily=ChinaCompareDaily,
            ChinaProvince=ChinaProvince,
            ChinaCity=ChinaCity)
        db.session.close()
        return is_add_or_update


def app_init():
    """
        初始化app
    :return:
    """
    # 不启用ASCII
    app.config['JSON_AS_ASCII'] = False

    # print(database_config.DatabaseConfig.SQLALCHEMY_DATABASE_URI)


def get_app():
    return app


# def get_db():
#     return db


# #################################模型类#####################################


class GlobalWomWorld(db.Model):
    """
        全球疫情汇总数据模型
    """
    __tablename__ = 't_global_wom_world'
    id = db.Column(db.Integer, primary_key=True, comment='主键')
    now_confirm = db.Column(db.BigInteger, comment='现有确诊')
    now_confirm_add = db.Column(db.BigInteger, comment='较上日确诊新增')
    confirm = db.Column(db.BigInteger, comment='累计确诊')
    confirm_add = db.Column(db.BigInteger, comment='较上日新增确诊')
    heal = db.Column(db.BigInteger, comment='累计治愈')
    heal_add = db.Column(db.BigInteger, comment='较上日治愈')
    dead = db.Column(db.BigInteger, comment='累计死亡')
    dead_add = db.Column(db.BigInteger, comment='较上日死亡')
    death_rate = db.Column(db.FLOAT, comment='死亡率')
    cure_rate = db.Column(db.FLOAT, comment='治愈率')
    last_update_time = db.Column(db.DateTime, comment='上次更新时间', unique=True)
    date_time = db.Column(db.DateTime, comment='当前数据所在年-月-日', unique=True)

    def __self_dict__(self):
        """
        返回所有属性的字典
        :return:
        """
        return {
            'id': self.id,
            'now_confirm': self.now_confirm,
            'now_confirm_add': self.now_confirm_add,
            'confirm': self.confirm,
            'confirm_add': self.confirm_add,
            'heal': self.heal,
            'heal_add': self.heal_add,
            'dead': self.dead,
            'dead_add': self.dead_add,
            'death_rate': self.death_rate,
            'cure_rate': self.cure_rate,
            'last_update_time': str(self.last_update_time),
            'date_time': str(self.date_time)
        }


class GlobalWomAboard(db.Model):
    """
        全球各个国家疫情数据模型
    """
    __tablename__ = 't_global_wom_aboard'
    id = db.Column(db.Integer, primary_key=True, comment='主键')
    continent = db.Column(db.String(64), comment='大洲')
    name = db.Column(db.String(64), comment='国家')
    confirm = db.Column(db.BigInteger, comment='累计确诊')
    confirm_add = db.Column(db.BigInteger, comment='较上日新增确诊')
    dead = db.Column(db.BigInteger, comment='累计死亡')
    dead_compare = db.Column(db.BigInteger, comment='较上日死亡')
    heal = db.Column(db.BigInteger, comment='累计治愈')
    heal_compare = db.Column(db.BigInteger, comment='较上日治愈')
    now_confirm = db.Column(db.BigInteger, comment='现有确诊')
    now_confirm_compare = db.Column(db.BigInteger, comment='较上日确诊')
    global_wom_world_id = db.Column(
        db.Integer,
        db.ForeignKey('t_global_wom_world.id'),
        comment='外键到同一时间的全球汇总数据')

    __table_args__ = (
        db.UniqueConstraint('name', 'global_wom_world_id', name='uk_name_global_wom_world_id'),
    )

    def __self_dict__(self):
        """
        返回所有属性的字典
        :return:
        """
        return {
            'id': self.id,
            'continent': self.continent,
            'name': self.name,
            'confirm': self.confirm,
            'confirm_add': self.confirm_add,
            'dead': self.dead,
            'dead_compare': self.dead_compare,
            'heal': self.heal,
            'heal_compare': self.heal_compare,
            'now_confirm': self.now_confirm,
            'now_confirm_compare': self.now_confirm_compare,
            'global_wom_world_id': self.global_wom_world_id
        }


class GlobalDaily(db.Model):
    """
        全球疫情汇总数据模型
    """
    __tablename__ = 't_global_daily'
    id = db.Column(db.Integer, primary_key=True, comment='主键')
    confirm = db.Column(db.BigInteger, comment='累计确诊')
    dead = db.Column(db.BigInteger, comment='累计死亡')
    heal = db.Column(db.BigInteger, comment='累计治愈')
    new_add_confirm = db.Column(db.BigInteger, comment='较上日新增确诊')
    dead_rate = db.Column(db.FLOAT, comment='死亡率')
    heal_rate = db.Column(db.FLOAT, comment='治愈率')
    date_time = db.Column(db.DateTime, comment='数据时间', unique=True)

    def __self_dict__(self):
        """
        返回所有属性的字典
        :return:
        """
        return {
            'id': self.id,
            'confirm': self.confirm,
            'dead': self.dead,
            'heal': self.heal,
            'new_add_confirm': self.new_add_confirm,
            'dead_rate': self.dead_rate,
            'heal_rate': self.heal_rate,
            'date_time': self.date_time.date().__str__()
        }


class ChinaTotal(db.Model):
    """
    中国疫情汇总
    """
    __tablename__ = 't_china_total'
    id = db.Column(db.Integer, primary_key=True, comment='主键')
    confirm = db.Column(db.BigInteger, comment='累计确诊')
    heal = db.Column(db.BigInteger, comment='累计治愈')
    dead = db.Column(db.BigInteger, comment='累计死亡')
    now_confirm = db.Column(db.BigInteger, comment='现有确诊')
    suspect = db.Column(db.BigInteger, comment='现有疑似')
    now_severe = db.Column(db.BigInteger, comment='现有重症')
    last_update_time = db.Column(db.DateTime, comment='上次更新时间', unique=True)
    date_time = db.Column(db.DateTime, comment='数据时间', unique=True)

    def __self_dict__(self):
        """
        返回所有属性的字典
        :return:
        """
        return {
            'id': self.id,
            'confirm': self.confirm,
            'heal': self.heal,
            'dead': self.dead,
            'now_confirm': self.now_confirm,
            'suspect': self.suspect,
            'now_severe': self.now_severe,
            'last_update_time': str(self.last_update_time),
            'date_time': get_date_by_standard_time(str(self.date_time))
        }


class ChinaCompareDaily(db.Model):
    """
    中国每日疫情数据较昨日变化
    """
    __tablename__ = 't_china_compare_daily'
    id = db.Column(db.Integer, primary_key=True, comment='主键')
    confirm_compare = db.Column(db.BigInteger, comment='较昨日确诊')
    heal_compare = db.Column(db.BigInteger, comment='较昨日治愈')
    dead_compare = db.Column(db.BigInteger, comment='较昨日死亡')
    now_confirm_compare = db.Column(db.BigInteger, comment='较昨日现有确诊')
    suspect_compare = db.Column(db.BigInteger, comment='较昨日疑似')
    now_severe_compare = db.Column(db.BigInteger, comment='较昨日重症')
    date_time = db.Column(db.DateTime, unique=True, comment='上次更新时间-的年月日')
    china_total_id = db.Column(
        db.Integer,
        db.ForeignKey('t_china_total.id'),
        comment='外键到同一时间的国内总数据')

    __table_args__ = (
        db.UniqueConstraint('date_time', 'china_total_id', name='uk_date_time_china_total_id'),
    )

    def __self_dict__(self):
        """
        返回所有属性的字典
        :return:
        """
        return {
            'id': self.id,
            'confirm_compare': self.confirm_compare,
            'heal_compare': self.heal_compare,
            'dead_compare': self.dead_compare,
            'now_confirm_compare': self.now_confirm_compare,
            'suspect_compare': self.suspect_compare,
            'now_severe_compare': self.now_severe_compare,
            'date_time': get_date_by_standard_time(str(self.date_time)),
            'china_total_id': self.china_total_id
        }


class ChinaProvince(db.Model):
    """
    中国各省数据汇总
    """
    __tablename__ = 't_china_province'
    id = db.Column(db.Integer, primary_key=True, comment='主键')
    name = db.Column(db.String(64), comment='省')
    confirm = db.Column(db.BigInteger, comment='累计确诊')
    heal = db.Column(db.BigInteger, comment='累计治愈')
    dead = db.Column(db.BigInteger, comment='累计死亡')
    now_confirm = db.Column(db.BigInteger, comment='现有确诊')
    confirm_compare = db.Column(db.BigInteger, comment='较昨日确诊')
    china_total_id = db.Column(
        db.Integer,
        db.ForeignKey('t_china_total.id'),
        comment='外键到同一时间的国内总数据id')
    # 使用此字段可以直接查询外键关联的china_total
    china_total = db.relationship('ChinaTotal', backref=db.backref('provinces'))

    __table_args__ = (
        db.UniqueConstraint('name', 'china_total_id', name='uk_name_china_total_id'),
    )

    def __self_dict__(self):
        """
        返回所有属性的字典, 不包括date_time
        :return:
        """
        return {
            'id': self.id,
            'name': self.name,
            'confirm': self.confirm,
            'heal': self.heal,
            'dead': self.dead,
            'now_confirm': self.now_confirm,
            'confirm_compare': self.confirm_compare,
            'china_total_id': self.china_total_id
        }

    def __self_dict_and_date_time__(self):
        """
        返回所有属性的字典, 包括date_time
        :return:
        """
        return {
            'id': self.id,
            'name': self.name,
            'confirm': self.confirm,
            'heal': self.heal,
            'dead': self.dead,
            'now_confirm': self.now_confirm,
            'confirm_compare': self.confirm_compare,
            'china_total_id': self.china_total_id,
            'date_time': get_date_by_standard_time(str(self.china_total.date_time))
        }


class ChinaCity(db.Model):
    """
    中国各城市数据汇总
    """
    __tablename__ = 't_china_city'
    id = db.Column(db.Integer, primary_key=True, comment='主键')
    name = db.Column(db.String(64), comment='城市')
    confirm = db.Column(db.BigInteger, comment='累计确诊')
    heal = db.Column(db.BigInteger, comment='累计治愈')
    dead = db.Column(db.BigInteger, comment='累计死亡')
    now_confirm = db.Column(db.BigInteger, comment='现有确诊')
    confirm_compare = db.Column(db.BigInteger, comment='较昨日确诊')
    china_province_id = db.Column(
        db.Integer,
        db.ForeignKey('t_china_province.id'),
        comment='外键到所属省份id')

    __table_args__ = (
        db.UniqueConstraint('name', 'china_province_id', name='uk_name_china_province_id'),
    )

    def __self_dict__(self):
        """
        返回所有属性的字典
        :return:
        """
        return {
            'id': self.id,
            'name': self.name,
            'confirm': self.confirm,
            'heal': self.heal,
            'dead': self.dead,
            'now_confirm': self.now_confirm,
            'confirm_compare': self.confirm_compare,
            'china_province_id': self.china_province_id
        }


# ###############################################################################

def table_init():
    """
    表结构初始化
    :return:
    """
    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    # 开启定时任务
    schedule = APScheduler()
    schedule.init_app(app)

    # app初始化
    app_init()
    # MySQL表初始化
    # table_init()

    # 添加定时任务
    schedule.add_job(id='pull_global', func=Jobs.pull_global, trigger='interval', minutes=10)
    schedule.add_job(id='pull_china', func=Jobs.pull_china, trigger='interval', minutes=10)
    schedule.start()

    app.run(debug=True, use_reloader=False)
