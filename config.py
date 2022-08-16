#encoding: utf-8

#配置文件，配置数据库
import os
DEBUG = True
SECRET_KEY = os.urandom(24)

DIALECT = 'mysql'      #要用的什么数据库
DRIVER = 'mysqldb'     #连接数据库驱动
HOST = '127.0.0.1'     #服务器
PORT = '3306'          #端口
DATABASE = 'UserPortrait'  #数据库名称
USERNAME = 'root'      #用户名
PASSWORD = '1230'      #密码
DB_URI = '{}+{}://{}:{}@{}:{}/{}?charset=utf8'.format(DIALECT,DRIVER,USERNAME,PASSWORD,HOST,PORT,DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False
#SQLALCHEMY发生变化，不去跟踪修改