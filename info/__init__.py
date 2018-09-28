import logging
from logging.handlers import RotatingFileHandler

import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_migrate import Migrate
from config import config_dict


#  设置数据库连接对象
from info.common import func_index_convert

db = None  # type:SQLAlchemy
redis_store = None  # type:redis.StrictRedis


def setup_log(log_level):
    # 设置日志的记录等级
    logging.basicConfig(level=log_level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(pathname)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_type):
    #  根据类型取出配置类
    config_class = config_dict[config_type]

    app = Flask(__name__)

    #  csrf保护
    # CSRFProtect(app)

    #  从对象加载配置信息
    app.config.from_object(config_class)

    global db, redis_store

    #  配置数据库
    db = SQLAlchemy(app)

    #  配置redis
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT,decode_responses=True)

    #  配置session保存位置
    Session(app)

    #  创建迁移器
    Migrate(app, db)

    #  注册路由
    from info.modules.home import home_blu
    app.register_blueprint(home_blu)
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)
    from info.modules.news import news_blu
    app.register_blueprint(news_blu)

    #  配置文件
    setup_log(config_class.LOG_LEVEL)

    #  关联文件
    import info.models

    # 添加过滤器
    app.add_template_filter(func_index_convert, "index_convert")

    return app

