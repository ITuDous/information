# 定义过滤器
import functools

from flask import session, current_app, g

from info.models import User


def func_index_convert(index):
    index_dict = {1: "first", 2: "second", 3: "third"}
    return index_dict.get(index, "")


# 装饰器来封装登陆信息的查询
def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 判断用户是否登陆,session中是否保存了user_id
        user_id = session.get("user_id")
        user = None
        if user_id:
            # 根据user_id获取用户信息
            try:
                user = User.query.get(user_id)
            except BaseException as e:
                current_app.logger.error(e)

        g.user = user
        return f(*args, **kwargs)
    return wrapper
