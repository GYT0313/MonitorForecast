# -*- coding: UTF-8 -*-
import pymysql
from flask import Flask
from flask import redirect, url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

from src import database_config, request_service

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


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    request_service.save_wom_world()
    return 'hello'


def app_init():
    """
        初始化app
    :return:
    """
    # 不启用ASCII
    app.config['JSON_AS_ASCII'] = False

    print(database_config.DatabaseConfig.SQLALCHEMY_DATABASE_URI)

    return app


def database_init(database):
    database.drop_all()
    database.create_all()


def get_app():
    return app


def get_db():
    return db


"""
模型类
"""


class GlobalWomAWorld(db.Model):
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
    global_wom_world_id = db.Column(
        db.Integer,
        db.ForeignKey('t_global_wom_world.id'),
        comment='外键到同一时间的全球汇总数据')

    def __repr__(self):
        return self.name


if __name__ == '__main__':
    app_init()
    database_init(db)

    app.run(debug=True)
