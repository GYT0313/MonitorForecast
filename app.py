# -*- coding: UTF-8 -*-
import pymysql
from flask import Flask
from flask import redirect, url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

from src import database_config, tencent_request_service, db_request_service

pymysql.install_as_MySQLdb()

# app
app = Flask(__name__)

# MySQL数据库相关设置
app.config.from_object(database_config.DatabaseConfig)
db = SQLAlchemy(app)


@app.route('/', methods=['GET', 'POST'])
def home():
    return redirect(url_for('index'))


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route('/global/continent')
def global_continent():
    """
    各州累计确诊分布(海外)
    :return:
    """
    return db_request_service.get_global_continent(GlobalWomWorld, GlobalWomAboard)


@app.route('/global/map')
def global_map():
    """
    全球各国数据-map地图
    :return:
    """
    return db_request_service.get_global_map(GlobalWomWorld, GlobalWomAboard)


@app.route('/global/daily_list')
def global_daily_list():
    """
    全球每日疫情数据-疫情趋势图
    :return:
    """
    return db_request_service.get_global_daily_list(GlobalDailyList)


@app.route('/global/head')
def global_head_fifteen():
    """
    各国确诊数前15
    :return:
    """
    return db_request_service.get_global_head_fifteen(GlobalWomWorld, GlobalWomAboard)


@app.route('/pull', methods=['GET', 'POST'])
def pull():
    tencent_request_service.save_global_data(db, GlobalWomWorld, GlobalWomAboard)
    tencent_request_service.save_global_daily_list(db, GlobalDailyList)
    return 'save_global_wom_world'


def app_init():
    """
        初始化app
    :return:
    """
    # 不启用ASCII
    app.config['JSON_AS_ASCII'] = False

    print(database_config.DatabaseConfig.SQLALCHEMY_DATABASE_URI)

    return app


def get_app():
    return app


# def get_db():
#     return db


"""
模型类
"""


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
    last_update_time = db.Column(db.DateTime, comment='上次更新时间')

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
            'last_update_time': self.last_update_time
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
    last_update_time = db.Column(db.DateTime, comment='上次更新时间')

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
            'last_update_time': self.last_update_time
        }

    # global_wom_world_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey('t_global_wom_world.id'),
    #     comment='外键到同一时间的全球汇总数据')


class GlobalDailyList(db.Model):
    """
        全球疫情汇总数据模型
    """
    __tablename__ = 't_global_wom_daily_list'
    id = db.Column(db.Integer, primary_key=True, comment='主键')
    confirm = db.Column(db.BigInteger, comment='累计确诊')
    dead = db.Column(db.BigInteger, comment='累计死亡')
    heal = db.Column(db.BigInteger, comment='累计治愈')
    new_add_confirm = db.Column(db.BigInteger, comment='较上日新增确诊')
    dead_rate = db.Column(db.FLOAT, comment='死亡率')
    heal_rate = db.Column(db.FLOAT, comment='治愈率')
    date_time = db.Column(db.DateTime, comment='数据时间')

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


if __name__ == '__main__':
    app_init()
    # db.drop_all()
    # db.create_all()

    app.run(debug=True)
