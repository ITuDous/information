from info import create_app
from flask_migrate import MigrateCommand
from flask_script import Manager

#  创建应用
app = create_app("dev")
#  创建管理器
manager = Manager(app)
#  添加迁移命令
manager.add_command("mc", MigrateCommand)


if __name__ == '__main__':
    manager.run()




