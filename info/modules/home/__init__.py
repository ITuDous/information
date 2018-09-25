from flask import Blueprint

#  创建蓝图
home_blu = Blueprint("home", __name__)

#  关联路由
from .views import *
