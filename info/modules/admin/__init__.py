from flask import Blueprint

admin_blu = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blu.before_request
def check_superuser():
    # 判断管理员是否登陆,如果没有登陆,重定向到前台首页
    is_admin = session.get("is_admin")

    if not is_admin and not request.url.endswith("admin/login"):
        return redirect(url_for("home.index"))


from .views import *
