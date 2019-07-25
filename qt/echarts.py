# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
import os
import re
import sys
import json
# from example import bar_example, line_example, graph_example, geo_example, map_example, pie_example
from math import sqrt

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QUrl, pyqtSlot, QObject
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow
from bson import ObjectId
from pyecharts.charts import Bar, WordCloud, Map, Line, Pie, Timeline, Geo, Graph
from pyecharts import options as opts
from pyecharts.globals import SymbolType, ChartType

sys.path.append(r'E:\Python\workspace\TDTSystem')

from mongo import MongoDB
from qt.city import china
from setting import *


class CallHandler(QObject):
    """
    JavaScript与python交互， JavaScripy信号传到python处理
    """

    def __init__(self, ui):
        super().__init__()
        self.ui = ui

    @pyqtSlot(str, result=str)
    def wordcloud_click(self, key):
        """
        Echarts wordcloud 点击关键词，点击信号传给python，根据关键词获取话题列表
        :param key:
        :return:
        """
        self.ui.getTopicByKey(key)

    @pyqtSlot(str, result=str)
    def map_click(self, area):
        """
        Echarts map 点击某地区，点击信号传给python，根据地区获取话题列表
        :param area:
        :return:
        """
        self.ui.getTopicByArea(area)


class Ui_Pyecharts(QWebEngineView):
    """
    QWebEngineView: qt部件，浏览器引擎，模拟浏览器
    Echarts 可视化工具， pyecharts为其python移植版
    pyecharts生成为html文件，缓存于buffer文件夹，
    QWebEngineView载入html文件实现可视化
    """
    webEngine = None
    webEngine2 = None

    @staticmethod
    def getEngine(parent):
        if Ui_Pyecharts.webEngine:
            print('WebEngine ready!')
            return Ui_Pyecharts.webEngine
        else:
            Ui_Pyecharts.webEngine = Ui_Pyecharts(parent)
            print('WebEngine init!')
            return Ui_Pyecharts.webEngine

    @staticmethod
    def getEngine2(parent):
        if Ui_Pyecharts.webEngine2:
            print('WebEngine ready!')
            return Ui_Pyecharts.webEngine2
        else:
            Ui_Pyecharts.webEngine2 = Ui_Pyecharts(parent)
            print('WebEngine init!')
            return Ui_Pyecharts.webEngine2

    def __init__(self, parent=None):
        """
        初始化
        :param parent: 调用浏览器引擎的父窗口
        """
        super().__init__(parent)
        self.superwindow = parent
        self.setupUi()
        self.client = MongoDB.get_client()
        self.db = MongoDB.get_client()[MONGO_DB]
        self.weibo = self.db['weibo']
        self.topic = self.db['topic']
        self.comment = self.db['comment']
        self.user = self.db['user']
        self.repost = self.db['repost']

        self.flag = None
        self.maparea = None
        self.maphtml = None
        self.barhtml = None
        self.wordcloudhtml = None
        self.graphtml = None
        self.geohtml = None
        self.id = None

    def setupUi(self):
        self.channel = QWebChannel()  # JavaScript与python交互通道
        self.handler = CallHandler(self)
        self.page().setWebChannel(self.channel)
        self.channel.registerObject('wordcloud', self.handler)  # 注册信号
        self.channel.registerObject('map', self.handler)
        QtCore.QMetaObject.connectSlotsByName(self)

    def bar(self):
        """
        柱状图，此处为获取话题总体热度时间曲线
        :return:
        """
        if self.barhtml:  # 是否存在缓存
            self.setHtml(self.barhtml)
            self.flag = 1
            return

        heat = {}
        # topicset = self.topic.find()
        # for topic in topicset:
        #     weibo_id_list = topic['text_id_list']
        #
        #     for weibo_id in weibo_id_list:
        #         weibo = self.weibo.find_one({'id': weibo_id})
        #         dateint = re.match(r'(\d+)-(\d+)-(\d+)', weibo['posted_at']).group()
        #         heat_score = weibo['comment_count'] + sqrt(weibo['forward_count'] + weibo['like_count'])
        #         if dateint not in heat:
        #             heat[dateint] = 0.0
        #         heat[dateint] += round(heat_score, 2)

        weiboset = self.weibo.find()
        for weibo in weiboset:
            dateint = re.match(r'(\d+)-(\d+)-(\d+)', weibo['posted_at']).group()
            heat_score = weibo['comment_count'] + sqrt(weibo['forward_count'] + weibo['like_count'])
            if dateint not in heat:
                heat[dateint] = 0.0
            heat[dateint] += round(heat_score, 2)

        heat = dict(sorted(heat.items(), key=lambda item: item[0], reverse=False))

        bar = (
            Bar()
                .add_xaxis([time for time in heat])
                .add_yaxis("热度", [value for value in heat.values()])
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=15)),
                title_opts=opts.TitleOpts(title="食品安全话题热度时间分布"),
                datazoom_opts=[opts.DataZoomOpts(type_="inside")],
            )
                .set_series_opts(
                label_opts=opts.LabelOpts(is_show=False),
            )
        )
        html = bar.render_embed()
        html = re.sub('width:\d+px', 'width:100%', html)
        self.setHtml(html)
        self.barhtml = html
        self.flag = 1

    def wordcloud(self):
        """
        词云，此处为话题总体关键词分布
        :return:
        """
        if self.wordcloudhtml:
            self.load(QUrl('file:///' + dirname + '/qt/buffer/wordcloud.html'))
            self.flag = 3
            return
        topicset = self.topic.find()
        keywords = {}
        for topic in topicset:
            for key, value in topic['keywords'].items():
                if key in keywords:
                    keywords[key] += value
                else:
                    keywords[key] = value
        keywords = dict(sorted(keywords.items(), key=lambda item: item[1], reverse=True))

        words = []
        count = 0
        for key, value in keywords.items():
            count += 1
            if count > 50:
                break
            words.append((key, value))

        wordcloud = (
            WordCloud()
                .add("", words, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
                .set_global_opts(title_opts=opts.TitleOpts(title="话题热词"))
        )
        html = wordcloud.render_embed()
        html_id = re.search('div id="(.*?)"', html).group(1)
        html = re.sub(r'width:\d+px', 'width:100%', html)
        js = '<script>chart_' + html_id + '''       
                    .on('click', function(params){
                        new QWebChannel(qt.webChannelTransport, function (channel) {
                            window.wordcloud = channel.objects.wordcloud
                            area = params.name
                            wordcloud.wordcloud_click(area);     
                        });
                    });</script>'''
        qwebchanneljs = '<script type="text/javascript" src="qwebchannel.js"></script>'
        html = re.sub('</head>', qwebchanneljs + '</head>', html)
        html = re.sub('</body>', js + '</body>', html)
        with open(dirname + '/qt/buffer/wordcloud.html', 'w') as f:
            f.write(html)
        self.wordcloudhtml = True
        self.load(QUrl('file:///' + dirname + '/qt/buffer/wordcloud.html'))
        self.flag = 3

    def get_province(self, str):
        """
        判断省份
        :param str:
        :return:
        """
        for province in china:
            if province in str or str in province:
                return province
            for city in china[province]:
                if city in str or str in city:
                    return province
        return None

    def get_city(self, str, province):
        """
        判断城市
        :param str: str, 待判断地名字符串
        :param province: str, 省份
        :return:
        """
        for city in china[province]:
            if city in str or str in city:
                return city
        return None

    def map(self, area=None):
        """
        话题地理分布
        :param area: 限制区域，默认为中国
        :return:
        """
        if self.maparea:
            if not area or self.maparea == area:
                self.load(QUrl('file:///' + dirname + '/qt/buffer/map.html'))
                self.flag = 4
                return
            if not area:
                area = 'china'

        self.maparea = area
        topicset = self.topic.find()
        temp = {}
        for topic in topicset:
            for item in topic['entity']['Ns']:
                if self.maparea == 'china':
                    city = self.get_province(''.join(item[0]))
                else:
                    city = self.get_city(''.join(item[0]), self.maparea)
                if city:
                    if city not in temp:
                        temp[city] = 0
                    temp[city] += item[1]
        data = []
        for key, value in temp.items():
            data.append([key, value])

        if self.maparea == 'china':
            temparea = '中国'
        else:
            temparea = self.maparea
        max_value = 100
        if temp.values():
            max_value = max(temp.values())
        map = (
            Map()
                .add("话题分布", data, self.maparea)
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts(title="话题分布-" + temparea),
                visualmap_opts=opts.VisualMapOpts(max_=max_value),
            )
        )
        html = map.render_embed()
        html_id = re.search('div id="(.*?)"', html).group(1)
        html = re.sub(r'width:\d+px', 'width:100%', html)

        # JavaScript代码注入，实现点击地图获取点击区域
        js = '''<script>
            new QWebChannel(qt.webChannelTransport, function (channel) {
                window.map = channel.objects.map;
            });       
            chart_html_id.on('click', function(params){      
                area = params.name;
                map.map_click(area);     
            });
            document.onclick = function(e){  
                ctx = e.target.getContext('2d')
                data = ctx.getImageData(e.pageX,e.pageY,1,1).data
                if (data[3] == 0) {
                    map.map_click('china')
                }
            }
            </script>'''
        qwebchanneljs = '<script type="text/javascript" src="qwebchannel.js"></script>'
        html = re.sub('</head>', qwebchanneljs + '</head>', html)
        html = re.sub('</body>', js + '</body>', html)
        html = re.sub('html_id', html_id, html)

        with open(dirname + '/qt/buffer/map.html', 'w') as f:
            f.write(html)
        self.load(QUrl('file:///' + dirname + '/qt/buffer/map.html'))
        self.flag = 4

    def geo(self, id=None):
        """
        话题地理传播路径
        :param id:
        :return:
        """
        if self.geohtml and (not id or self.id == id):
            self.load(QUrl('file:///' + dirname + '/qt/buffer/geo.html'))
            self.flag = 5
            return
        self.id = id

        provinces = {}
        links = []
        topic = self.topic.find_one({'_id': id})

        for weibo_id in topic['text_id_list']:
            if MONGO_DB == 'weibo':
                data = self.repost.find_one({'id': weibo_id})
                if not data:
                    continue
                uid = data['uid']
                dataset = self.repost.find({'uid': uid})
                for data in dataset:
                    if data['area']:
                        province = self.get_province(data['area'])
                        if province:
                            if province not in provinces:
                                provinces[province] = 0
                            provinces[province] += 1
                        break
            else:
                weibo = self.weibo.find_one({'id': weibo_id})
                user = self.user.find_one({'uid': weibo['uid']})
                if not user:
                    continue
                if user['area']:
                    # print(user['area'])
                    province = self.get_province(user['area'])
                    # print(province)
                    if province:
                        if province not in provinces:
                            provinces[province] = 0
                        provinces[province] += 1

        temp = None
        for province in provinces:
            if not temp:
                temp = province
                continue
            links.append((temp, province))
            temp = province
        # print(provinces)
        # print(links)

        c = (
            Geo()
                .add_schema(maptype="china")
                .add(
                "geo",
                [(key, value) for key, value in provinces.items()],
                type_=ChartType.EFFECT_SCATTER,
            )
                .add(
                "geo",
                links,
                type_=ChartType.LINES,
                effect_opts=opts.EffectOpts(
                    symbol=SymbolType.ARROW, symbol_size=6, color="blue"
                ),
                linestyle_opts=opts.LineStyleOpts(curve=0.2),
            )
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(),
                title_opts=opts.TitleOpts(title="话题地理传播路径图")
            )
        )
        html = c.render_embed()
        html = re.sub(r'width:\d+px', 'width:100%', html)
        html = re.sub(r'height:\d+px', 'height:800px', html)
        with open(dirname + '/qt/buffer/geo.html', 'w') as f:
            f.write(html)
        self.geohtml = True

        self.load(QUrl('file:///' + dirname + '/qt/buffer/geo.html'))
        self.flag = 5

    def bound(self, num):
        if num > 1000:
            num = 1000
        return ((num - 0) / 1000) * (100 - 5) + 5

    def graph(self, id=None):
        """
        话题微博转发（评论）关系图
        :param id: 话题id
        :return:
        """

        if id and str(id) + '_graph.html' in os.listdir(dirname + '/qt/buffer/graph/'):
            self.load(QUrl('file:///' + dirname + '/qt/buffer/graph/' + str(id) + '_graph.html'))
            self.id = id
            return

        if self.graphtml and (not id or self.id == id):
            self.load(QUrl('file:///' + dirname + '/qt/buffer/graph/' + str(self.id) + '_graph.html'))
            self.flag = 6
            return
        self.id = id
        nodes = []
        links = []
        category = []
        elements = ['username', 'content', 'posted_at', 'comment_count', 'forward_count', 'like_count']
        topic = self.topic.find_one({'_id': id})
        for id in topic['text_id_list']:
            weibo = self.weibo.find_one({'id': id})
            node = {}
            node['draggable'] = 'False'
            node['name'] = weibo['id']
            node['category'] = weibo['id']
            heat = weibo['comment_count'] + sqrt(weibo['forward_count'] + weibo['like_count'])
            node['value'] = heat
            node['symbolSize'] = self.bound(heat)
            for element in elements:
                node[element] = weibo[element]
            nodes.append(node)
            category.append({'name': weibo['id']})

        for item in category:
            if MONGO_DB == 'weibo':
                comments = self.comment.find({'id': item['name']})
            else:
                data = self.db['mid'].find_one({'id': item['name']})
                if not data:
                    continue
                comments = self.comment.find({'mid': data['mid']})
            for comment in comments:
                if not comment['is_v'] and not comment['is_vip']:
                    continue
                if re.search('@(.*):', comment['content']):
                    continue
                node = {}
                node['draggable'] = 'False'
                node['name'] = str(comment['_id'])
                node['category'] = item['name']
                node['value'] = 0.3 * comment['like_count']
                node['symbolSize'] = self.bound(0.3 * comment['like_count'])
                nodes.append(node)

                link = {'source': item['name'], 'target': str(comment['_id'])}
                for element in elements:
                    if element not in 'comment_count_forward_count':
                        link[element] = comment[element]
                links.append(link)

        # print(nodes)
        # print(links)
        # print(category)
        graph = (
            Graph()
                .add(
                "",
                nodes,
                links,
                category,
                repulsion=50,
                linestyle_opts=opts.LineStyleOpts(curve=0.2),
                label_opts=opts.LabelOpts(is_show=False),

            )
                .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=False),
                title_opts=opts.TitleOpts(title="微博转发关系图"),
            )
        )
        # JavaScript注入，实现鼠标移动到结点或边显示微博内容
        js = u'''
            <script>
            temp = document.createElement('div');
            temp.id = 'username';
            temp.style.cssText = 'divposition:absolute; width:100%; height:100px; top: 620px; left:10px;';
            temp.style.font = '15px Times New Roman'
            document.body.appendChild(temp);
            chart_html_id.on('mouseover', function(params) {
                username = params.data.username;
                content = params.data.content;
                if(username && content) {
                    temp.innerHTML = '<h2>' + username + ':</h2>';
                    temp.innerHTML += '<h1>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp' + content + '</h1>';
                    temp.innerHTML += '<h3>'
                    if(comment_count = params.data.comment_count)
                        temp.innerHTML += '评论数：' + comment_count + '&nbsp&nbsp'
                    if(forward_count = params.data.forward_count)
                        temp.innerHTML += '转发数：' + forward_count + '&nbsp&nbsp  '
                    temp.innerHTML += '点赞数：' + params.data.like_count + '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp';
                    temp.innerHTML += params.data.posted_at + '</h3>';
                }
            });
            chart_html_id.on('mouseout', function(params) {
                temp.innerHTML = '';
            });
        </script>
        '''
        html = graph.render_embed()
        html_id = re.search('div id="(.*?)"', html).group(1)
        html = re.sub(r'width:\d+px', 'width:100%', html)
        html = re.sub(r'height:\d+px', 'height:600px', html)
        html = re.sub('</body>', js + '</body>', html)
        html = re.sub('html_id', html_id, html)
        with open(dirname + '/qt/buffer/graph/' + str(self.id) + '_graph.html', 'w', encoding='utf-8') as f:
            f.write(html)
        self.load(QUrl('file:///' + dirname + '/qt/buffer/graph/' + str(self.id) + '_graph.html'))
        self.flag = 6
        self.graphtml = True

    def getTopicByKey(self, key):
        """
        通过关键词检索话题
        :param key:
        :return:
        """
        # print(key)
        self.superwindow.keys_update(key)

    def getTopicByArea(self, area):
        """
        # 通过地区检索话题
        :param area:
        :return:
        """
        # print(area)
        if area == self.maparea:
            return
        if area == 'china':
            self.map(area)
            self.superwindow.set_area('')
            return
        temp = None
        for province in china:
            if temp:
                break
            if area == province:
                temp = province
                break
            for city in china[province]:
                if area == city:
                    temp = province
                    break

        if temp:
            self.map(temp)
        self.superwindow.set_area(area)

    def resizeEvent(self, *args, **kwargs):
        if self.flag == 1:
            self.bar()
        elif self.flag == 2:
            self.pie()
        elif self.flag == 3:
            self.wordcloud()
        elif self.flag == 4:
            self.map()
        elif self.flag == 5:
            self.geo()
        elif self.flag == 6:
            self.graph()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainwindow = QMainWindow()
    mainwindow.resize(800, 900)
    centralwidget = QtWidgets.QWidget(mainwindow)
    verticalLayout = QtWidgets.QVBoxLayout(centralwidget)
    echarts = Ui_Pyecharts.getEngine(centralwidget)
    verticalLayout.addWidget(echarts)

    # echarts.wordcloud()
    # echarts.map('china')
    # echarts.bar('5cee1a286367791eacfeee57')
    # echarts.pie()
    # echarts.geo()
    # echarts.graph()
    mainwindow.setCentralWidget(centralwidget)
    mainwindow.show()
    sys.exit(app.exec_())
