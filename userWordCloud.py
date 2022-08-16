# -*- coding: utf-8 -*-
import jieba
from wordcloud import WordCloud
from imageio import imread
from flask import request
from Modelku import BasicProperty

class WC(object):
    def draw_wordcloud(self):
        client_id = request.form.get('client_id')  #获取用户id
        client = BasicProperty.query.filter(BasicProperty.yhid == client_id).first()
        file = open("static/用户画像词云.txt", "r", encoding="utf-8")
        text = file.read()
        file.close()
        comment_text = jieba.lcut(text)  #jieba分词
        cut_txt = " ".join(comment_text)
        if client.sex == 1:    # 判断用户性别（1表示男、0表示女）
            mask_img = imread("static/images/M_mask.png")  # 读取模板图片
        else:
            mask_img = imread("static/images/G_mask.png")
        cloud = WordCloud(
            width=1000, height=700, background_color="white", min_font_size=8, max_font_size=45,
            font_path="msyh.ttc", mask=mask_img, max_words=1000)
        word_cloud = cloud.generate(cut_txt)
        word_cloud.to_file("static/images/用户画像结果/用户%s的画像.png"%client.yhid)  #保存图片

# if __name__ == '__main__':
#     wc = WC()
#     wc.draw_wordcloud()
