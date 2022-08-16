#encoding: utf-8

#该文件存放所有模型class，定义数据库的各种表
from exts import db

#系统管理员信息表
class User(db.Model):
    __tablename__ = 'user'   #定义数据库表的名称为user
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户id')
    username = db.Column(db.String(20), nullable=False, comment='用户名')
    password = db.Column(db.String(20), nullable=False, comment='密码')

#用户基本属性表
class BasicProperty(db.Model):
    __tablename__ = 'basicproperty'
    userid = db.Column(db.Integer, autoincrement=True, comment='自增列')
    yhid = db.Column(db.Integer, primary_key=True, comment='用户id')
    sex = db.Column(db.Integer, nullable=False, comment='性别')
    nlqt = db.Column(db.Integer, nullable=False, comment='年龄群体')
    sjxh = db.Column(db.Integer, comment='手机型号')
    clxx = db.Column(db.Integer, nullable=False, comment='车辆信息')
    gxsj = db.Column(db.DateTime, nullable=False, comment='数据更新时间')
    Consumers = db.Column(db.String(20), comment='消费群体标签')

#住房属性表
class HouseProperty(db.Model):
    __tablename__ = 'houseproperty'
    houseid = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增列')
    fwid = db.Column(db.Integer, nullable=False, comment='房屋编号')
    yhid = db.Column(db.Integer, nullable=False, comment='用户id')
    rygx = db.Column(db.Integer, comment='人员关系')
    sex = db.Column(db.Integer, comment='性别')
    nlqt = db.Column(db.Integer, comment='年龄群体')
    xqid = db.Column(db.Integer, nullable=False, comment='小区id')
    fwdy = db.Column(db.String(20), nullable=False, comment='房屋单元')
    fwh = db.Column(db.Integer, nullable=False, comment='房屋门牌号')

#访问属性表
class AccessProperty(db.Model):
    __tablename__ = 'accessproperty'
    accessid = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增列')
    yhid = db.Column(db.Integer, nullable=False, comment='用户id')
    xqid = db.Column(db.Integer, nullable=False, comment='小区id')
    sbjcd = db.Column(db.String(20), comment='进门检测站点')
    sbid = db.Column(db.Integer, comment='门禁设备编号')
    kmfs = db.Column(db.Integer, nullable=False, comment='开门方式')
    kmsj = db.Column(db.DateTime, nullable=False, comment='开门时间')

#小区属性表
class CommunityProperty(db.Model):
    __tablename__ = 'communityproperty'
    xqid = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='小区id')
    xqmc = db.Column(db.String(20), nullable=False, comment='小区名称')
    city = db.Column(db.String(20), nullable=False, comment='所在城市')
    city_houseprice = db.Column(db.Integer, comment='所在城市二手房均价')
    community_houseprice = db.Column(db.Integer, comment='所在小区二手房均价')

#     classe = db.relationship('Class', secondary=zhongjianbiao,
#                              backref=db.backref('student', lazy='dynamic'), lazy='dynamic')
#
# #中间表
# zhongjianbiao = db.Table('zhongjianbiao',
#                          db.Column('yh_nlqt', db.Integer, db.ForeignKey('basicproperty.nlqt')),
#                          db.Column('yh_yhid', db.Integer, db.ForeignKey('accessproperty.yhid')))

# basicproperty.nlqt、accessproperty.yhid为需要关联的表名字





