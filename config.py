import redis


class Config(object):
    """配置信息"""
    SECRET_KEY = "bXlpbmZvcm1hdGlvbg=="

    #  开启提示信息
    DEBUG = True

    #  数据库配置信息
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456789@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #  session配置
    SESSION_TYPE = "redis"  # 指定session保存到redis中
    SESSION_USE_SIGNER = True  # 让cookie中的session_id被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用redis的实例
    PERMANENT_SEESION_LIFETIME = 86400  # session的有效期为30天
