import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session
from config import Config

app = Flask(__name__)

#  配置
app.config.from_object(Config)
#  配置数据库
db = SQLAlchemy(app)
#  配置redis
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
#  配置session保存位置
Session(app)