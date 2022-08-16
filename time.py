# from flask import Flask,render_template,request,redirect,url_for,flash,session
# from datetime import date,time,datetime
# from Modelku import User,BasicProperty,HouseProperty,AccessProperty,CommunityProperty
# from exts import db
# from functools import wraps
# from collections import Counter
# import config
#
# app = Flask(__name__)          # 初始化一个Flask对象
# app.config.from_object(config) #从config.py文件导入配置参数  # 载入配置文件
# db.init_app(app)
#
# # xqcs = city[3:]   #提取城市名称，如桂林
# # xqcs_pinyin = Pinyin().get_pinyin(u"%s" % xqcs, '')   #先使用Pinyin（）函数将城市和小区的中文名称转为拼音
# # xqmc_pinyin = Pinyin().get_pinyin(u"%s" % xqmc, '')
# # city_url = "https://fangjia.fang.com/%s/"% xqcs_pinyin  #生成用户所在城市平均房价数据的url链接
# # community_url = "https://%s.fang.com/" % xqmc_pinyin   #生成住户所在小区平均房价数据的url链接
# # print(city_url)
# # print(community_url)
# # headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
# #                     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
# # def spider(url, headers):  #根据url爬取目标站点，返回源码
# #     try:
# #         response = requests.get(url, headers=headers)
# #         response.encoding = response.apparent_encoding  #自动判断字符集类型
# #         return response.text
# #     except:
# #         print('爬取站点失败，请检查url是否正确或连接是否可用！')
# # # 爬取房天下网站的房价数据，获取源码
# # city_html = spider(city_url, headers)
# # community_html = spider(community_url, headers)
# # # 从源码中定位到目标数据，即平均房价的数值
# # city_etree_html = etree.HTML(city_html)
# # city_price = city_etree_html.xpath('/html/body/div[3]/div[2]/dl/dd[1]/div/h3/text()')#得到一个列表，包含目标数据
# # community_etree_html = etree.HTML(community_html)
# # community_price = community_etree_html.xpath('//*[@id="body"]/div[5]/div[2]/div[2]/span[1]/text()')
# # # 将列表转换成为字符串
# # community_house_price = ''.join(community_price)
# # city_house_price = ''.join(city_price)
# # HouseRatio = float(community_house_price) / float(city_house_price)  #评估所在小区房价在当地城市水平
# # print(community_house_price)
# # print(city_house_price)
# # print(HouseRatio)


# # 绘制手机类型情况图 SJLX
# Phonelabels = ['无手机', 'iOS', 'Android']
# SJLX = [nophone, iOS, Android]
# b = plt.barh(Phonelabels, SJLX, color=['gold', 'limegreen', 'hotpink'])
# for rect in b:
#     w = rect.get_width()
#     plt.text(w, rect.get_y() + rect.get_height() / 2, '%d' % int(w), ha='left', va='center', fontsize=12)
# plt.xlim(0, 500)
# plt.xlabel('人数/台', fontsize=15)
# plt.xticks(fontsize=15)
# plt.yticks(fontsize=15)
# plt.title('住户拥有手机情况', fontproperties='SimHei', fontsize=18)
# plt.savefig('./static/images/社区画像结果/手机类型情况画像.png', dpi=400, bbox_inches='tight')
# plt.close()

# 手机型号sjxh (0 Android、1 iOS、2 无)
#             if client.sjxh == 0:
#                 sjxh = 'Android'
#             elif client.sjxh == 1:
#                 sjxh = 'iOS'
#             else:
#                 sjxh = '无'
# 手机型号sjxh (0 Android、1 iOS、2 无)、手机机型二级标签权重SJ
#             if client.sjxh == 0:
#                 SJ = 0.5
#             elif client.sjxh == 1:
#                 SJ = 0.9
#             else:
#                 SJ = 0.0

# if __name__ == '__main__':
#     app.run(debug=True)