# -*- coding:utf-8 -*-
#主app文件
from flask import Flask,render_template,request,redirect,url_for,flash,session
import userWordCloud
import requests
import config
import numpy as np
import matplotlib.pyplot as plt
from Modelku import User,BasicProperty,HouseProperty,AccessProperty,CommunityProperty
from exts import db
from functools import wraps
from collections import Counter
from lxml import etree
from xpinyin import Pinyin


# render_template(.html)跳转到html页面
# request请求函数
# redirect(路由名url)重定向跳转到路由
# url_for(函数名)即可跳转到函数所在的路由url
# flash是闪现
# 因为flask的session是通过加密之后放到了cookie中, 所以有加密就有密钥用于解密
# 所以只要用到了flask的session模块就一定要配置“SECRET_KEY”这个全局宏, 一般设置为24位的字符

app = Flask(__name__)          # 初始化一个Flask对象
app.config.from_object(config) #从config.py文件导入配置参数  # 载入配置文件
db.init_app(app)

# 登录限制的装饰器,f表示需要传入一个函数
def is_login(f):
    """装饰器: 用来判断用户是否登录成功"""
    @wraps(f)  # 可以保留被装饰函数f的函数名__name__和帮助信息文档
    def wrapper(*args, **kwargs):
        if session.get('username'):  # 判断session对象中是否有seesion['username'], None
            return f(*args, **kwargs)  # 如果包含信息, 则登录成功, 可以访问主页
        else:
            flash("请先登录！")
            return redirect(url_for('login'))  # 如果不包含信息, 则未登录成功, 跳转到登录界面
    return wrapper

@app.route('/')
def index():  #进入主页
    return render_template('index.html')
    # return render_template('portrait.html') 等价于 return redirect(url_for('portrait')) ？  错
    # 左返回的是网页，右返回的是路由

@app.route('/login/',methods=['GET','POST']) # 创建登陆页面路由, 数据传输方法为GET/POST
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')  #读入表单提交数据
        password = request.form.get('upassword')
        uname = User.query.filter(User.username == username).first() #从数据库查询是否用户存在
        upass = User.query.filter(User.password == password).first() #从数据库查询是否密码正确
        # 检查用户名和密码是否都正确
        if uname and upass:
            session['username'] = username  #将管理员的用户名和密码保存到session里的cookie
            session['username'] = password
            return redirect(url_for('inquery'))
        else:
            flash("用户名或密码错误，请确认后登录！")
            return redirect(url_for('login'))

@app.route('/regist/',methods=['GET','POST'])  #管理员注册
@is_login
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter(User.username == username).first()
        if user:
            flash("该用户名已存在，请更换名字！")
            return redirect(url_for('regist'))
        else:
            if password1 != password2:
                flash("两次密码不一致，请核对后再填写！")
                return redirect(url_for('regist'))
            else:
                user = User(username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                flash("注册成功，请登录")
                return redirect(url_for('login'))


@app.route('/change/',methods=['GET','POST'])  #更换密码
@is_login
def change():
    if request.method == 'GET':
        return render_template('chpass.html')
    else:
        oldpassword = request.form.get('oldpassword')
        newpassword1 = request.form.get('newpassword1')
        newpassword2 = request.form.get('newpassword2')
        if newpassword1 != newpassword2:
            flash("两次密码不一致，请核对后再填写！")
            return redirect(url_for('change'))
        else:
             user = User.query.filter(User.password == oldpassword).first()
             if user:
                user.password = newpassword1
                db.session.commit()
                flash("密码修改成功，请重新登录！")
                return redirect(url_for('login'))
             else:
                 flash("旧密码输入错误！")
                 return redirect(url_for('change'))

@app.route('/logout/',methods=['GET','POST'])  # 注销用户信息
@is_login    #检测是否登录
def logout():
    session.pop('username')  #从session中清除用户名
    session.pop('password')  #从session中清除密码
    return render_template('logout.html')  #跳转到退出页面

# 爬虫函数
def SpiderCityHousePrice(city):
    xqcs = city[3:]  # 提取城市名称，如桂林
    xqcs_pinyin = Pinyin().get_pinyin(u"%s" % xqcs, '')  # 先使用Pinyin（）函数将城市和小区的中文名称转为拼音
    city_url = "https://fangjia.fang.com/%s/" % xqcs_pinyin  # 生成用户所在城市平均房价数据的url链接
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
                                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
    def spider(url, headers):  # 根据url爬取目标站点，返回源码
        try:
            response = requests.get(url, headers=headers)
            response.encoding = response.apparent_encoding  # 自动判断字符集类型
            return response.text
        except:
            print('爬取站点失败，请检查url是否正确或连接是否可用！')
    city_html = spider(city_url, headers)
    city_etree_html = etree.HTML(city_html)
    # 定位目标数据，取其值，列表类型
    city_price = city_etree_html.xpath('/html/body/div[3]/div[2]/dl/dd[1]/div/h3/text()')
    city_house_price = ''.join(city_price)
    print(city_url)
    return city_house_price

def SpiderCommunityHousePrice(xqmc):
    xqmc_pinyin = Pinyin().get_pinyin(u"%s" % xqmc, '')  # 先使用Pinyin（）函数将小区的中文名称转为拼音
    community_url = "https://%s.fang.com/" % xqmc_pinyin  # 生成住户所在小区平均房价数据的url链接
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
                                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
    def spider(url, headers):  # 根据url爬取目标站点，返回源码
        try:
            response = requests.get(url, headers=headers)
            response.encoding = response.apparent_encoding  # 自动判断字符集类型
            return response.text
        except:
            print('爬取站点失败，请检查url是否正确或连接是否可用！')
    community_html = spider(community_url, headers)
    community_etree_html = etree.HTML(community_html)
    community_price = community_etree_html.xpath('//*[@id="body"]/div[5]/div[2]/div[2]/span[1]/text()')
    community_house_price = ''.join(community_price)
    print(community_url)
    return community_house_price

@app.route('/XqInquery/',methods=['GET','POST']) #查询社区画像
@is_login   #调用is_login装饰器，检测是否登录，必须是登录状态才能执行此操作
def XqInquery():
    if request.method == 'GET':
        return render_template('XqInquery.html')
    else:
        xq_id = request.form.get('xq_id')
        community = CommunityProperty.query.filter(CommunityProperty.xqid == xq_id).first()
        if not xq_id.isdigit():        #判断输入id是否纯数字
            flash('输入字符非法，请输入正确id号！')
            return render_template('XqInquery.html')
        elif community is None:        #判断输入id是否存在
            flash('暂无%s号社区画像数据' % xq_id)
            return render_template('XqInquery.html')
        else:
            # 小区属性
            xqid = community.xqid  # 小区id（数字）
            xqmc = community.xqmc  # 小区名称（中文）
            city = community.city  # 小区所在省份-城市（中文），如广西-桂林
            # 小区用户数据更新时间GXSJ,只显示日期date,用于web页面右上角显示
            GXSJ = AccessProperty.query.filter(AccessProperty.xqid == xqid).order_by(
                AccessProperty.kmsj.desc()).first()   #逆序
            GXSJ = GXSJ.kmsj.date()
            # 数据统计
            # 统计住房类型情况(购房人数=住户人数+亲人人数，租房人数=租客人数）
            huzhu = HouseProperty.query.filter(HouseProperty.rygx == 0).count()
            qinren = HouseProperty.query.filter(HouseProperty.rygx == 1).count()
            zuke = HouseProperty.query.filter(HouseProperty.rygx == 2).count()
            GF = huzhu + qinren
            ZF = zuke
            # 统计车辆类型情况（汽车、货车、摩托车、电动车、无车）
            car = BasicProperty.query.filter(BasicProperty.clxx == 0).count()
            trunk = BasicProperty.query.filter(BasicProperty.clxx == 1).count()
            motorcycle = BasicProperty.query.filter(BasicProperty.clxx == 2).count()
            electriccar = BasicProperty.query.filter(BasicProperty.clxx == 3).count()
            nocar = BasicProperty.query.filter(BasicProperty.clxx == 4).count()
            # 统计各年龄段和性别分布（女儿童、男儿童...少年、青年、中年、女老年、男老年）
            ertongG = BasicProperty.query.filter(BasicProperty.sex == 0, BasicProperty.nlqt == 0).count()
            ertongB = BasicProperty.query.filter(BasicProperty.sex == 1, BasicProperty.nlqt == 0).count()
            shaonianG = BasicProperty.query.filter(BasicProperty.sex == 0, BasicProperty.nlqt == 1).count()
            shaonianB = BasicProperty.query.filter(BasicProperty.sex == 1, BasicProperty.nlqt == 1).count()
            qinnianG = BasicProperty.query.filter(BasicProperty.sex == 0, BasicProperty.nlqt == 2).count()
            qinnianB = BasicProperty.query.filter(BasicProperty.sex == 1, BasicProperty.nlqt == 2).count()
            zongnianG = BasicProperty.query.filter(BasicProperty.sex == 0, BasicProperty.nlqt == 3).count()
            zongnianB = BasicProperty.query.filter(BasicProperty.sex == 1, BasicProperty.nlqt == 3).count()
            laonianG = BasicProperty.query.filter(BasicProperty.sex == 0, BasicProperty.nlqt == 4).count()
            laonianB = BasicProperty.query.filter(BasicProperty.sex == 1, BasicProperty.nlqt == 4).count()
            # 统计开门方式偏好（输密码、刷脸、门禁卡）
            passw = AccessProperty.query.filter(AccessProperty.kmfs == 0).count()
            face = AccessProperty.query.filter(AccessProperty.kmfs == 1).count()
            card = AccessProperty.query.filter(AccessProperty.kmfs == 2).count()

            # # 统计手机类型情况（Android、iOS、无）
            # Android = BasicProperty.query.filter(BasicProperty.sjxh == 0).count()
            # iOS = BasicProperty.query.filter(BasicProperty.sjxh == 1).count()
            # nophone = BasicProperty.query.filter(BasicProperty.sjxh == 2).count()
            # 扩展：统计小区每日每个单元门的访问次数（6栋1单元单元门、7栋1单元单元门、7栋2单元单元门、8栋1单元单元门、8栋2单元单元门）


            # 正式开始绘制画像
            # 访问数据处理(总访问量、少年群体访问量、青年访问量、中年访问量、老年访问量）
            shao_fwsj_list = []
            # 遍历少年群体的访问情况
            # SHAO_ACCESS = AccessProperty.query.filter(AccessProperty.xqid == xqid,)
            # for SHAO_KMSJS in SHAO_ACCESS:
            #     kmdate = SHAO_KMSJS.kmsj.date()
            #     kmstr = str(kmdate)
            #     kmsj = kmstr[5:]
            #     shao_fwsj_list.append(kmsj)
            sum_list = []
            SUM_ACCESS = AccessProperty.query.filter(AccessProperty.xqid == xqid)
            # 遍历所有人的访问情况
            for KMSJS in SUM_ACCESS:
                kmdate = KMSJS.kmsj.date()
                kmstr = str(kmdate)    #将日期类型datetime.date转换成字符串str类型
                kmsj = kmstr[5:]       #只保留原日期的具体天数，如02-18
                sum_list.append(kmsj)  #将访问时间全部存到列表date_list中
            # 统计各群体每日的访问次数fwcs,得到一个字典
            sum_fwcs = Counter(sum_list)
            shao_fwcs = Counter(shao_fwsj_list)
            # 将访问时间存入相应列表
            sum_fwsj_list = []
            for key in sum_fwcs.keys():
                sum_fwsj_list.append(key)
            # 将各群体访问次数存入相应列表
            sum_fwcs_list = []
            for value in sum_fwcs.values():
                sum_fwcs_list.append(value)
            shao_fwcs_list = []
            for value in shao_fwcs.values():
                shao_fwcs_list.append(value)
            # 设置全局字体样式
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False
            # 绘制住房类型情况图 ZFLX ，饼图
            ZFlabels = ['买房', '租房']
            ZFLX = [GF, ZF]
            color = ['orange', 'darkviolet']
            plt.axes(aspect='equal')
            plt.pie(x=ZFLX, labels=ZFlabels, autopct='%.1f%%', explode=[0.1, 0], colors=color,
                    wedgeprops={'linewidth': 1.5, 'edgecolor': 'black'},
                    textprops={'fontsize': 16, 'color': 'black'})
            plt.title('住户住房情况', fontproperties='SimHei', fontsize=20)
            plt.savefig('./static/images/社区画像结果/住房类型情况画像.png', dpi=400, bbox_inches='tight')
            plt.close()

            # 绘制车辆类型情况图 CLLX ，饼图
            Carlabels = ['汽车', '电动车', '货车', '摩托车', '无车']
            CLLX = [car, electriccar, trunk, motorcycle, nocar]
            explode = [0.1, 0, 0, 0, 0]
            color = ['yellow', 'red', 'blue', 'green','magenta']
            plt.axes(aspect='equal')
            plt.pie(x=CLLX, labels=Carlabels, autopct='%.1f%%',explode=explode, colors=color,
                    wedgeprops={'linewidth': 1.5, 'edgecolor': 'black'},textprops={'fontsize': 16, 'color': 'black'})
            plt.title('住户拥有车辆情况', fontproperties='SimHei', fontsize=20)
            plt.savefig('./static/images/社区画像结果/汽车类型情况画像.png', dpi=400, bbox_inches='tight')
            plt.close()

            # 绘制小区日访问量情况图 FWCS
            x = sum_fwsj_list
            y = sum_fwcs_list
            plt.figure(figsize=(8, 5))  # 创建绘图对象，可改变图片大小
            # 绘制折线图
            plt.plot(x, y, color='red', linewidth=2)
            for a, b in zip(x, y):
                plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=9)  # 使用text显示数值
            plt.ylim(0, 500)  # 设置Y轴上下限
            plt.xlabel('访问日期', fontsize=16)
            plt.ylabel("人次/天", fontproperties='SimHei', fontsize=16)  # Y轴标签
            plt.xticks(rotation=45, fontsize=11)  # x坐标轴字体设置为倾斜45°
            plt.grid()  # 加入网格
            plt.title("小区近28天日访问量情况", fontproperties='SimHei', fontsize=20)  # 图标题
            plt.savefig('./static/images/社区画像结果/小区近28天日访问量情况画像.png', dpi=400, bbox_inches='tight')
            plt.close()

            # 绘制小区住户年龄段和性别分布图 NLD
            # plt.rcParams["font.sans-serif"] = ["SimHei"]
            NLlabels = ['儿童', '少年', '青年', '中年', '老年']   # 柱高信息
            NLD_B = [ertongB, shaonianB, qinnianB, zongnianB, laonianB]  #存放男性群体各年龄段个数
            NLD_G = [ertongG, shaonianG, qinnianG, zongnianG, laonianG]  #存放女性群体各年龄段个数
            X = np.arange(len(NLD_B))
            bar_width = 0.25
            # 显示每个柱的具体高度
            for x, y in zip(X, NLD_B):
                plt.text(x + 0.005, y, '%.0f' % y, ha='center', va='bottom')
            for x, y1 in zip(X, NLD_G):
                plt.text(x + 0.24, y1, '%.0f' % y1, ha='center', va='bottom')
            # 绘制柱状图
            plt.bar(X, NLD_B, bar_width, align="center", color=['blue'], label="男性", alpha=0.5)
            plt.bar(X + bar_width, NLD_G, bar_width, align="center", color=['red'], label="女性", alpha=0.5)
            plt.ylabel('人数', fontsize=16)
            plt.xticks(fontsize=16)
            plt.yticks(fontsize=16)
            plt.title('住户年龄段和性别分布情况', fontproperties='SimHei', fontsize=20)
            plt.xticks(X + bar_width/2, NLlabels)
            plt.legend()
            plt.savefig('./static/images/社区画像结果/年龄段和性别分布情况画像.png', dpi=400, bbox_inches='tight')
            plt.close()

            # 绘制小区住户开门方式习惯情况 KMFS
            KMFSlabels = ['输密码', '刷脸', '刷门禁卡']
            KMFS = [passw, face, card]
            # 绘制横向柱状图
            b = plt.barh(KMFSlabels, KMFS, color=['gold', 'limegreen', 'hotpink'])
            for rect in b:
                w = rect.get_width()
                plt.text(w, rect.get_y() + rect.get_height() / 2, '%d' % int(w), ha='left', va='center', fontsize=15)
            plt.xlabel('访问次数', fontsize=17)
            plt.xticks(fontsize=16)
            plt.yticks(fontsize=17)
            plt.title('近28天住户开门方式统计', fontproperties='SimHei', fontsize=22)
            plt.savefig('./static/images/社区画像结果/开门方式情况画像.png', dpi=400, bbox_inches='tight')
            plt.close()

            # 绘制当地房价水平情况图 FJSP
            xqcs = city[3:]  # 提取城市名称，如桂林
            csjj = '全%s市均价'%xqcs  #全xx市均价
            city_price = int(SpiderCityHousePrice(city))  # 住户所在城市的二手房均价（元/㎡)
            community_price = int(SpiderCommunityHousePrice(xqmc)) # 住户所在小区的二手房均价（元/㎡)
            Pricelabels = [csjj, '小区楼盘均价']
            Pricedata = [city_price, community_price]
            bar_width = 0.6
            b = plt.barh(Pricelabels, Pricedata, bar_width, color=['dodgerblue', 'red'])
            for rect in b:
                w = rect.get_width()
                plt.text(w, rect.get_y() + rect.get_height() / 2, '%d' % int(w), ha='left', va='center', fontsize=15)
            plt.xlabel('元/平方', fontsize=17)
            plt.xticks(fontsize=16)
            plt.yticks(fontsize=17)
            plt.title('当地二手房房价水平对比', fontproperties='SimHei', fontsize=22)
            plt.savefig('./static/images/社区画像结果/当地房价水平对比情况画像.png', dpi=400, bbox_inches='tight')
            plt.close()
            return render_template('XqPortrait.html', GXSJ=GXSJ, xqmc=xqmc)


@app.route('/inquery/',methods=['GET','POST']) #用户画像查询
@is_login   #调用is_login装饰器，检测是否登录，必须是登录状态才能执行此操作
def inquery():
    if request.method == 'GET':
        return render_template('inquery.html')
    else:
        client_id = request.form.get('client_id')
        client = BasicProperty.query.filter(BasicProperty.yhid == client_id).first()
        if not client_id.isdigit():  #判断输入id是否纯数字
            flash('输入字符非法，请输入正确id号！')
            return render_template('inquery.html')
        elif client is None:        #判断输入id是否存在
            flash('对不起，本小区无该用户信息！')
            return render_template('inquery.html')
        else:
            # 用户基本属性
            # 用户性别sex（0表示女、1表示男）
            if client.sex == 0:
                sex = '女'
            else:
                sex = '男'
            # 年龄群体nlqt (0儿童7岁以下、1少年7-17、2青年18-40、3中年41-65、4老人65岁以上)
            if client.nlqt == 0:
                nlqt = '儿童'
            elif client.nlqt == 1:
                nlqt = '少年'
            elif client.nlqt == 2:
                nlqt = '青年'
            elif client.nlqt == 3:
                nlqt = '中年'
            else:
                nlqt = '老年'
            # 车辆信息clxx (0汽车、1货车、2摩托车、3电动车、4无车)
            if client.clxx == 0:
                clxx = '汽车'
            elif client.clxx == 1:
                clxx = '货车'
            elif client.clxx == 2:
                clxx = '摩托车'
            elif client.clxx == 3:
                clxx = '电动车'
            else:
                clxx = '无车'
            # 手机型号sjxh (0 Android、1 iOS、2 无)
            if client.sjxh == 0:
                sjxh = 'Android'
            elif client.sjxh == 1:
                sjxh = 'iOS'
            else:
                sjxh = '无'
            # 用户数据更新时间gxsj,处理为只显示日期date
            gxsj = client.gxsj.date()

            # 住房属性
            house = HouseProperty.query.filter(HouseProperty.yhid == client_id).first()
            # 房屋编号fwid、房屋单元fwdy、房屋门牌号fwh
            fwid = house.fwid
            fwdy = house.fwdy
            fwh = house.fwh
            # 统计户主、亲人、租客的个数,判断是否有租客
            huzhu = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.rygx == 0).count()
            qinren = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.rygx == 1).count()
            zuke = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.rygx == 2).count()
            num = huzhu + qinren
            # 用户和房屋户主关系rygx、房屋信息fwxx、家庭人员数量rysl
            if house.rygx == 0:
                rygx = '本人'
                fwxx = '购房'
                if zuke > 0:
                    rysl = '未知'
                else:
                    rysl = '%d' % num
            elif house.rygx == 1:
                rygx = '亲人'
                fwxx = '购房'
                rysl = '%d' % num
            else:
                rygx = '租客'
                fwxx = '租房'
                rysl = '%d' % zuke

            # 家庭类型预测 JTLX
            # 统计同一个fwid下不同性别不同年龄段的人数（女儿童、男儿童、女少年......男中年、男老年、女老年）
            ertongG = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 0,
                                                 HouseProperty.sex == 0).count()
            ertongB = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 0,
                                                 HouseProperty.sex == 1).count()
            shaonianG=HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 1,
                                                 HouseProperty.sex == 0).count()
            shaonianB=HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 1,
                                                 HouseProperty.sex == 1).count()
            qinnianG =HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 2,
                                                 HouseProperty.sex == 0).count()
            qinnianB =HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 2,
                                                 HouseProperty.sex == 1).count()
            zongnianG=HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 3,
                                                 HouseProperty.sex == 0).count()
            zongnianB=HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 3,
                                                 HouseProperty.sex == 1).count()
            laonianG =HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 4,
                                                 HouseProperty.sex == 0).count()
            laonianB =HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 4,
                                                 HouseProperty.sex == 1).count()
            # 定义变量并初始化
            child = 0
            qinnian = 0
            zongnian = 0
            laonian = 0
            # 统计年龄代数nlds，这里分为1-4代，儿童和少年同属于一代人
            if ertongB > 0 or ertongG > 0 or shaonianB > 0 or shaonianG > 0:
                child = 1
            if qinnianB > 0 or qinnianG > 0:
                qinnian = 1
            if zongnianB > 0 or zongnianG > 0:
                zongnian = 1
            if laonianB > 0 or laonianG > 0:
                laonian = 1
            nlds = child + qinnian + zongnian + laonian
            if house.rygx == 0:       #用户是户主
                if zuke > 0:
                    JTLX = '房东'  # 家庭类型不知，只可判断出这是房东
                else:
                    if nlds == 1:
                        if (qinnianB > 0 and qinnianG > 0) or (zongnianB > 0 and zongnianG > 0):
                            JTLX = '小家庭'
                        elif laonianB > 0 and laonianG > 0:
                            JTLX = '空巢家庭'
                        else:
                            JTLX = '独居人士'
                    elif nlds == 2:
                        JTLX = '核心家庭'
                    elif nlds == 3:
                        JTLX = '主干家庭'
                    else:
                        JTLX = '联合大家庭'
            elif house.rygx == 1:    #用户是户主亲人
                if nlds == 1:
                    if (qinnianB > 0 and qinnianG > 0) or (zongnianB > 0 and zongnianG > 0):
                        JTLX = '小家庭'
                    else:
                        JTLX = '空巢家庭'
                elif nlds == 2:
                    JTLX = '核心家庭'
                elif nlds == 3:
                    JTLX = '主干家庭'
                else:
                    JTLX = '联合大家庭'
            else:                    #用户是租客
                if nlds == 1:
                    if (qinnianB > 0 and qinnianG > 0) or (zongnianB > 0 and zongnianG > 0):
                        JTLX = '小家庭'
                    elif laonianB > 0 and laonianG > 0:
                        JTLX = '空巢家庭'
                    else:
                        JTLX = '独居人士'
                elif nlds == 2:
                    JTLX = '核心家庭'
                elif nlds == 3:
                    JTLX = '主干家庭'
                else:
                    JTLX = '联合大家庭'

            # 访问属性
            access = AccessProperty.query.filter(AccessProperty.yhid == client_id).first()
            if access is None:
                flash("无该用户近28天的访问记录！")
                lastin = '暂无'
                sbid = '暂无'
                sbjcd = '暂无'
                kmfsph = '暂无'
                fwtimes = '0'
                FWGL = '长期在外'
            else:
                # 用户最近一次访问时间lastin、进门检测站点sbjcd、门禁设备编号sbid
                lastintime = AccessProperty.query.filter(AccessProperty.yhid == client_id).order_by(
                    AccessProperty.kmsj.desc()).first()
                lastin = lastintime.kmsj
                sbjcd = lastintime.sbjcd
                sbid = lastintime.sbid
                # 用户开门方式偏好kmfsph
                passw = AccessProperty.query.filter(AccessProperty.yhid == client_id, AccessProperty.kmfs == 0).count()
                face = AccessProperty.query.filter(AccessProperty.yhid == client_id, AccessProperty.kmfs == 1).count()
                card = AccessProperty.query.filter(AccessProperty.yhid == client_id, AccessProperty.kmfs == 2).count()
                if passw > face and passw > card:
                    kmfsph = '输入密码'
                elif face > passw and face > card:
                    kmfsph = '刷脸'
                else:
                    kmfsph = '刷门禁卡'
                # 用户访问规律 FWGL
                ALLACCESS = AccessProperty.query.filter(AccessProperty.yhid == client_id).order_by(
                    AccessProperty.kmsj)
                fwsj = []
                for data in ALLACCESS:  # 将该用户的访问时间全部存入列表，格式是datetime.datetime(2020, 3, 13, 15, 52, 18)
                    fwsj.append(data.kmsj)
                # print(fwsj)

                fwtimes = AccessProperty.query.filter(AccessProperty.yhid == client_id).count()   #近28天访问次数
                if fwtimes > 45:
                    FWGL = '出入频繁'
                elif fwtimes > 5 and fwtimes < 10:
                    FWGL = '居家宅'
                elif  fwtimes <= 5:
                    FWGL = '经常不在家'
                else:
                    FWGL = '出入无规律'

            # 小区属性
            community = CommunityProperty.query.filter(CommunityProperty.xqid == house.xqid).first()
            xqid = community.xqid   #小区id（数字）
            xqmc = community.xqmc   #小区名称（中文）
            city = community.city   #小区所在省份-城市（中文），如广西-桂林
            # 调用自定义函数爬取房天下网站的二手房均价数据（元/㎡)
            city_house_price = SpiderCityHousePrice(city)             #爬取住户所在城市的二手房均价（元/㎡)
            community_house_price = SpiderCommunityHousePrice(xqmc)   #住户所在小区的二手房均价（元/㎡)
            HouseRatio = float(community_house_price) / float(city_house_price)  #评估所在小区房价在当地城市水平
            print(city_house_price)
            print(community_house_price)
            print(HouseRatio)

            # #将所在城市的平均房价和小区的平均房价保存到数据库的小区信息表里
            # community.city_houseprice = city_price
            # community.community_houseprice = community_price
            # db.session.commit()

            # 消费水平预测
            # XFYZ = (0.4×年龄群体二级标签NLD+0.3×房屋二级标签FW+0.2×车辆二级标签CL+0.1×手机二级标签SJ)
            # 年龄群体nlqt (0：儿童7岁以下、1：少年7-17、2：青年18-40、3：中年41-65、4：老人65岁以上)、年龄群体二级标签权重NLD
            if client.nlqt == 0:
                NLD = 0.1
            elif client.nlqt == 1:
                NLD = 0.3
            elif client.nlqt == 2:
                NLD = 0.9
            elif client.nlqt == 3:
                NLD = 0.7
            else:
                NLD = 0.4
            # 与户主关系rygx（0户主、1亲人、2租客）、房屋信息二级标签权重FW，三级标签权重HouseRatio
            # CommunityHousePrice = float(community.community_houseprice)
            # CityHousePrice = float(community.city_houseprice)
            # HouseRatio = CommunityHousePrice/CityHousePrice  #三级标签权重，评估所在小区房价在当地水平

            if house.rygx == 0:
                FW = 0.9 * HouseRatio
            elif house.rygx == 1:
                FW = 0.9 * HouseRatio
            else:
                FW = 0.4 * HouseRatio
            # 车辆信息clxx (0汽车、1货车、2摩托车、3电动车、4无) 、车辆类型二级标签权重CL
            if client.clxx == 0:
                CL = 0.9
            elif client.clxx == 1:
                CL = 0.8
            elif client.clxx == 2:
                CL = 0.5
            elif client.clxx == 3:
                CL = 0.4
            else:
                CL = 0.0
            # 手机型号sjxh (0 Android、1 iOS、2 无)、手机机型二级标签权重SJ
            if client.sjxh == 0:
                SJ = 0.5
            elif client.sjxh == 1:
                SJ = 0.9
            else:
                SJ = 0.0
            # 用户的消费指数
            XFZS = 0.4 * NLD + 0.3 * FW + 0.2 * CL + 0.1 * SJ
            XFZS = round(XFZS,2) #保留两位小数
            if XFZS >= 0.75:
                XFSP = '高消费水平'
            elif XFZS> 0.5 and XFZS < 0.75:
                XFSP = '中消费水平'
            else:
                XFSP = '低消费水平'

            #绘制用户画像词云图
            #根据本系统特点自定义以下属性标签，并根据重要性大小设定其出现次数的频次，以便词云图达到最佳显示效果，不然没有区分度。
            people = ['性别', '年龄群体', '家庭人数']
            access = ['访问时间', '访问次数', '开门方式偏好', '门禁设备', '进入单元', '出行特点', '月活跃度']
            consumption = ['资产情况', '车辆类型', '手机类型', '消费属性', '消费水平', '购买力']
            house = ['小区名称', '小区住户', '所在城市', '房屋单元', '门牌号', '人员关系', '房屋类型']
            system = ['社区', '门禁系统', '用户画像', '标签', '数据分析', '词云图', '可视化', 'Flask', 'Python', 'MySQL']
            #将以上标签写入txt文件，注意标签频次不一样(1-5次)
            with open("static/用户画像词云.txt", "w", encoding='utf-8') as f:
                for i in range(5):
                    for j in people:
                        f.write(j + ',')
                for i in range(4):
                    for j in access:
                        f.write(j + ',')
                for i in range(3):
                    for j in consumption:
                        f.write(j + ',')
                for i in range(2):
                    for j in house:
                        f.write(j + ',')
                for i in range(1):
                    for j in system:
                        f.write(j + ',')
            #将用户实时产生的部分标签追加到txt文件,更加个性化地展示用户画像，具有区分度。(标签频次是4-6次）
            SIX = [sex, nlqt, XFSP]
            FIVE = [fwxx, kmfsph, JTLX]
            FOUR = [clxx, sjxh, xqmc, city, fwdy, rygx]
            with open("static/用户画像词云.txt", "a", encoding='utf-8') as f:
                for i in range(6):
                    for j in SIX:
                        f.write(j + ',')
                for i in range(5):
                    for j in FIVE:
                        f.write(j + ',')
                for i in range(4):
                    for j in FOUR:
                        f.write(j + ',')
            #调用userWordCould.py文件里的WC()类，执行draw_wordcloud()函数得到词云画像
            wc = userWordCloud.WC()
            wc.draw_wordcloud()
            # flash("当前管理员：%s" % session['username'])
            # 将生成的用户标签传到网页
            return render_template('portrait.html', yhid=client.yhid, sex=sex, nlqt=nlqt, sjxh=sjxh, clxx=clxx,
                                   gxsj=gxsj, fwid=fwid, rygx=rygx, fwxx=fwxx, rysl=rysl, fwdy=fwdy, fwh=fwh,
                                   lastin=lastin, sbjcd=sbjcd, sbid=sbid, kmfsph=kmfsph, fwtimes=fwtimes,
                                   xqid=xqid, xqmc=xqmc, city=city, JTLX=JTLX, FWGL=FWGL, XFZS=XFZS, XFSP=XFSP)

@app.route('/inquery/portrait/',methods=['GET','POST']) #生成用户画像
@is_login
def portrait():
    if request.method == 'GET':
        return render_template('portrait.html')
    else:
        client_id = request.form.get('client_id')
        client = BasicProperty.query.filter(BasicProperty.yhid == client_id).first()
        if not client_id.isdigit():  # 判断输入id是否纯数字
            flash('输入字符非法，请输入正确id号！')
            return render_template('inquery.html')
        elif client is None:  # 判断输入id是否存在
            flash('对不起，本小区无该用户信息！')
            return render_template('inquery.html')
        else:
            # 用户基本属性
            # 用户性别sex（0表示女、1表示男）
            if client.sex == 0:
                sex = '女'
            else:
                sex = '男'
            # 年龄群体nlqt (0儿童7岁以下、1少年7-17、2青年18-40、3中年41-65、4老人65岁以上)
            if client.nlqt == 0:
                nlqt = '儿童'
            elif client.nlqt == 1:
                nlqt = '少年'
            elif client.nlqt == 2:
                nlqt = '青年'
            elif client.nlqt == 3:
                nlqt = '中年'
            else:
                nlqt = '老年'
            # 手机型号sjxh (0 Android、1 iOS、2 无)
            if client.sjxh == 0:
                sjxh = 'Android'
            elif client.sjxh == 1:
                sjxh = 'iOS'
            else:
                sjxh = '无'
            # 车辆信息clxx (0汽车、1货车、2摩托车、3电动车、4无车)
            if client.clxx == 0:
                clxx = '汽车'
            elif client.clxx == 1:
                clxx = '货车'
            elif client.clxx == 2:
                clxx = '摩托车'
            elif client.clxx == 3:
                clxx = '电动车'
            else:
                clxx = '无车'
            # 手机型号sjxh (0 Android、1 iOS、2 无)
            if client.sjxh == 0:
                sjxh = 'Android'
            elif client.sjxh == 1:
                sjxh = 'iOS'
            else:
                sjxh = '无'
            # 用户数据更新时间gxsj,处理为只显示日期date
            gxsj = client.gxsj.date()

            # 住房属性
            house = HouseProperty.query.filter(HouseProperty.yhid == client_id).first()
            # 房屋编号fwid、房屋单元fwdy、房屋门牌号fwh
            fwid = house.fwid
            fwdy = house.fwdy
            fwh = house.fwh
            # 统计户主、亲人、租客的个数,判断是否有租客
            huzhu = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.rygx == 0).count()
            qinren = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.rygx == 1).count()
            zuke = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.rygx == 2).count()
            num = huzhu + qinren
            # 用户和房屋户主关系rygx、房屋信息fwxx、家庭人员数量rysl
            if house.rygx == 0:
                rygx = '本人'
                fwxx = '购房'
                if zuke > 0:
                    rysl = '未知'
                else:
                    rysl = '%d' % num
            elif house.rygx == 1:
                rygx = '亲人'
                fwxx = '购房'
                rysl = '%d' % num
            else:
                rygx = '租客'
                fwxx = '租房'
                rysl = '%d' % zuke

            # 家庭类型预测 JTLX
            # 统计同一个fwid下不同性别不同年龄段的人数（女儿童、男儿童、女少年......男中年、男老年、女老年）
            ertongG = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 0,
                                                 HouseProperty.sex == 0).count()
            ertongB = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 0,
                                                 HouseProperty.sex == 1).count()
            shaonianG = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 1,
                                                   HouseProperty.sex == 0).count()
            shaonianB = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 1,
                                                   HouseProperty.sex == 1).count()
            qinnianG = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 2,
                                                  HouseProperty.sex == 0).count()
            qinnianB = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 2,
                                                  HouseProperty.sex == 1).count()
            zongnianG = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 3,
                                                   HouseProperty.sex == 0).count()
            zongnianB = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 3,
                                                   HouseProperty.sex == 1).count()
            laonianG = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 4,
                                                  HouseProperty.sex == 0).count()
            laonianB = HouseProperty.query.filter(HouseProperty.fwid == fwid, HouseProperty.nlqt == 4,
                                                  HouseProperty.sex == 1).count()
            # 定义变量并初始化
            child = 0
            qinnian = 0
            zongnian = 0
            laonian = 0
            # 统计年龄代数nlds，这里分为1-4代，儿童和少年同属于一代人
            if ertongB > 0 or ertongG > 0 or shaonianB > 0 or shaonianG > 0:
                child = 1
            if qinnianB > 0 or qinnianG > 0:
                qinnian = 1
            if zongnianB > 0 or zongnianG > 0:
                zongnian = 1
            if laonianB > 0 or laonianG > 0:
                laonian = 1
            nlds = child + qinnian + zongnian + laonian
            if house.rygx == 0:  # 用户是户主
                if zuke > 0:
                    JTLX = '房东'  # 家庭类型不知，只可判断出这是房东
                else:
                    if nlds == 1:
                        if (qinnianB > 0 and qinnianG > 0) or (zongnianB > 0 and zongnianG > 0):
                            JTLX = '小家庭'
                        elif laonianB > 0 and laonianG > 0:
                            JTLX = '空巢家庭'
                        else:
                            JTLX = '独居人士'
                    elif nlds == 2:
                        JTLX = '核心家庭'
                    elif nlds == 3:
                        JTLX = '主干家庭'
                    else:
                        JTLX = '联合大家庭'
            elif house.rygx == 1:  # 用户是户主亲人
                if nlds == 1:
                    if (qinnianB > 0 and qinnianG > 0) or (zongnianB > 0 and zongnianG > 0):
                        JTLX = '小家庭'
                    else:
                        JTLX = '空巢家庭'
                elif nlds == 2:
                    JTLX = '核心家庭'
                elif nlds == 3:
                    JTLX = '主干家庭'
                else:
                    JTLX = '联合大家庭'
            else:  # 用户是租客
                if nlds == 1:
                    if (qinnianB > 0 and qinnianG > 0) or (zongnianB > 0 and zongnianG > 0):
                        JTLX = '小家庭'
                    elif laonianB > 0 and laonianG > 0:
                        JTLX = '空巢家庭'
                    else:
                        JTLX = '独居人士'
                elif nlds == 2:
                    JTLX = '核心家庭'
                elif nlds == 3:
                    JTLX = '主干家庭'
                else:
                    JTLX = '联合大家庭'

            # 访问属性
            access = AccessProperty.query.filter(AccessProperty.yhid == client_id).first()
            if access is None:
                flash("无该用户近28天的访问记录！")
                lastin = '暂无'
                sbid = '暂无'
                sbjcd = '暂无'
                kmfsph = '暂无'
                fwtimes = '0'
                FWGL = '长期在外'
            else:
                # 用户最近一次访问时间lastin、进门检测站点sbjcd、门禁设备编号sbid
                lastintime = AccessProperty.query.filter(AccessProperty.yhid == client_id).order_by(
                    AccessProperty.kmsj.desc()).first()
                lastin = lastintime.kmsj
                sbjcd = lastintime.sbjcd
                sbid = lastintime.sbid
                # 用户开门方式偏好kmfsph
                passw = AccessProperty.query.filter(AccessProperty.yhid == client_id, AccessProperty.kmfs == 0).count()
                face = AccessProperty.query.filter(AccessProperty.yhid == client_id, AccessProperty.kmfs == 1).count()
                card = AccessProperty.query.filter(AccessProperty.yhid == client_id, AccessProperty.kmfs == 2).count()
                if passw > face and passw > card:
                    kmfsph = '输入密码'
                elif face > passw and face > card:
                    kmfsph = '刷脸'
                else:
                    kmfsph = '刷门禁卡'
                # 访问规律FWGL
                fwtimes = AccessProperty.query.filter(AccessProperty.yhid == client_id).count()  # 近28天访问次数
                if fwtimes > 45:
                    FWGL = '出入频繁'
                elif fwtimes > 5 and fwtimes < 10:
                    FWGL = '居家宅'
                elif fwtimes <= 5:
                    FWGL = '经常不在家'
                else:
                    FWGL = '出入无规律'

            # 小区属性
            community = CommunityProperty.query.filter(CommunityProperty.xqid == house.xqid).first()
            xqid = community.xqid
            xqmc = community.xqmc
            city = community.city
            city_house_price = SpiderCityHousePrice(city)  # 住户所在城市的二手房均价（元/㎡)
            community_house_price = SpiderCommunityHousePrice(xqmc)  # 住户所在小区的二手房均价（元/㎡)
            HouseRatio = float(community_house_price) / float(city_house_price)  # 评估所在小区房价在当地城市水平
            print(city_house_price)
            print(community_house_price)
            print(HouseRatio)

            # 消费水平预测
            # XFYZ = (0.4×年龄群体二级标签NLD+0.3×房屋二级标签FW+0.2×车辆二级标签CL+0.1×手机二级标签SJ)
            # 年龄群体nlqt (0：儿童7岁以下、1：少年7-17、2：青年18-40、3：中年41-65、4：老人65岁以上)、年龄群体二级标签权重NLD
            if client.nlqt == 0:
                NLD = 0.1
            elif client.nlqt == 1:
                NLD = 0.3
            elif client.nlqt == 2:
                NLD = 0.9
            elif client.nlqt == 3:
                NLD = 0.7
            else:
                NLD = 0.4
            # 与户主关系rygx（0户主、1亲人、2租客）、房屋信息二级标签权重FW，三级标签权重HouseRatio
            if house.rygx == 0:
                FW = 0.9 * HouseRatio
            elif house.rygx == 1:
                FW = 0.9 * HouseRatio
            else:
                FW = 0.4 * HouseRatio
            # 车辆信息clxx (0汽车、1货车、2摩托车、3电动车、4无) 、车辆类型二级标签权重CL
            if client.clxx == 0:
                CL = 0.9
            elif client.clxx == 1:
                CL = 0.8
            elif client.clxx == 2:
                CL = 0.5
            elif client.clxx == 3:
                CL = 0.4
            else:
                CL = 0.0
            # 手机型号sjxh (0 Android、1 iOS、2 无)、手机机型二级标签权重SJ
            if client.sjxh == 0:
                SJ = 0.5
            elif client.sjxh == 1:
                SJ = 0.9
            else:
                SJ = 0.0
            # 用户的消费指数
            XFZS = 0.4 * NLD + 0.3 * FW + 0.2 * CL + 0.1*SJ
            XFZS = round(XFZS, 2)  # 保留两位小数
            if XFZS >= 0.75:
                XFSP = '高消费水平'
            elif XFZS > 0.5 and XFZS < 0.75:
                XFSP = '中消费水平'
            else:
                XFSP = '低消费水平'

            # 绘制用户画像词云图
            people = ['性别', '年龄群体', '家庭人数']
            access = ['访问时间', '访问次数', '开门方式偏好', '门禁设备', '进入单元', '出行特点', '月活跃度']
            consumption = ['资产情况', '车辆类型', '手机类型', '消费属性', '消费水平', '购买力']
            house = ['小区名称', '小区住户', '所在城市', '房屋单元', '门牌号', '人员关系', '房屋类型']
            system = ['社区', '门禁系统', '用户画像', '标签', '数据分析', '词云图', '可视化', 'Flask', 'Python', 'MySQL']
            with open("static/用户画像词云.txt", "w", encoding='utf-8') as f:
                for i in range(5):
                    for j in people:
                        f.write(j + ',')
                for i in range(4):
                    for j in access:
                        f.write(j + ',')
                for i in range(3):
                    for j in consumption:
                        f.write(j + ',')
                for i in range(2):
                    for j in house:
                        f.write(j + ',')
                for i in range(1):
                    for j in system:
                        f.write(j + ',')
            SIX = [sex, nlqt, XFSP]
            FIVE = [fwxx, kmfsph, JTLX]
            FOUR = [clxx, sjxh, xqmc, city, fwdy, rygx]
            with open("static/用户画像词云.txt", "a", encoding='utf-8') as f:
                for i in range(6):
                    for j in SIX:
                        f.write(j + ',')
                for i in range(5):
                    for j in FIVE:
                        f.write(j + ',')
                for i in range(4):
                    for j in FOUR:
                        f.write(j + ',')
            wc = userWordCloud.WC()
            wc.draw_wordcloud()
            return render_template('portrait.html', yhid=client.yhid, sex=sex, nlqt=nlqt, sjxh=sjxh, clxx=clxx,
                                   gxsj=gxsj, fwid=fwid, rygx=rygx, fwxx=fwxx, rysl=rysl, fwdy=fwdy, fwh=fwh,
                                   lastin=lastin, sbjcd=sbjcd, sbid=sbid, kmfsph=kmfsph, fwtimes=fwtimes,
                                   xqid=xqid, xqmc=xqmc, city=city, JTLX=JTLX, FWGL=FWGL,  XFZS=XFZS, XFSP=XFSP)

# 启动服务器
# 如果当前这个文件是作为入口程序运行，那么就执行app.run()
if __name__ == '__main__':
    app.run(debug=True,host='127.0.0.1')