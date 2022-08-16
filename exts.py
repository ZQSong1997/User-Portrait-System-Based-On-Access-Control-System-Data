#encoding: utf-8

#该文件存放db，解决循环引用
from flask_sqlalchemy import SQLAlchemy
#使用Flask-SQLAlchemy创建模型与表的映射
db = SQLAlchemy()
