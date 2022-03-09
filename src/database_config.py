# -*- coding: UTF-8 -*-

host = '127.0.0.1'
port = 3306
database_name = 'monitor_forecast_dev'
username = 'root'
password = '123456'


class DatabaseConfig:
    """
        MySQL数据库相关设置
    """
    SQLALCHEMY_DATABASE_URI = 'mysql://' + username + ":" + password + "@" + host + ":" + str(
        port) + "/" + database_name
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # SQLAlchemy 会记录所有 发给 stderr 的语句
    SQLALCHEMY_ECHO = True
    # 可以用于显式地禁用或启用查询记录. 在调试或测试模式自动启用
    SQLALCHEMY_RECORD_QUERIES = True
