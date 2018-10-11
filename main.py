from flask import current_app
from flask_migrate import MigrateCommand
from flask_script import Manager
from info import create_app

# 创建应用
app = create_app("dev")

# 创建管理器
manager = Manager(app)

# 添加迁移命令
manager.add_command("mc", MigrateCommand)


# 生成管理员命令
@manager.option("-u", dest="username")
@manager.option("-p", dest="password")
def create_superuser(username, password):
    if not all([username, password]):
        print("参数不完整")
        return

    from info.models import User
    from info import db

    # 创建管理员
    user = User()
    user.mobile = username
    user.password = password
    user.nick_name = username
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        db.session.rollback()
        print("数据库保存失败")

    print("管理员创建成功")


if __name__ == '__main__':
    manager.run()
