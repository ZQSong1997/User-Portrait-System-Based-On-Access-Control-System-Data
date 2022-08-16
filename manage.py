#encoding: utf-8

#该文件用做数据库迁移配置
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from portrait import app
from exts import db
from Modelku import User,BasicProperty,HouseProperty,AccessProperty,CommunityProperty

#从Modelku中导入用户模型
#flask_script可以通过命令行的形式来操作Flask
#flask_migrate可以在每次修改模型后，可以将修改的东西映射到数据库中。

# 模型 -> 迁移文件 -> 表
# Manager初始化要导入app
manager = Manager(app)
# 使用Migrate绑定app和db
migrate = Migrate(app, db)
# 添加迁移脚本的命令到manager中
manager.add_command('db', MigrateCommand)
#把MigrateCommand命令添加到manager中，名字是db，MigrateCommand中包含了所有和数据库相关的命令

if __name__ == "__main__":
    manager.run()