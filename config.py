import redis
import logging


class Config(object):
    """配置信息"""
    SECRET_KEY = "bXlpbmZvcm1hdGlvbg=="

    #  开启提示信息
    DEBUG = True

    #  数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456789@127.0.0.1:3306/information?charset=utf8"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #  session配置
    SESSION_TYPE = "redis"  # 指定session保存到redis中
    SESSION_USE_SIGNER = True  # 让cookie中的session_id被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用redis的实例
    PERMANENT_SEESION_LIFETIME = 86400  # session的有效期为31天
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = logging.ERROR


config_dict = {
    "dev": DevelopmentConfig,
    "pro": ProductConfig
}
