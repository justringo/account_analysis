#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
# 禁用代理设置，解决网络连接问题
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

from tqsdk import TqApi, TqAuth
from tqsdk.ta import RSI  # 恢复导入tqsdk.ta中的RSI函数
# 也可以使用 from tqsdk.tafunc import 导入旧版技术指标函数
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from collections import defaultdict
import requests
import json
# import talib  # 移除talib导入，使用tqsdk.ta模块计算技术指标

# 技术指标计算说明：
# tqsdk提供了两种计算技术指标的方式：
# 1. tqsdk.ta - 新版接口，返回pandas.Series对象，使用方式类似talib
# 2. tqsdk.tafunc - 旧版接口，返回numpy数组，使用方式略有不同
# 本程序使用tqsdk.ta模块替代talib，无需安装额外的talib库

# 定义板块数据 - 更新板块信息
sectors = {
    "银行保险板块": [
        {"code": "SSE.601398", "name": "工商银行", "weight": 0.15},
        {"code": "SSE.601288", "name": "农业银行", "weight": 0.10},
        {"code": "SSE.601939", "name": "建设银行", "weight": 0.10},
        {"code": "SSE.601988", "name": "中国银行", "weight": 0.10},
        {"code": "SSE.600036", "name": "招商银行", "weight": 0.10},
        {"code": "SSE.600016", "name": "民生银行", "weight": 0.05},
        {"code": "SSE.601318", "name": "中国平安", "weight": 0.15},
        {"code": "SSE.601601", "name": "中国太保", "weight": 0.10},
        {"code": "SSE.601628", "name": "中国人寿", "weight": 0.10},
        {"code": "SSE.601336", "name": "新华保险", "weight": 0.05}
    ],
    
    "券商信托板块": [
        {"code": "SSE.600030", "name": "中信证券", "weight": 0.15},
        {"code": "SSE.600837", "name": "海通证券", "weight": 0.12},
        {"code": "SSE.601211", "name": "国泰君安", "weight": 0.12},
        {"code": "SSE.601688", "name": "华泰证券", "weight": 0.12},
        {"code": "SSE.600999", "name": "招商证券", "weight": 0.10},
        {"code": "SZSE.000776", "name": "广发证券", "weight": 0.10},
        {"code": "SSE.600109", "name": "国金证券", "weight": 0.08},
        {"code": "SSE.601788", "name": "光大证券", "weight": 0.08},
        {"code": "SZSE.002736", "name": "国信证券", "weight": 0.08},
        {"code": "SSE.600816", "name": "安信信托", "weight": 0.05}
    ],
    
    "房地产板块": [
        {"code": "SZSE.000002", "name": "万科A", "weight": 0.15},
        {"code": "SSE.600048", "name": "保利发展", "weight": 0.15},
        {"code": "SSE.600606", "name": "绿地控股", "weight": 0.10},
        {"code": "SSE.601668", "name": "中国建筑", "weight": 0.10},
        {"code": "SZSE.001979", "name": "招商蛇口", "weight": 0.10},
        {"code": "SSE.600340", "name": "华夏幸福", "weight": 0.08},
        {"code": "SSE.600383", "name": "金地集团", "weight": 0.08},
        {"code": "SZSE.000540", "name": "中天金融", "weight": 0.08},
        {"code": "SSE.600208", "name": "新湖中宝", "weight": 0.08},
        {"code": "SZSE.000069", "name": "华侨城A", "weight": 0.08}
    ],
    
    "有色金属板块": [
        {"code": "SSE.601600", "name": "中国铝业", "weight": 0.12},
        {"code": "SSE.601899", "name": "紫金矿业", "weight": 0.12},
        {"code": "SSE.603799", "name": "华友钴业", "weight": 0.12},
        {"code": "SZSE.002460", "name": "赣锋锂业", "weight": 0.12},
        {"code": "SSE.600547", "name": "山东黄金", "weight": 0.10},
        {"code": "SSE.600362", "name": "江西铜业", "weight": 0.10},
        {"code": "SZSE.000060", "name": "中金岭南", "weight": 0.08},
        {"code": "SSE.601958", "name": "金钼股份", "weight": 0.08},
        {"code": "SZSE.000878", "name": "云南铜业", "weight": 0.08},
        {"code": "SSE.600111", "name": "北方稀土", "weight": 0.08}
    ],
    
    "钢铁煤炭板块": [
        {"code": "SSE.600019", "name": "宝钢股份", "weight": 0.12},
        {"code": "SSE.601857", "name": "中国石油", "weight": 0.12},
        {"code": "SSE.600028", "name": "中国石化", "weight": 0.12},
        {"code": "SSE.601088", "name": "中国神华", "weight": 0.12},
        {"code": "SSE.601225", "name": "陕西煤业", "weight": 0.10},
        {"code": "SSE.600188", "name": "兖矿能源", "weight": 0.10},
        {"code": "SSE.600010", "name": "包钢股份", "weight": 0.08},
        {"code": "SSE.600808", "name": "马钢股份", "weight": 0.08},
        {"code": "SSE.600740", "name": "山西焦化", "weight": 0.08},
        {"code": "SSE.600395", "name": "盘江股份", "weight": 0.08}
    ],
    
    "化工板块": [
        {"code": "SSE.600309", "name": "万华化学", "weight": 0.15},
        {"code": "SSE.600346", "name": "恒力石化", "weight": 0.12},
        {"code": "SZSE.000830", "name": "鲁西化工", "weight": 0.10},
        {"code": "SSE.603260", "name": "合盛硅业", "weight": 0.10},
        {"code": "SSE.601216", "name": "君正集团", "weight": 0.10},
        {"code": "SSE.600143", "name": "金发科技", "weight": 0.10},
        {"code": "SZSE.000525", "name": "红太阳", "weight": 0.08},
        {"code": "SSE.600426", "name": "华鲁恒升", "weight": 0.10},
        {"code": "SZSE.000792", "name": "盐湖股份", "weight": 0.08},
        {"code": "SSE.603456", "name": "九洲药业", "weight": 0.07}
    ],
    
    "白酒食品板块": [
        {"code": "SSE.600519", "name": "贵州茅台", "weight": 0.20},
        {"code": "SZSE.000858", "name": "五粮液", "weight": 0.15},
        {"code": "SSE.600887", "name": "伊利股份", "weight": 0.10},
        {"code": "SSE.603288", "name": "海天味业", "weight": 0.10},
        {"code": "SSE.600809", "name": "山西汾酒", "weight": 0.10},
        {"code": "SZSE.000568", "name": "泸州老窖", "weight": 0.10},
        {"code": "SZSE.000596", "name": "古井贡酒", "weight": 0.07},
        {"code": "SZSE.002304", "name": "洋河股份", "weight": 0.08},
        {"code": "SZSE.002557", "name": "洽洽食品", "weight": 0.05},
        {"code": "SSE.600597", "name": "光明乳业", "weight": 0.05}
    ],
    
    "医药生物板块": [
        {"code": "SSE.600276", "name": "恒瑞医药", "weight": 0.15},
        {"code": "SZSE.000538", "name": "云南白药", "weight": 0.12},
        {"code": "SSE.600436", "name": "片仔癀", "weight": 0.12},
        {"code": "SSE.603259", "name": "药明康德", "weight": 0.12},
        {"code": "SSE.688180", "name": "君实生物", "weight": 0.10},
        {"code": "SZSE.300760", "name": "迈瑞医疗", "weight": 0.10},
        {"code": "SZSE.300015", "name": "爱尔眼科", "weight": 0.08},
        {"code": "SSE.603883", "name": "老百姓", "weight": 0.07},
        {"code": "SSE.600763", "name": "通策医疗", "weight": 0.07},
        {"code": "SZSE.300347", "name": "泰格医药", "weight": 0.07}
    ],
    
    "家电板块": [
        {"code": "SZSE.000651", "name": "格力电器", "weight": 0.15},
        {"code": "SZSE.000333", "name": "美的集团", "weight": 0.15},
        {"code": "SSE.600690", "name": "海尔智家", "weight": 0.12},
        {"code": "SZSE.002508", "name": "老板电器", "weight": 0.10},
        {"code": "SZSE.002032", "name": "苏泊尔", "weight": 0.10},
        {"code": "SZSE.000100", "name": "TCL科技", "weight": 0.10},
        {"code": "SZSE.002242", "name": "九阳股份", "weight": 0.08},
        {"code": "SSE.603868", "name": "飞科电器", "weight": 0.07},
        {"code": "SZSE.002677", "name": "浙江美大", "weight": 0.07},
        {"code": "SSE.600060", "name": "海信视像", "weight": 0.06}
    ],
    
    "电子半导体板块": [
        {"code": "SZSE.002415", "name": "海康威视", "weight": 0.15},
        {"code": "SZSE.300059", "name": "东方财富", "weight": 0.12},
        {"code": "SZSE.002371", "name": "北方华创", "weight": 0.12},
        {"code": "SSE.688981", "name": "中芯国际", "weight": 0.12},
        {"code": "SZSE.000725", "name": "京东方A", "weight": 0.10},
        {"code": "SZSE.002049", "name": "紫光国微", "weight": 0.10},
        {"code": "SSE.603501", "name": "韦尔股份", "weight": 0.08},
        {"code": "SSE.600584", "name": "长电科技", "weight": 0.07},
        {"code": "SSE.688012", "name": "中微公司", "weight": 0.07},
        {"code": "SZSE.300782", "name": "卓胜微", "weight": 0.07}
    ],
    
    "计算机软件板块": [
        {"code": "SZSE.002230", "name": "科大讯飞", "weight": 0.12},
        {"code": "SZSE.000977", "name": "浪潮信息", "weight": 0.12},
        {"code": "SSE.600845", "name": "宝信软件", "weight": 0.12},
        {"code": "SZSE.300454", "name": "深信服", "weight": 0.10},
        {"code": "SZSE.300033", "name": "同花顺", "weight": 0.10},
        {"code": "SZSE.002410", "name": "广联达", "weight": 0.10},
        {"code": "SSE.688111", "name": "金山办公", "weight": 0.10},
        {"code": "SZSE.300188", "name": "美亚柏科", "weight": 0.08},
        {"code": "SZSE.300496", "name": "中科创达", "weight": 0.08},
        {"code": "SZSE.300674", "name": "宇信科技", "weight": 0.08}
    ],
    
    "通信传媒板块": [
        {"code": "SZSE.000063", "name": "中兴通讯", "weight": 0.15},
        {"code": "SZSE.002027", "name": "分众传媒", "weight": 0.12},
        {"code": "SZSE.002558", "name": "巨人网络", "weight": 0.10},
        {"code": "SZSE.300413", "name": "芒果超媒", "weight": 0.10},
        {"code": "SSE.600637", "name": "东方明珠", "weight": 0.10},
        {"code": "SSE.601198", "name": "东兴证券", "weight": 0.10},
        {"code": "SSE.600050", "name": "中国联通", "weight": 0.10},
        {"code": "SZSE.000503", "name": "国新健康", "weight": 0.08},
        {"code": "SSE.603000", "name": "人民网", "weight": 0.08},
        {"code": "SSE.600804", "name": "鹏博士", "weight": 0.07}
    ],
    
    "新能源汽车板块": [
        {"code": "SZSE.300750", "name": "宁德时代", "weight": 0.18},
        {"code": "SZSE.002594", "name": "比亚迪", "weight": 0.15},
        {"code": "SSE.601127", "name": "小康股份", "weight": 0.10},
        {"code": "SZSE.002812", "name": "恩捷股份", "weight": 0.10},
        {"code": "SZSE.300014", "name": "亿纬锂能", "weight": 0.10},
        {"code": "SSE.601238", "name": "广汽集团", "weight": 0.10},
        {"code": "SSE.601633", "name": "长城汽车", "weight": 0.07},
        {"code": "SSE.603799", "name": "华友钴业", "weight": 0.07},
        {"code": "SSE.601689", "name": "拓普集团", "weight": 0.07},
        {"code": "SZSE.002074", "name": "国轩高科", "weight": 0.06}
    ],
    
    "光伏风电板块": [
        {"code": "SSE.601012", "name": "隆基绿能", "weight": 0.18},
        {"code": "SZSE.300274", "name": "阳光电源", "weight": 0.15},
        {"code": "SSE.600089", "name": "特变电工", "weight": 0.12},
        {"code": "SSE.603806", "name": "福斯特", "weight": 0.10},
        {"code": "SSE.600905", "name": "三峡能源", "weight": 0.10},
        {"code": "SZSE.002459", "name": "晶澳科技", "weight": 0.08},
        {"code": "SSE.688303", "name": "大全能源", "weight": 0.07},
        {"code": "SSE.603185", "name": "上机数控", "weight": 0.07},
        {"code": "SSE.600438", "name": "通威股份", "weight": 0.07},
        {"code": "SZSE.002202", "name": "金风科技", "weight": 0.06}
    ],
    
    "机械设备板块": [
        {"code": "SSE.600031", "name": "三一重工", "weight": 0.15},
        {"code": "SZSE.000157", "name": "中联重科", "weight": 0.12},
        {"code": "SZSE.000425", "name": "徐工机械", "weight": 0.12},
        {"code": "SSE.601766", "name": "中国中车", "weight": 0.12},
        {"code": "SSE.601100", "name": "恒立液压", "weight": 0.10},
        {"code": "SSE.603899", "name": "晨光股份", "weight": 0.08},
        {"code": "SSE.601877", "name": "正泰电器", "weight": 0.08},
        {"code": "SSE.601608", "name": "中信重工", "weight": 0.08},
        {"code": "SZSE.300124", "name": "汇川技术", "weight": 0.08},
        {"code": "SSE.688200", "name": "华峰测控", "weight": 0.07}
    ],
    
    "建筑建材板块": [
        {"code": "SSE.601668", "name": "中国建筑", "weight": 0.15},
        {"code": "SSE.601390", "name": "中国中铁", "weight": 0.12},
        {"code": "SSE.601186", "name": "中国铁建", "weight": 0.12},
        {"code": "SSE.600585", "name": "海螺水泥", "weight": 0.12},
        {"code": "SSE.600801", "name": "华新水泥", "weight": 0.10},
        {"code": "SSE.600720", "name": "祁连山", "weight": 0.08},
        {"code": "SZSE.000786", "name": "北新建材", "weight": 0.08},
        {"code": "SSE.600176", "name": "中国巨石", "weight": 0.08},
        {"code": "SSE.600516", "name": "方大炭素", "weight": 0.08},
        {"code": "SSE.600006", "name": "东风汽车", "weight": 0.07}
    ],
    
    "军工板块": [
        {"code": "SSE.600760", "name": "中航沈飞", "weight": 0.15},
        {"code": "SZSE.000768", "name": "中航西飞", "weight": 0.12},
        {"code": "SSE.600372", "name": "中航电子", "weight": 0.12},
        {"code": "SSE.600893", "name": "航发动力", "weight": 0.10},
        {"code": "SSE.600118", "name": "中国卫星", "weight": 0.10},
        {"code": "SZSE.002025", "name": "航天电器", "weight": 0.10},
        {"code": "SSE.600316", "name": "洪都航空", "weight": 0.08},
        {"code": "SSE.601989", "name": "中国重工", "weight": 0.08},
        {"code": "SSE.600038", "name": "中直股份", "weight": 0.08},
        {"code": "SSE.600879", "name": "航天电子", "weight": 0.07}
    ],
    
    "农林牧渔板块": [
        {"code": "SZSE.000876", "name": "新希望", "weight": 0.15},
        {"code": "SZSE.300498", "name": "温氏股份", "weight": 0.15},
        {"code": "SZSE.002714", "name": "牧原股份", "weight": 0.15},
        {"code": "SZSE.002157", "name": "正邦科技", "weight": 0.10},
        {"code": "SSE.600127", "name": "金健米业", "weight": 0.08},
        {"code": "SSE.600598", "name": "北大荒", "weight": 0.08},
        {"code": "SSE.600506", "name": "香梨股份", "weight": 0.07},
        {"code": "SSE.600371", "name": "万向德农", "weight": 0.07},
        {"code": "SZSE.300087", "name": "荃银高科", "weight": 0.08},
        {"code": "SZSE.300189", "name": "神农科技", "weight": 0.07}
    ],
    
    "商业贸易板块": [
        {"code": "SSE.601888", "name": "中国中免", "weight": 0.20},
        {"code": "SZSE.002024", "name": "苏宁易购", "weight": 0.12},
        {"code": "SSE.600655", "name": "豫园股份", "weight": 0.10},
        {"code": "SSE.600697", "name": "欧亚集团", "weight": 0.10},
        {"code": "SSE.600415", "name": "小商品城", "weight": 0.10},
        {"code": "SSE.600827", "name": "百联股份", "weight": 0.08},
        {"code": "SZSE.002251", "name": "步步高", "weight": 0.08},
        {"code": "SZSE.002419", "name": "天虹股份", "weight": 0.08},
        {"code": "SSE.600693", "name": "东百集团", "weight": 0.07},
        {"code": "SZSE.000759", "name": "中百集团", "weight": 0.07}
    ]
}

# 定义板块特征说明
sector_features = {
    "银行保险板块": "银行和保险企业，受宏观经济环境和货币政策影响大，经济上行期利率上升时表现较好。",
    "券商信托板块": "证券公司和信托企业，受市场交投活跃度和资本市场改革影响大，牛市行情时表现强势。",
    "房地产板块": "房地产开发和物业企业，受房地产政策和信贷环境影响显著，对利率变动敏感。",
    "有色金属板块": "有色金属开采、冶炼企业，受大宗商品价格影响大，周期性强，通胀预期上升时表现较好。",
    "钢铁煤炭板块": "钢铁、煤炭、石油等传统工业企业，强周期性，受宏观经济和供给侧改革影响明显。",
    "化工板块": "基础化学品和特种化学品企业，部分受油价影响，行业集中度提升利好龙头企业。",
    "白酒食品板块": "白酒、食品饮料企业，必需消费品，具有防御性，高端白酒具有奢侈品属性。",
    "医药生物板块": "医药研发、制造和医疗服务企业，长期成长性好，受政策影响大，创新药企业备受关注。",
    "家电板块": "家用电器制造企业，可选消费品，受地产后周期影响，品牌溢价能力强的企业更具竞争力。",
    "电子半导体板块": "半导体和电子元器件企业，科技创新前沿，国产替代空间大，高研发投入特点明显。",
    "计算机软件板块": "软件开发和IT服务企业，科技属性强，云计算、大数据、AI等新兴技术驱动成长。",
    "通信传媒板块": "通信设备、运营和传媒企业，5G建设是当前主线，传媒受政策和流量变化影响大。",
    "新能源汽车板块": "新能源汽车产业链企业，政策支持，高成长性，估值较高，技术迭代快。",
    "光伏风电板块": "太阳能、风能等可再生能源企业，全球绿色低碳转型受益，行业景气度高。",
    "机械设备板块": "工程机械和自动化设备企业，中游制造业，受固定资产投资影响较大。",
    "建筑建材板块": "基建、建材企业，受政府投资和房地产周期影响，政策敏感性高。",
    "军工板块": "国防军工企业，受益于国防现代化建设，政策导向明确，业绩确定性较高。",
    "农林牧渔板块": "农业和养殖企业，受自然灾害和疫情影响大，养殖板块具有较强周期性。",
    "商业贸易板块": "商业零售和贸易企业，消费相关性高，受居民消费能力和习惯变化影响，免税和线上零售是近期亮点。"
}

# 市场整体指数
market_indices = {
    "上证指数": "SSE.000001",
    "深证成指": "SZSE.399001",
    "创业板指": "SZSE.399006",
    "科创50": "SSE.588000",
    "中证500": "SSE.000905",
    "沪深300": "SSE.000300"
}

class AdvancedSectorAnalysis:
    def __init__(self, auth=None):
        """
        初始化高级板块分析器
        :param auth: TqAuth对象，用于API认证
        """
        self.api = TqApi(auth=auth)
        # 设置api的全局等待超时时间为1秒，防止在非交易时段长时间阻塞
        # self.api.set_wait_timeout(1)  # 在新版本TqSdk中此方法已不存在
        self.sector_quotes = {}  # 存储板块行情
        self.sector_indices = {}  # 存储板块指数
        self.sector_indices_history = defaultdict(list)  # 存储板块指数历史数据
        self.stock_quotes = {}  # 存储所有股票行情
        self.stock_prices = {}  # 存储所有股票当前价格
        self.stock_changes = {}  # 存储所有股票涨跌幅
        self.stock_volumes = {}  # 存储所有股票成交量
        self.stock_amounts = {}  # 存储所有股票成交额
        self.base_values = {}  # 存储各板块基准值
        self.market_indices_data = {}  # 存储市场指数数据
        self.timestamp_history = []  # 时间戳历史
        
        # 新增数据结构
        self.stock_price_history = defaultdict(list)  # 存储个股价格历史
        self.stock_volume_history = defaultdict(list)  # 存储个股成交量历史
        self.sector_rsi = {}  # 存储板块RSI值
        self.stock_rsi = {}  # 存储个股RSI值
        self.sector_fund_flow = {}  # 存储板块资金流向
        self.stock_fund_flow = {}  # 存储个股资金流向
        self.stock_ma_data = {}  # 存储均线数据
        self.market_trend = {}  # 存储大盘趋势判断
        
        # 从sectors中提取所有股票代码
        self.all_stocks = []
        for sector_name, stocks in sectors.items():
            for stock in stocks:
                if stock["code"] not in self.all_stocks:
                    self.all_stocks.append(stock["code"])
        
        # 添加市场指数
        for idx_name, idx_code in market_indices.items():
            self.all_stocks.append(idx_code)
    
    def init_quotes(self):
        """
        初始化所有股票和指数行情数据
        """
        print("正在订阅股票和指数行情...")
        try:
            # 使用get_quote_list批量获取股票行情，效率更高
            print(f"尝试获取 {len(self.all_stocks)} 只股票的行情数据...")
            quotes = self.api.get_quote_list(self.all_stocks)
            print(f"成功获取行情数据，正在处理...")
            
            # 将行情数据保存到字典中，方便后续查询
            for i, code in enumerate(self.all_stocks):
                self.stock_quotes[code] = quotes[i]
            
            print("行情数据处理完成，正在初始化板块基准值...")
            # 初始化各板块基准值（简单设为100）
            for sector_name in sectors.keys():
                self.base_values[sector_name] = 100
                self.sector_indices[sector_name] = 100  # 初始指数值为100
            
            print("板块基准值初始化完成，正在初始化市场指数数据...")
            # 初始化市场指数数据
            for idx_name, idx_code in market_indices.items():
                self.market_indices_data[idx_name] = {
                    "code": idx_code,
                    "price": self.stock_quotes[idx_code].last_price,
                    "change": 0
                }
            
            print("市场指数数据初始化完成，开始获取历史K线数据...")
            # 初始化历史K线数据，用于计算技术指标
            self.init_kline_history()
            
            print("所有初始化步骤完成！")
        except Exception as e:
            print(f"初始化行情数据时发生错误: {e}")
            raise  # 重新抛出异常，以便主程序可以捕获它
    
    def init_kline_history(self):
        """
        初始化历史K线数据，用于计算技术指标
        """
        total_stocks = len(self.all_stocks)
        print(f"开始获取{total_stocks}只股票的历史数据...")
        
        for idx, code in enumerate(self.all_stocks):
            try:
                # 打印进度
                progress = (idx + 1) / total_stocks * 100
                print(f"进度: {progress:.1f}% - 正在获取 {code} 的历史数据...", end="\r")
                
                # 获取日线数据，用于计算MA和RSI
                klines = self.api.get_kline_serial(code, 24*60*60, 100)  # 获取100个交易日数据
                if len(klines) > 0:
                    # 存储收盘价历史和K线数据
                    self.stock_price_history[code] = list(klines["close"])
                    # 存储成交量历史
                    self.stock_volume_history[code] = list(klines["volume"])
                    # 计算初始RSI
                    if len(klines) >= 14:  # RSI至少需要14个数据点
                        try:
                            # 使用tqsdk.ta.RSI函数计算RSI
                            rsi_result = RSI(klines, 14)
                            # 使用更安全的方式检查rsi_result是否有可用的值
                            if isinstance(rsi_result, pd.Series) and len(rsi_result) > 0:
                                rsi_value = float(rsi_result.iloc[-1])
                                if not np.isnan(rsi_value) and 0 <= rsi_value <= 100:
                                    self.stock_rsi[code] = rsi_value
                                else:
                                    # 使用手动计算
                                    self.stock_rsi[code] = self.calculate_rsi(self.stock_price_history[code], 14)
                            else:
                                self.stock_rsi[code] = 50  # 默认中性值
                        except Exception as e:
                            print(f"\n计算{code}的RSI出错: {e}")
                            # 尝试手动计算
                            self.stock_rsi[code] = self.calculate_rsi(self.stock_price_history[code], 14)
                    # 计算初始均线
                    self.stock_ma_data[code] = {
                        "MA20": self.calculate_ma(self.stock_price_history[code], 20),
                        "MA60": self.calculate_ma(self.stock_price_history[code], 60)
                    }
            except Exception as e:
                print(f"\n获取{code}历史数据失败: {e}")
        
        print("\n所有历史数据获取完成！")
        # 初始化板块RSI
        self.calculate_sector_rsi()
    
    def calculate_rsi(self, prices_or_klines, period=14):
        """
        计算RSI指标
        :param prices_or_klines: 价格序列或K线DataFrame
        :param period: RSI周期
        :return: RSI值
        """
        # 检查输入数据类型
        if isinstance(prices_or_klines, pd.DataFrame):
            # 输入是K线DataFrame，直接使用tqsdk.ta.RSI
            try:
                rsi_result = RSI(prices_or_klines, period)
                # 使用更安全的方式检查rsi_result是否有可用的值
                if isinstance(rsi_result, pd.Series) and len(rsi_result) > 0:
                    return float(rsi_result.iloc[-1])
                else:
                    return 50  # 默认中性值
            except Exception as e:
                print(f"使用tqsdk.ta计算RSI出错: {e}")
                # 出错时降级到手动计算
                if "close" in prices_or_klines.columns:
                    prices = list(prices_or_klines["close"])
                else:
                    return 50  # 没有close列，返回默认值
        else:
            # 输入是价格序列，使用手动计算
            prices = prices_or_klines
            
        # 手动计算RSI
        if len(prices) <= period:
            return 50  # 数据不足，返回中性值
            
        try:
            prices_array = np.array(prices, dtype=float)
            # 计算价格变化
            deltas = np.diff(prices_array)
            # 使用完整的deltas而不仅仅是前period+1个数据
            # 获取最近的period个数据来计算RSI
            seed = deltas[-period:]
            # 计算上涨和下跌的平均值
            up = seed[seed >= 0].sum() / period
            down = -seed[seed < 0].sum() / period
            # 防止除以零的更健壮处理方式
            if down == 0:
                # 如果没有下跌但有上涨，RSI应该很高但不一定是100
                if up > 0:
                    return 90  # 返回一个高但不是100的值
                else:
                    # 如果既没有上涨也没有下跌，说明价格没有变化
                    return 50  # 返回中性值
            # 计算相对强弱值
            rs = up / down
            # 计算RSI
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            print(f"手动计算RSI出错: {e}")
            return 50
    
    def calculate_sector_rsi(self):
        """
        计算各板块的RSI值
        """
        for sector_name, stocks in sectors.items():
            # 计算板块内所有股票的RSI平均值
            total_rsi = 0
            valid_count = 0
            for stock in stocks:
                code = stock["code"]
                if code in self.stock_rsi and not np.isnan(self.stock_rsi[code]):
                    total_rsi += self.stock_rsi[code]
                    valid_count += 1
            
            if valid_count > 0:
                self.sector_rsi[sector_name] = total_rsi / valid_count
            else:
                self.sector_rsi[sector_name] = 50  # 默认中性值
    
    def calculate_ma(self, prices, period):
        """
        计算移动平均线
        :param prices: 价格序列
        :param period: 周期
        :return: MA值
        """
        if len(prices) < period:
            return None
            
        try:
            # 使用numpy计算移动平均
            prices_array = np.array(prices, dtype=float)
            ma = np.mean(prices_array[-period:])
            return ma
        except Exception as e:
            print(f"计算MA出错: {e}")
            return None
    
    def analyze_fund_flow(self):
        """
        分析主力资金流入情况
        这里使用成交额变化作为资金流向的简化指标
        :return: 资金流向分析结果
        """
        # 计算个股资金流向
        for code in self.all_stocks:
            if len(self.stock_volume_history[code]) < 5:
                continue
                
            # 使用当日成交额与5日平均成交额比较作为资金流向指标
            current_amount = self.stock_amounts[code]
            if current_amount == 0:
                continue
                
            # 计算过去5日平均成交额
            avg_amount = 0
            valid_days = 0
            for i in range(1, min(6, len(self.stock_volume_history[code]))):
                idx = -i - 1  # 避开当天的数据
                if idx < -len(self.stock_volume_history[code]):
                    continue
                if self.stock_volume_history[code][idx] > 0:
                    # 简化处理，用成交量 * 当前均价作为历史成交额估计
                    avg_price = self.stock_prices[code]
                    historical_amount = self.stock_volume_history[code][idx] * avg_price
                    avg_amount += historical_amount
                    valid_days += 1
            
            if valid_days > 0:
                avg_amount /= valid_days
                # 计算资金流向比率
                flow_ratio = (current_amount - avg_amount) / avg_amount if avg_amount > 0 else 0
                self.stock_fund_flow[code] = flow_ratio * 100  # 转换为百分比
            else:
                self.stock_fund_flow[code] = 0
        
        # 计算板块资金流向
        fund_flow_results = {}
        for sector_name, stocks in sectors.items():
            # 加权计算板块资金流向
            weighted_flow = 0
            total_weight = 0
            
            # 用于记录板块内个股流向
            sector_stocks_flow = []
            
            for stock in stocks:
                code = stock["code"]
                weight = stock.get("weight", 0.1)
                if code in self.stock_fund_flow:
                    flow = self.stock_fund_flow[code]
                    weighted_flow += flow * weight
                    total_weight += weight
                    
                    # 添加个股流向数据
                    stock_flow = {
                        "code": code,
                        "name": stock["name"],
                        "flow": flow
                    }
                    sector_stocks_flow.append(stock_flow)
            
            if total_weight > 0:
                sector_flow = weighted_flow / total_weight
                self.sector_fund_flow[sector_name] = sector_flow
                
                # 计算资金流入评分(0-1)，用于强信号识别
                flow_score = 0.0
                if sector_flow > 50:  # 极强流入
                    flow_score = 0.9
                elif sector_flow > 30:  # 强势流入
                    flow_score = 0.8
                elif sector_flow > 20:  # 明显流入
                    flow_score = 0.7
                elif sector_flow > 10:  # 适度流入
                    flow_score = 0.6
                elif sector_flow > 5:   # 轻微流入
                    flow_score = 0.5
                elif sector_flow > 0:   # 极微流入
                    flow_score = 0.4
                
                # 判断资金流入的连续性
                continuous_flow = False
                if len(self.sector_indices_history[sector_name]) >= 3:
                    # 如果最近3天板块指数连续上涨，视为连续流入
                    if (len(self.sector_indices_history[sector_name]) >= 3 and 
                        self.sector_indices_history[sector_name][-1] > self.sector_indices_history[sector_name][-2] and 
                        self.sector_indices_history[sector_name][-2] > self.sector_indices_history[sector_name][-3]):
                        continuous_flow = True
                        flow_score += 0.1  # 连续流入加分
                
                # 保存该板块的资金流向分析结果
                fund_flow_results[sector_name] = {
                    "flow": sector_flow,
                    "flow_score": flow_score,
                    "continuous_flow": continuous_flow,
                    "stocks_flow": sorted(sector_stocks_flow, key=lambda x: x["flow"], reverse=True)[:5]  # 资金流入前5的股票
                }
            else:
                self.sector_fund_flow[sector_name] = 0
                fund_flow_results[sector_name] = {
                    "flow": 0,
                    "flow_score": 0,
                    "continuous_flow": False,
                    "stocks_flow": []
                }
        
        return fund_flow_results
    
    def analyze_market_trend(self):
        """
        分析大盘趋势
        结合主要指数涨跌、技术指标分析大盘趋势
        :return: 市场趋势分析结果
        """
        # 设置权重，上证指数和沪深300权重更高
        index_weights = {
            "上证指数": 0.3,
            "深证成指": 0.2,
            "创业板指": 0.15,
            "科创50": 0.15,
            "沪深300": 0.2
        }
        
        # 计算加权大盘涨跌幅
        weighted_change = 0
        total_weight = 0
        
        for idx_name, weight in index_weights.items():
            if idx_name in self.market_indices_data:
                change = self.market_indices_data[idx_name]["change"]
                if not np.isnan(change):
                    weighted_change += change * weight
                    total_weight += weight
        
        if total_weight > 0:
            avg_market_change = weighted_change / total_weight
        else:
            avg_market_change = 0
        
        # 分析上证指数RSI
        market_rsi = None
        if "上证指数" in self.market_indices_data:
            idx_code = self.market_indices_data["上证指数"]["code"]
            if idx_code in self.stock_rsi:
                market_rsi = self.stock_rsi[idx_code]
        
        # 判断趋势方向和强度
        trend_direction = ""
        trend_strength = 0.0
        
        # 根据涨跌幅和RSI综合判断大盘趋势
        if market_rsi is not None:
            if avg_market_change > 1.0 and market_rsi > 60:
                trend = "强势上涨"
                trend_direction = "up"
                # 趋势强度：根据涨幅和RSI组合计算
                trend_strength = min(1.0, (avg_market_change / 3.0) * 0.6 + (market_rsi / 100) * 0.4)
            elif avg_market_change > 0 and market_rsi > 50:
                trend = "温和上涨"
                trend_direction = "up"
                trend_strength = min(0.7, (avg_market_change / 2.0) * 0.6 + ((market_rsi - 50) / 50) * 0.4)
            elif avg_market_change < -1.0 and market_rsi < 40:
                trend = "明显下跌"
                trend_direction = "down"
                trend_strength = min(1.0, (abs(avg_market_change) / 3.0) * 0.6 + ((50 - market_rsi) / 50) * 0.4)
            elif avg_market_change < 0 and market_rsi < 50:
                trend = "温和下跌"
                trend_direction = "down"
                trend_strength = min(0.7, (abs(avg_market_change) / 2.0) * 0.6 + ((50 - market_rsi) / 50) * 0.4)
            else:
                trend = "横盘整理"
                trend_direction = "sideways"
                trend_strength = 0.3
        else:
            # 仅根据涨跌幅判断
            if avg_market_change > 1.0:
                trend = "上涨"
                trend_direction = "up"
                trend_strength = min(0.8, avg_market_change / 3.0)
            elif avg_market_change < -1.0:
                trend = "下跌"
                trend_direction = "down"
                trend_strength = min(0.8, abs(avg_market_change) / 3.0)
            else:
                trend = "横盘"
                trend_direction = "sideways"
                trend_strength = 0.2
        
        # 保存大盘趋势分析结果
        market_trend_result = {
            "trend": trend,
            "change": avg_market_change,
            "rsi": market_rsi,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength
        }
        
        self.market_trend = market_trend_result
        return market_trend_result
    
    def get_strong_sectors_by_rsi(self, top_n=5):
        """
        根据RSI获取强势板块
        :param top_n: 返回前n个强势板块
        :return: 强势板块列表，包含详细信息
        """
        # 按RSI值排序
        sorted_sectors = sorted(self.sector_rsi.items(), key=lambda x: x[1], reverse=True)
        
        # 选择RSI在50以上的强势板块
        strong_sectors_data = []
        for sector_name, rsi in sorted_sectors:
            if rsi > 50:
                # 获取该板块的资金流向
                fund_flow = self.sector_fund_flow.get(sector_name, 0)
                
                # 计算板块强度评分 (RSI贡献70%，资金流向贡献30%)
                strength_score = 0.0
                if rsi >= 75:  # 极强势
                    strength_score = 0.9
                elif rsi >= 65:  # 强势
                    strength_score = 0.8
                elif rsi >= 60:  # 中强
                    strength_score = 0.7
                elif rsi >= 55:  # 偏强
                    strength_score = 0.6
                else:  # 轻微强势
                    strength_score = 0.5
                
                # 资金流向对强度的贡献
                if fund_flow > 30:
                    strength_score += 0.1
                elif fund_flow < -20:
                    strength_score -= 0.1
                
                # 添加到强势板块列表
                strong_sectors_data.append({
                    "name": sector_name,
                    "rsi": rsi,
                    "fund_flow": fund_flow,
                    "strength_score": min(1.0, strength_score)
                })
        
        return strong_sectors_data[:top_n]
    
    def get_strong_stocks_by_sector(self, sector_name, top_n=3):
        """
        获取指定板块中的强势股票
        :param sector_name: 板块名称
        :param top_n: 返回前n只强势股票
        :return: 强势股票列表
        """
        if sector_name not in sectors:
            return []
            
        # 从该板块获取股票
        sector_stocks = sectors[sector_name]
        
        # 评分系统：结合RSI, 涨幅, 资金流向, 均线突破
        stock_scores = []
        
        for stock in sector_stocks:
            code = stock["code"]
            score = 0
            
            # RSI因子 (0-40分)
            if code in self.stock_rsi:
                rsi = self.stock_rsi[code]
                if not np.isnan(rsi):
                    if rsi > 70:
                        score += 40
                    elif rsi > 60:
                        score += 35
                    elif rsi > 50:
                        score += 25
                    else:
                        score += rsi / 2  # 低于50的RSI得分较低
            
            # 涨幅因子 (0-25分)
            if code in self.stock_changes:
                change = self.stock_changes[code]
                if not np.isnan(change):
                    if change > 5:
                        score += 25
                    elif change > 3:
                        score += 20
                    elif change > 1:
                        score += 15
                    elif change > 0:
                        score += 10
            
            # 资金流向因子 (0-20分)
            if code in self.stock_fund_flow:
                flow = self.stock_fund_flow[code]
                if not np.isnan(flow):
                    if flow > 50:
                        score += 20
                    elif flow > 30:
                        score += 15
                    elif flow > 10:
                        score += 10
                    elif flow > 0:
                        score += 5
            
            # 均线突破因子 (0-15分)
            if code in self.stock_ma_data and self.stock_ma_data[code]["MA20"] and self.stock_ma_data[code]["MA60"]:
                ma20 = self.stock_ma_data[code]["MA20"]
                ma60 = self.stock_ma_data[code]["MA60"]
                current_price = self.stock_prices.get(code, 0)
                
                if current_price > ma20 and current_price > ma60 and ma20 > ma60:
                    # 价格站上均线且短期均线上穿长期均线：强势上涨形态
                    score += 15
                elif current_price > ma20 and current_price > ma60:
                    # 价格站上所有均线：看涨
                    score += 12
                elif current_price > ma20:
                    # 价格站上短期均线：短期看涨
                    score += 8
                elif current_price < ma20 and current_price < ma60:
                    # 价格跌破所有均线：看跌
                    score -= 5
            
            # 成交量放大因子 (0-10分)
            if code in self.stock_volume_history and len(self.stock_volume_history[code]) >= 5:
                current_vol = self.stock_volume_history[code][-1]
                avg_vol = np.mean(self.stock_volume_history[code][-6:-1])  # 前5日平均
                if avg_vol > 0:
                    vol_ratio = current_vol / avg_vol
                    if vol_ratio > 2:
                        score += 10
                    elif vol_ratio > 1.5:
                        score += 7
                    elif vol_ratio > 1.2:
                        score += 5
                    elif vol_ratio > 1:
                        score += 3
            
            # 保存评分和股票信息
            stock_scores.append({
                "code": code,
                "name": stock["name"],
                "score": score,
                "rsi": self.stock_rsi.get(code, None),
                "change": self.stock_changes.get(code, None),
                "fund_flow": self.stock_fund_flow.get(code, None),
                "price": self.stock_prices.get(code, None),
                "volume": self.stock_volumes.get(code, None),
                "amount": self.stock_amounts.get(code, None)
            })
        
        # 按评分排序
        sorted_stocks = sorted(stock_scores, key=lambda x: x["score"], reverse=True)
        
        return sorted_stocks[:top_n]
    
    def identify_breakout_stocks(self):
        """
        识别突破20/60日均线且成交量放大的强势股票
        :return: 突破股票列表
        """
        breakout_stocks = []
        
        for code in self.all_stocks:
            if code not in self.stock_ma_data or code not in self.stock_volumes or code not in self.stock_volume_history:
                continue
                
            ma_data = self.stock_ma_data[code]
            if not ma_data["MA20"] or not ma_data["MA60"]:
                continue
                
            # 获取当前价格、移动平均线和成交量
            current_price = self.stock_prices.get(code, 0)
            ma20 = ma_data["MA20"]
            ma60 = ma_data["MA60"]
            current_vol = self.stock_volumes[code]
            
            # 判断是否站上均线
            above_ma20 = current_price > ma20
            above_ma60 = current_price > ma60
            
            # 计算价格突破幅度
            ma20_breakout_pct = (current_price / ma20 - 1) * 100 if ma20 > 0 else 0
            ma60_breakout_pct = (current_price / ma60 - 1) * 100 if ma60 > 0 else 0
            
            # 判断成交量是否放大 (与5日均量比较)
            vol_expansion = 0
            if len(self.stock_volume_history[code]) >= 5:
                avg_vol = sum(self.stock_volume_history[code][-6:-1]) / 5
                if avg_vol > 0:
                    vol_expansion = current_vol / avg_vol
            
            # 获取股票名称
            stock_name = "未知"
            for sector_name, stocks in sectors.items():
                for stock in stocks:
                    if stock["code"] == code:
                        stock_name = stock["name"]
                        break
                        
            # 计算突破强度评分(0-1)
            breakout_score = 0.0
            
            # 同时突破两条均线且成交量明显放大
            if above_ma20 and above_ma60 and vol_expansion >= 1.5:
                # 突破幅度贡献
                if ma60_breakout_pct >= 3:  # 强突破
                    breakout_score += 0.4
                elif ma60_breakout_pct >= 1.5:  # 中等突破
                    breakout_score += 0.3
                else:  # 轻微突破
                    breakout_score += 0.2
                
                # 成交量放大贡献
                if vol_expansion >= 3:  # 量能剧增
                    breakout_score += 0.4
                elif vol_expansion >= 2:  # 量能明显放大
                    breakout_score += 0.3
                else:  # 量能小幅放大
                    breakout_score += 0.2
                
                # 涨幅贡献
                change_pct = self.stock_changes.get(code, 0)
                if change_pct >= 5:  # 强势上涨
                    breakout_score += 0.2
                elif change_pct >= 2:  # 中等上涨
                    breakout_score += 0.1
                
                # 如果指数也处于上升趋势，加分
                if self.market_trend.get('trend_direction', '') == 'up':
                    breakout_score += 0.1
                
                # 突破均线且成交量放大，添加到结果
                breakout_stocks.append({
                    "code": code,
                    "name": stock_name,
                    "price": current_price,
                    "change": self.stock_changes.get(code, 0),
                    "above_ma20": above_ma20,
                    "above_ma60": above_ma60,
                    "ma20_breakout_pct": ma20_breakout_pct,
                    "ma60_breakout_pct": ma60_breakout_pct,
                    "vol_expansion": vol_expansion,
                    "breakout_score": breakout_score
                })
            # 单突破MA20但更强的放量和涨幅
            elif above_ma20 and vol_expansion >= 2.0 and self.stock_changes.get(code, 0) >= 3.0:
                # 简单的单MA突破也值得关注
                breakout_score = 0.5 + vol_expansion / 10
                
                # 突破均线且成交量放大，添加到结果
                breakout_stocks.append({
                    "code": code,
                    "name": stock_name,
                    "price": current_price,
                    "change": self.stock_changes.get(code, 0),
                    "above_ma20": above_ma20,
                    "above_ma60": above_ma60,
                    "ma20_breakout_pct": ma20_breakout_pct,
                    "ma60_breakout_pct": ma60_breakout_pct,
                    "vol_expansion": vol_expansion,
                    "breakout_score": breakout_score
                })
        
        # 按突破评分排序
        sorted_breakout_stocks = sorted(breakout_stocks, key=lambda x: x["breakout_score"], reverse=True)
        
        return sorted_breakout_stocks
    
    def calculate_sector_indices(self, method="weighted"):
        """
        计算各板块指数
        :param method: 计算方法，可选"equal"(等权重)或"weighted"(加权)
        """
        for sector_name, stocks in sectors.items():
            if method == "equal":
                # 等权重方法
                total_change = 0
                valid_stocks = 0
                
                for stock in stocks:
                    code = stock["code"]
                    if code in self.stock_changes and not np.isnan(self.stock_changes[code]):
                        total_change += self.stock_changes[code]
                        valid_stocks += 1
                
                # 计算平均涨跌幅
                if valid_stocks > 0:
                    avg_change = total_change / valid_stocks
                else:
                    avg_change = 0
                    
                # 根据涨跌幅更新板块指数
                self.sector_indices[sector_name] = self.base_values[sector_name] * (1 + avg_change / 100)
            
            else:  # weighted
                # 加权方法
                weighted_change = 0
                total_weight = 0
                
                for stock in stocks:
                    code = stock["code"]
                    weight = stock.get("weight", 0.1)  # 默认权重为0.1
                    
                    if code in self.stock_changes and not np.isnan(self.stock_changes[code]):
                        weighted_change += self.stock_changes[code] * weight
                        total_weight += weight
                
                # 计算加权平均涨跌幅
                if total_weight > 0:
                    avg_change = weighted_change / total_weight
                else:
                    avg_change = 0
                    
                # 根据涨跌幅更新板块指数
                self.sector_indices[sector_name] = self.base_values[sector_name] * (1 + avg_change / 100)
        
        # 记录历史数据
        self.timestamp_history.append(datetime.now())
        for sector_name, index_value in self.sector_indices.items():
            self.sector_indices_history[sector_name].append(index_value)
    
    def calculate_sector_momentum(self, periods=5):
        """
        计算板块动量指标
        :param periods: 用于计算动量的周期数
        :return: 按动量排序的板块列表
        """
        momentum = {}
        
        if len(self.timestamp_history) <= periods:
            return []  # 数据不足，无法计算动量
        
        for sector_name, history in self.sector_indices_history.items():
            if len(history) > periods:
                # 计算最近n个周期的变化率
                recent_change = (history[-1] - history[-periods-1]) / history[-periods-1] * 100
                momentum[sector_name] = recent_change
        
        # 按动量排序
        sorted_momentum = sorted(momentum.items(), key=lambda x: x[1], reverse=True)
        return sorted_momentum
    
    def identify_sector_trends(self):
        """
        识别板块趋势
        :return: 强势板块和弱势板块列表
        """
        if len(self.timestamp_history) < 10:
            return [], []  # 数据不足，无法识别趋势
        
        strong_sectors = []
        weak_sectors = []
        
        for sector_name, history in self.sector_indices_history.items():
            if len(history) >= 10:
                # 计算5日和10日变化率
                change_5d = (history[-1] - history[-6]) / history[-6] * 100 if len(history) >= 6 else 0
                change_10d = (history[-1] - history[-11]) / history[-11] * 100 if len(history) >= 11 else 0
                
                # 判断强势和弱势
                if change_5d > 0 and change_10d > 0 and change_5d > change_10d:
                    strong_sectors.append((sector_name, change_5d))
                elif change_5d < 0 and change_10d < 0 and change_5d < change_10d:
                    weak_sectors.append((sector_name, change_5d))
        
        # 排序
        strong_sectors = sorted(strong_sectors, key=lambda x: x[1], reverse=True)
        weak_sectors = sorted(weak_sectors, key=lambda x: x[1])
        
        return strong_sectors, weak_sectors
    
    def calculate_correlation_with_market(self):
        """
        计算各板块与大盘指数的相关性
        :return: 相关性数据
        """
        correlations = {}
        
        if len(self.timestamp_history) < 10:
            return {}  # 数据不足，无法计算相关性
        
        # 提取上证指数的变化历史
        sh_idx_code = market_indices["上证指数"]
        sh_idx_changes = []
        
        for i in range(1, len(self.timestamp_history)):
            if sh_idx_code in self.stock_prices:
                current_price = self.stock_prices[sh_idx_code]
                # 这里简化处理，实际应存储每个时间点的价格
                sh_idx_changes.append(self.stock_changes[sh_idx_code])
        
        # 计算各板块与大盘的相关性
        for sector_name, history in self.sector_indices_history.items():
            if len(history) >= 10:
                sector_changes = []
                for i in range(1, len(history)):
                    change = (history[i] - history[i-1]) / history[i-1] * 100
                    sector_changes.append(change)
                
                # 确保长度一致
                min_len = min(len(sector_changes), len(sh_idx_changes))
                if min_len > 5:  # 至少需要6个数据点
                    sector_changes = sector_changes[-min_len:]
                    sh_idx_changes_used = sh_idx_changes[-min_len:]
                    
                    # 计算相关系数
                    if len(set(sector_changes)) > 1 and len(set(sh_idx_changes_used)) > 1:
                        corr = np.corrcoef(sector_changes, sh_idx_changes_used)[0, 1]
                        correlations[sector_name] = corr
        
        return correlations
    
    def print_sector_performance(self):
        """
        打印各板块表现
        """
        print("\n" + "="*60)
        print(f"板块指数表现 (更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print("="*60)
        
        # 对板块按照表现排序
        sorted_sectors = sorted(self.sector_indices.items(), 
                               key=lambda x: x[1], 
                               reverse=True)
        
        for i, (sector_name, index_value) in enumerate(sorted_sectors):
            change = (index_value - self.base_values[sector_name]) / self.base_values[sector_name] * 100
            print(f"{i+1:2d}. {sector_name:<15} {index_value:>8.2f}  {change:>+6.2f}%")
    
    def print_market_indices(self):
        """
        打印市场指数行情
        """
        print("\n" + "="*60)
        print(f"大盘指数 (更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print("="*60)
        
        for idx_name, idx_data in self.market_indices_data.items():
            print(f"{idx_name:<10} {idx_data['price']:>8.2f}  {idx_data['change']:>+6.2f}%")
    
    def print_top_stocks(self, n=5):
        """
        打印每个板块内表现最好的n只股票
        """
        print("\n" + "="*70)
        print(f"各板块内表现最佳的{n}只股票")
        print("="*70)
        
        for sector_name, stocks in sectors.items():
            print(f"\n{sector_name}:")
            print("-"*70)
            
            # 获取该板块所有股票的涨跌幅
            sector_stocks_changes = []
            for stock in stocks:
                code = stock["code"]
                if code in self.stock_changes and not np.isnan(self.stock_changes[code]):
                    sector_stocks_changes.append((stock["name"], code, self.stock_changes[code], 
                                               self.stock_prices[code], self.stock_volumes[code], 
                                               self.stock_amounts[code]))
            
            # 对板块内股票按涨跌幅排序
            sorted_stocks = sorted(sector_stocks_changes, key=lambda x: x[2], reverse=True)
            
            # 打印前n只表现最好的股票
            for i, (name, code, change, price, volume, amount) in enumerate(sorted_stocks[:n]):
                # 计算成交额（万元）
                amount_wan = amount / 10000 if amount else 0
                print(f"{i+1:2d}. {name:<8} ({code:<10}) 价格:{price:>8.2f}  涨跌:{change:>+6.2f}%  成交:{amount_wan:>8.2f}万")
    
    def print_sector_momentum(self):
        """
        打印板块动量数据
        """
        momentum_data = self.calculate_sector_momentum()
        if not momentum_data:
            return
            
        print("\n" + "="*60)
        print(f"板块动量排名 (5周期)")
        print("="*60)
        
        for i, (sector_name, momentum) in enumerate(momentum_data[:10]):  # 只显示前10个
            print(f"{i+1:2d}. {sector_name:<15} 动量:{momentum:>+6.2f}%")
    
    def print_sector_trends(self):
        """
        打印板块趋势分析
        """
        strong_sectors, weak_sectors = self.identify_sector_trends()
        
        if strong_sectors:
            print("\n" + "="*60)
            print(f"强势板块 (趋势向上)")
            print("="*60)
            
            for i, (sector_name, change) in enumerate(strong_sectors[:5]):  # 只显示前5个
                print(f"{i+1:2d}. {sector_name:<15} 5日涨幅:{change:>+6.2f}%")
        
        if weak_sectors:
            print("\n" + "="*60)
            print(f"弱势板块 (趋势向下)")
            print("="*60)
            
            for i, (sector_name, change) in enumerate(weak_sectors[:5]):  # 只显示前5个
                print(f"{i+1:2d}. {sector_name:<15} 5日跌幅:{change:>+6.2f}%")
    
    def plot_sector_performance(self, top_n=5):
        """
        绘制板块表现图表
        :param top_n: 显示表现最好的前n个板块
        """
        if not plt:
            print("未安装matplotlib，无法绘制图表")
            return
            
        # 对板块按照表现排序
        sorted_sectors = sorted(self.sector_indices.items(), 
                               key=lambda x: (x[1] - self.base_values[x[0]]) / self.base_values[x[0]], 
                               reverse=True)
        
        # 选择表现最好的前N个板块
        top_sectors = sorted_sectors[:top_n]
        
        # 计算涨跌幅
        sector_names = []
        changes = []
        
        for sector_name, index_value in top_sectors:
            change = (index_value - self.base_values[sector_name]) / self.base_values[sector_name] * 100
            sector_names.append(sector_name)
            changes.append(change)
        
        # 绘制水平条形图
        plt.figure(figsize=(10, 6))
        bars = plt.barh(sector_names, changes, color=['#2E8B57' if x > 0 else '#D2042D' for x in changes])
        
        # 添加标签和标题
        plt.xlabel('涨跌幅 (%)')
        plt.title(f'表现最佳的{top_n}个板块 ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})')
        plt.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        # 在条形上添加数值标签
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width if width > 0 else width - 0.5
            plt.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.2f}%', 
                    va='center', ha='left' if width > 0 else 'right')
        
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(f'sector_performance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        print("\n已保存板块表现图表")
    
    def print_market_trend(self):
        """
        打印大盘趋势分析
        """
        print("\n" + "="*70)
        print(f"大盘趋势分析 (更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print("="*70)
        
        # 打印各指数情况
        print("主要指数走势:")
        for idx_name, idx_data in self.market_indices_data.items():
            print(f"{idx_name:<10}: {idx_data['price']:>8.2f}  涨跌:{idx_data['change']:>+6.2f}%")
        
        # 打印大盘趋势
        if self.market_trend:
            print(f"\n大盘综合趋势: {self.market_trend['trend']}")
            print(f"大盘加权涨跌: {self.market_trend['change']:>+6.2f}%")
            if self.market_trend['rsi'] is not None:
                print(f"大盘RSI值: {self.market_trend['rsi']:>6.2f}")
            
            # 分析趋势特征
            if self.market_trend['trend'] in ["强势上涨", "温和上涨"]:
                print("\n趋势特征: 大盘处于上升趋势，可积极寻找强势板块和个股进行布局")
            elif self.market_trend['trend'] in ["明显下跌", "温和下跌"]:
                print("\n趋势特征: 大盘处于下降趋势，建议控制仓位，防守为主，寻找逆势上涨的强势品种")
            else:
                print("\n趋势特征: 大盘处于横盘整理，可关注强势板块和个股的结构性机会")
    
    def print_sector_rsi(self):
        """
        打印板块RSI分析
        """
        print("\n" + "="*70)
        print(f"板块RSI相对强弱分析 (更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print("="*70)
        
        # 按RSI值排序
        sorted_sectors = sorted(self.sector_rsi.items(), key=lambda x: x[1], reverse=True)
        
        print(f"{'序号':<4}{'板块名称':<15}{'RSI值':<8}{'相对强弱':<10}{'资金流向':<10}")
        print("-"*50)
        
        for i, (sector_name, rsi) in enumerate(sorted_sectors):
            # 判断相对强弱
            if rsi > 70:
                strength = "超强"
            elif rsi > 60:
                strength = "强势"
            elif rsi > 50:
                strength = "偏强"
            elif rsi > 40:
                strength = "偏弱"
            elif rsi > 30:
                strength = "弱势"
            else:
                strength = "超弱"
                
            # 资金流向
            fund_flow = self.sector_fund_flow.get(sector_name, 0)
            if fund_flow > 30:
                flow_str = "大幅流入"
            elif fund_flow > 10:
                flow_str = "适度流入"
            elif fund_flow > 0:
                flow_str = "小幅流入"
            elif fund_flow > -10:
                flow_str = "小幅流出"
            elif fund_flow > -30:
                flow_str = "适度流出"
            else:
                flow_str = "大幅流出"
                
            print(f"{i+1:<4}{sector_name:<15}{rsi:<8.2f}{strength:<10}{flow_str:<10}")
        
        # 打印特征提示
        print("\n板块RSI解读:")
        print("- RSI > 70: 超强势，但可能面临短期回调风险")
        print("- RSI 60-70: 强势上涨，可能继续保持强势")
        print("- RSI 50-60: 偏强势，有上涨潜力")
        print("- RSI 40-50: 偏弱势，可能陷入震荡")
        print("- RSI 30-40: 弱势，可能继续下跌")
        print("- RSI < 30: 超弱势，但可能出现超跌反弹机会")
    
    def print_fund_flow(self):
        """
        打印资金流向分析
        """
        print("\n" + "="*70)
        print(f"板块资金流向分析 (更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print("="*70)
        
        # 按资金流向排序
        sorted_sectors = sorted(self.sector_fund_flow.items(), key=lambda x: x[1], reverse=True)
        
        print(f"{'序号':<4}{'板块名称':<15}{'资金流向':<10}{'流向幅度':<10}")
        print("-"*50)
        
        for i, (sector_name, flow) in enumerate(sorted_sectors):
            # 资金流向描述
            if flow > 30:
                flow_str = "大幅流入"
            elif flow > 10:
                flow_str = "适度流入"
            elif flow > 0:
                flow_str = "小幅流入"
            elif flow > -10:
                flow_str = "小幅流出"
            elif flow > -30:
                flow_str = "适度流出"
            else:
                flow_str = "大幅流出"
                
            print(f"{i+1:<4}{sector_name:<15}{flow_str:<10}{flow:>+10.2f}%")
        
        # 打印资金持续性分析
        print("\n资金持续性分析:")
        
        # 获取连续资金流入的板块
        continuous_inflow = []
        for sector_name, history in self.sector_indices_history.items():
            if len(history) >= 3 and sector_name in self.sector_fund_flow:
                if self.sector_fund_flow[sector_name] > 0:
                    # 简化判断连续性的方法：最近3天都是上涨的
                    if len(history) >= 3 and history[-1] > history[-2] and history[-2] > history[-3]:
                        continuous_inflow.append((sector_name, self.sector_fund_flow[sector_name]))
        
        # 显示连续资金流入的板块
        if continuous_inflow:
            print("\n连续资金流入的板块:")
            for sector_name, flow in sorted(continuous_inflow, key=lambda x: x[1], reverse=True):
                print(f"{sector_name:<15}: 资金流入 {flow:>+6.2f}%，呈现持续性流入特征")
        else:
            print("\n未发现明显的连续资金流入板块")
    
    def print_breakout_stocks(self, top_n=10):
        """
        打印突破均线且成交量放大的强势股票
        """
        breakout_stocks = self.identify_breakout_stocks()
        
        if not breakout_stocks:
            return
            
        print("\n" + "="*80)
        print(f"突破均线且成交量放大的强势股票 (Top {top_n})")
        print("="*80)
        
        print(f"{'序号':<4}{'股票名称':<8}{'代码':<12}{'所属板块':<12}{'价格':<8}{'涨跌幅':<8}{'成交量比':<8}{'MA20':<6}{'MA60':<6}{'RSI':<6}")
        print("-"*80)
        
        for i, stock in enumerate(breakout_stocks[:top_n]):
            ma20_status = "↑" if stock["above_ma20"] else "↓"
            ma60_status = "↑" if stock["above_ma60"] else "↓"
            vol_ratio = f"{stock['volume_ratio']:.2f}" if stock['volume_ratio'] is not None else "N/A"
            
            print(f"{i+1:<4}{stock['name']:<8}{stock['code']:<12}{stock['sector'][:12]:<12}{stock['price']:<8.2f}{stock['change']:>+8.2f}%{vol_ratio:<8}{ma20_status:<6}{ma60_status:<6}{stock['rsi']:<6.1f}")
        
        print("\n均线状态标识: ↑=站上均线  ↓=跌破均线")
    
    def print_strong_sectors_stocks(self, top_sectors=5, top_stocks=3):
        """
        打印强势板块及其强势股票
        """
        strong_sectors = self.get_strong_sectors_by_rsi(top_sectors)
        
        if not strong_sectors:
            return
            
        print("\n" + "="*80)
        print(f"强势板块(RSI)及其强势股票 (Top {top_sectors}板块, 每板块Top {top_stocks}股票)")
        print("="*80)
        
        for i, sector_data in enumerate(strong_sectors):
            print(f"\n{i+1}. {sector_data['name']} (板块RSI: {sector_data['rsi']:.2f}, 资金流向: {sector_data['fund_flow']:>+6.2f}%)")
            
            # 获取该板块的强势股票
            strong_stocks = self.get_strong_stocks_by_sector(sector_data['name'], top_stocks)
            
            if strong_stocks:
                print(f"{'股票名称':<8}{'代码':<12}{'价格':<8}{'涨跌幅':<8}{'RSI':<6}{'资金流向':<10}{'得分':<6}")
                print("-"*60)
                
                for stock in strong_stocks:
                    fund_flow = stock['fund_flow'] if stock['fund_flow'] is not None else 0
                    rsi = stock['rsi'] if stock['rsi'] is not None else 0
                    
                    print(f"{stock['name']:<8}{stock['code']:<12}{stock['price']:<8.2f}{stock['change']:>+8.2f}%{rsi:<6.1f}{fund_flow:>+10.2f}%{stock['score']:<6.1f}")
            else:
                print("  未找到符合条件的强势股票")
    
    def generate_comprehensive_report(self):
        """
        生成综合分析报告
        """
        print("\n" + "="*80)
        print(f"市场综合分析报告 (生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print("="*80)
        
        # 1. 大盘趋势分析
        trend = self.market_trend.get('trend', 'Unknown')
        print(f"\n【1. 大盘趋势】: {trend}")
        
        # 简单描述大盘趋势
        if trend in ["强势上涨", "温和上涨"]:
            print("大盘处于上升趋势，各主要指数普遍走强。")
        elif trend in ["明显下跌", "温和下跌"]:
            print("大盘处于下降趋势，各主要指数普遍走弱。")
        else:
            print("大盘处于横盘整理，各主要指数涨跌互现。")
        
        # 显示主要指数
        print("\n主要指数表现:")
        for idx_name in ["上证指数", "深证成指", "创业板指", "沪深300"]:
            if idx_name in self.market_indices_data:
                print(f"{idx_name}: {self.market_indices_data[idx_name]['price']:.2f}, 涨跌幅: {self.market_indices_data[idx_name]['change']:>+6.2f}%")
        
        # 2. 板块轮动分析
        print("\n【2. 板块轮动分析】")
        
        # 获取强势板块
        strong_sectors = self.get_strong_sectors_by_rsi(5)
        if strong_sectors:
            print("\n强势板块(RSI指标):")
            for i, sector_data in enumerate(strong_sectors):
                fund_flow = sector_data['fund_flow']
                print(f"{i+1}. {sector_data['name']}: RSI={sector_data['rsi']:.2f}, 资金流向={fund_flow:>+6.2f}%")
                
                # 显示板块特征
                if sector_data['name'] in sector_features:
                    print(f"   特征: {sector_features[sector_data['name']]}")
        
        # 资金持续流入的板块
        continuous_inflow = []
        for sector_name, flow in self.sector_fund_flow.items():
            if flow > 10:  # 显著流入
                continuous_inflow.append((sector_name, flow))
        
        if continuous_inflow:
            print("\n资金显著流入的板块:")
            for sector_name, flow in sorted(continuous_inflow, key=lambda x: x[1], reverse=True)[:3]:
                print(f"{sector_name}: 资金流入 {flow:>+6.2f}%")
        
        # 3. 强势个股分析
        print("\n【3. 强势个股分析】")
        
        # 从强势板块中选择强势个股
        if strong_sectors:
            top_sector_name = strong_sectors[0]['name']
            strong_stocks = self.get_strong_stocks_by_sector(top_sector_name, 3)
            
            if strong_stocks:
                print(f"\n最强势板块 [{top_sector_name}] 中的强势个股:")
                for i, stock in enumerate(strong_stocks):
                    print(f"{i+1}. {stock['name']}({stock['code']}): 价格={stock['price']:.2f}, 涨跌幅={stock['change']:.2f}%, RSI={stock['rsi']:.2f}")
        
        # 突破均线的强势股票
        breakout_stocks = self.identify_breakout_stocks()[:5]
        if breakout_stocks:
            print("\n突破均线且成交量放大的强势股票:")
            for i, stock in enumerate(breakout_stocks):
                ma_status = f"MA20{'↑' if stock['above_ma20'] else '↓'} MA60{'↑' if stock['above_ma60'] else '↓'}"
                print(f"{i+1}. {stock['name']}({stock['code']}): 价格={stock['price']:.2f}, 涨跌幅={stock['change']:>+6.2f}%, {ma_status}")
        
        # 4. 投资建议
        print("\n【4. 投资建议】")
        
        # 根据大盘趋势给出建议
        if trend in ["强势上涨", "温和上涨"]:
            print("• 大盘处于上升趋势，可积极布局强势板块和个股")
            if strong_sectors:
                print(f"• 重点关注 {strong_sectors[0]['name']} 和 {strong_sectors[1]['name'] if len(strong_sectors) > 1 else strong_sectors[0]['name']} 等强势板块")
            if breakout_stocks:
                print(f"• 可优先选择突破均线且成交量放大的个股，如 {breakout_stocks[0]['name']} 和 {breakout_stocks[1]['name'] if len(breakout_stocks) > 1 else breakout_stocks[0]['name']}")
        elif trend in ["明显下跌", "温和下跌"]:
            print("• 大盘处于下降趋势，建议控制仓位，以防守为主")
            print("• 可关注逆势走强的板块和个股")
            if continuous_inflow:
                print(f"• 可关注资金持续流入的 {continuous_inflow[0][0]} 板块")
        else:
            print("• 大盘处于横盘整理，建议精选个股，关注结构性机会")
            if strong_sectors:
                print(f"• 可关注相对强势的 {strong_sectors[0]['name']} 板块")
            if breakout_stocks:
                print(f"• 可关注突破技术形态的股票，如 {breakout_stocks[0]['name'] if breakout_stocks else ''}")
        
        # 5. 风险提示
        print("\n【5. 风险提示】")
        if any(sector_data['rsi'] > 75 for sector_data in strong_sectors[:2]):
            print("• 部分强势板块RSI处于高位，短期可能面临回调风险")
        if trend in ["强势上涨", "温和上涨"] and self.market_trend.get('rsi', 50) > 70:
            print("• 大盘RSI处于高位，短期可能面临回调风险")
        print("• 市场波动风险始终存在，建议根据自身风险承受能力进行投资")
        print("• 本报告仅供参考，不构成具体投资建议")
    
    def detect_strong_signals_and_notify(self, market_trend, strong_sectors, breakout_stocks, fund_flow):
        """
        检测强信号并通过钉钉通知
        只在发现明显的交易机会时才发送通知
        
        :param market_trend: 市场趋势分析结果
        :param strong_sectors: 强势板块列表
        :param breakout_stocks: 突破股票列表
        :param fund_flow: 资金流向分析结果 
        """
        strong_signals = []
        notification_needed = False
        
        # 1. 分析市场趋势强信号 - 提高判断标准
        if market_trend and 'trend_strength' in market_trend:
            trend_strength = market_trend['trend_strength']
            trend_direction = market_trend.get('trend_direction', '')
            
            # 只在趋势非常明显时才发出信号
            if trend_strength >= 0.8 and trend_direction == 'up':
                strong_signals.append(f"市场处于极强上升趋势 (强度: {trend_strength:.2f})")
                notification_needed = True
            elif trend_strength >= 0.8 and trend_direction == 'down':
                strong_signals.append(f"市场处于极强下降趋势 (强度: {trend_strength:.2f})")
                notification_needed = True
        
        # 2. 分析板块RSI强信号 - 增加更多维度的判断
        if strong_sectors:
            very_strong_sectors = []
            for sector in strong_sectors:
                # 同时考虑RSI和资金流向
                sector_fund_flow = fund_flow.get(sector['name'], {}).get('flow_score', 0)
                
                # 只有当RSI和资金流向都很强时才发出信号
                if sector['rsi'] >= 75 and sector_fund_flow >= 0.6:
                    very_strong_sectors.append(
                        f"{sector['name']} (RSI: {sector['rsi']:.1f}, 资金流入: {sector_fund_flow:.2f})"
                    )
                    notification_needed = True
                    
            if very_strong_sectors:
                strong_signals.append(f"极强势板块: {', '.join(very_strong_sectors)}")
                
                # 为每个强势板块添加其中的强势股票
                for sector in strong_sectors:
                    if sector['name'] in [vs.split(' ')[0] for vs in very_strong_sectors]:
                        strong_stocks = self.get_strong_stocks_by_sector(sector['name'], top_n=3)
                        if strong_stocks:
                            stock_details = [
                                f"{stock['name']}({stock['code'].split('.')[-1]}): "
                                f"涨幅{stock.get('change', 0):.2f}%" 
                                for stock in strong_stocks
                            ]
                            strong_signals.append(f"{sector['name']}强势股: {', '.join(stock_details)}")
        
        # 3. 分析突破股票强信号 - 增加突破确认
        if breakout_stocks:
            confirmed_breakouts = []
            for stock in breakout_stocks:
                # 只有当股票同时满足以下条件才认为是有效突破：
                # 1. 突破均线
                # 2. 成交量放大
                # 3. 股价创新高
                if (stock.get('volume_ratio', 0) > 2.0 and  # 成交量是平均水平的2倍以上
                    stock.get('price_strength', 0) > 0.7):  # 价格强度指标大于0.7
                    confirmed_breakouts.append(
                        f"{stock['name']}({stock['code'].split('.')[-1]}): "
                        f"量比{stock.get('volume_ratio', 0):.1f}"
                    )
            
            if len(confirmed_breakouts) >= 3:  # 至少要有3只股票同时突破才算是显著信号
                strong_signals.append(f"有效突破股票: {', '.join(confirmed_breakouts[:5])}")
                notification_needed = True
        
        # 4. 分析资金流向强信号 - 提高判断标准
        if fund_flow:
            strong_inflow_sectors = []
            
            # 检查是否有板块有明显的强资金流入
            for sector_name, flow_data in fund_flow.items():
                # 提高资金流入的判断标准，必须同时满足：
                # 1. 流入评分高
                # 2. 持续时间长
                # 3. 规模大
                if (flow_data.get('flow_score', 0) >= 0.8 and  # 提高到0.8
                    flow_data.get('duration', 0) >= 3 and      # 至少持续3个时间单位
                    flow_data.get('amount', 0) >= 100000000):  # 流入资金至少1亿
                    strong_inflow_sectors.append(
                        f"{sector_name} (流入: {flow_data.get('amount', 0)/100000000:.2f}亿, "
                        f"持续: {flow_data.get('duration', 0)}期)"
                    )
                    notification_needed = True
            
            if strong_inflow_sectors:
                strong_signals.append(f"大规模资金持续流入: {', '.join(strong_inflow_sectors)}")
        
        # 5. 只有在检测到强信号时才发送通知
        if notification_needed and strong_signals:
            # 生成更详细的通知内容
            notification_content = f"【股市轮动】强势机会提醒 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
            notification_content += "\n".join([f"• {signal}" for signal in strong_signals])
            
            # 添加关键市场指数数据
            notification_content += "\n\n【市场指数】"
            for idx_name, idx_data in self.market_indices_data.items():
                if idx_name in ["上证指数", "深证成指", "创业板指"]:  # 只显示主要指数
                    notification_content += f"\n{idx_name}: {idx_data['price']:.2f} ({idx_data['change']:+.2f}%)"
            
            # 调用发送钉钉消息的函数
            print("\n检测到强势机会，正在发送钉钉通知...")
            send_success = send_to_dingtalk(notification_content)
            
            if send_success:
                print("钉钉通知发送成功")
            else:
                print("钉钉通知发送失败")
        else:
            print("未检测到需要通知的强势机会")
    
    def run(self, update_interval=60, plot_interval=300, report_interval=1800):
        """
        运行板块分析
        :param update_interval: 数据更新间隔（秒），默认1分钟
        :param plot_interval: 图表绘制间隔（秒）
        :param report_interval: 综合报告生成间隔（秒）
        """
        try:
            print("开始初始化行情数据...")
            # 初始化行情
            self.init_quotes()
            
            print("行情初始化完成，进入主循环...")
            last_plot_time = datetime.now()
            last_update_time = datetime.now()
            last_report_time = datetime.now()
            last_data_update = time.time()
            
            print("等待第一次数据更新...")
            while True:
                try:
                    # 等待数据更新，此时会阻塞直到有新数据或超时
                    print("等待行情更新...", end="\r")
                    update_result = self.api.wait_update()
                    
                    # 如果有数据更新，立即记录时间
                    if update_result:
                        current_time = datetime.now()
                        time_since_update = (current_time - last_update_time).total_seconds()
                        
                        # 每分钟执行一次完整分析
                        if time_since_update >= update_interval:
                            print(f"\n\n{'-'*60}")
                            print(f"开始新一轮分析... (当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')})")
                            print(f"{'-'*60}")
                            
                            # 1. 更新基础数据
                            print("\n1. 更新基础数据...")
                            self.update_stock_prices()
                            self.calculate_sector_indices(method="weighted")
                            
                            # 2. 分析市场趋势
                            print("\n2. 分析市场趋势...")
                            market_trend = self.analyze_market_trend()
                            
                            # 3. 分析板块强弱
                            print("\n3. 分析板块强弱...")
                            self.calculate_sector_rsi()
                            strong_sectors = self.get_strong_sectors_by_rsi(top_n=5)
                            
                            # 4. 分析资金流向
                            print("\n4. 分析资金流向...")
                            fund_flow = self.analyze_fund_flow()
                            
                            # 5. 识别突破股票
                            print("\n5. 识别突破股票...")
                            breakout_stocks = self.identify_breakout_stocks()
                            
                            # 6. 检测强信号并通知（只在发现明显机会时通知）
                            print("\n6. 检测强势机会...")
                            self.detect_strong_signals_and_notify(
                                market_trend=market_trend,
                                strong_sectors=strong_sectors,
                                breakout_stocks=breakout_stocks,
                                fund_flow=fund_flow
                            )
                            
                            # 7. 定期绘制图表（每5分钟）
                            if (current_time - last_plot_time).total_seconds() >= plot_interval:
                                print("\n7. 更新分析图表...")
                                self.plot_sector_performance()
                                last_plot_time = current_time
                            
                            # 8. 定期生成综合报告（每30分钟）
                            if (current_time - last_report_time).total_seconds() >= report_interval:
                                print("\n8. 生成综合报告...")
                                self.generate_comprehensive_report()
                                last_report_time = current_time
                            
                            # 更新最后更新时间
                            last_update_time = current_time
                            print(f"\n分析完成，下次更新将在 {update_interval} 秒后进行...")
                            
                            # 显示非交易时段的提示
                            if time.time() - last_data_update > 60:
                                print("\n⚠️ 提示：当前可能处于非交易时段，数据更新频率可能较低")
                
                except Exception as e:
                    print(f"\n行情更新遇到问题: {e}")
                    time.sleep(5)  # 出错后等待5秒再继续
                
        except KeyboardInterrupt:
            print("\n程序已终止")
        except Exception as e:
            print(f"程序运行时发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n正在关闭API连接...")
            self.api.close()
    
    def update_stock_prices(self):
        """
        更新所有股票的最新价格和涨跌幅
        """
        # 使用get_quote_list批量获取最新行情，提高效率
        latest_quotes = self.api.get_quote_list(self.all_stocks)
        
        # 更新股票行情数据
        for i, code in enumerate(self.all_stocks):
            quote = latest_quotes[i]
            self.stock_quotes[code] = quote  # 更新行情对象
            
            # 获取最新价
            last_price = quote.last_price
            if np.isnan(last_price) or last_price == 0:
                last_price = quote.pre_close  # 如果还没有成交，使用昨收价
            
            # 计算涨跌幅
            if quote.pre_close and quote.pre_close > 0:
                change_percent = (last_price - quote.pre_close) / quote.pre_close * 100
            else:
                change_percent = 0
                
            self.stock_prices[code] = last_price
            self.stock_changes[code] = change_percent
            
            # 成交量和成交额
            self.stock_volumes[code] = quote.volume
            self.stock_amounts[code] = quote.amount
            
            # 更新价格历史和成交量历史
            if last_price > 0:
                self.stock_price_history[code].append(last_price)
                if len(self.stock_price_history[code]) > 100:  # 保持历史数据不超过100个点
                    self.stock_price_history[code].pop(0)
                    
            if quote.volume > 0:
                self.stock_volume_history[code].append(quote.volume)
                if len(self.stock_volume_history[code]) > 100:
                    self.stock_volume_history[code].pop(0)
            
            # 尝试获取最新K线数据来更新RSI值
            try:
                # 获取日线数据用于RSI计算
                klines = self.api.get_kline_serial(code, 24*60*60, 20)  # 获取近20个交易日数据即可
                if len(klines) >= 14:
                    try:
                        rsi_result = RSI(klines, 14)
                        # 检查rsi_result是否为Series对象，并且不为空
                        if isinstance(rsi_result, pd.Series) and len(rsi_result) > 0:
                            # 获取最后一个RSI值并检查其有效性
                            rsi_value = float(rsi_result.iloc[-1])
                            if not np.isnan(rsi_value) and 0 <= rsi_value <= 100:
                                self.stock_rsi[code] = rsi_value
                            else:
                                # 如果RSI值无效，使用手动计算
                                self.stock_rsi[code] = self.calculate_rsi(self.stock_price_history[code], 14)
                        else:
                            # 如果rsi_result不是预期的格式，使用手动计算
                            self.stock_rsi[code] = self.calculate_rsi(self.stock_price_history[code], 14)
                    except Exception as e:
                        print(f"处理{code}的RSI结果出错: {e}")
                        # 如果处理RSI结果失败，使用手动计算
                        self.stock_rsi[code] = self.calculate_rsi(self.stock_price_history[code], 14)
                else:
                    # 如果K线数据不足，使用价格序列计算
                    if len(self.stock_price_history[code]) >= 14:
                        self.stock_rsi[code] = self.calculate_rsi(self.stock_price_history[code], 14)
            except Exception as e:
                print(f"更新{code}的RSI出错: {e}")
                # 如果获取K线失败，尝试使用价格历史计算
                if len(self.stock_price_history[code]) >= 14:
                    self.stock_rsi[code] = self.calculate_rsi(self.stock_price_history[code], 14)
            
            # 更新均线数据
            if len(self.stock_price_history[code]) >= 60:
                self.stock_ma_data[code] = {
                    "MA20": self.calculate_ma(self.stock_price_history[code], 20),
                    "MA60": self.calculate_ma(self.stock_price_history[code], 60)
                }
        
        # 更新市场指数数据
        for idx_name, idx_data in self.market_indices_data.items():
            code = idx_data["code"]
            quote = self.stock_quotes[code]
            last_price = quote.last_price
            if np.isnan(last_price) or last_price == 0:
                last_price = quote.pre_close
                
            pre_close = quote.pre_close
            if pre_close and pre_close > 0:
                change = (last_price - pre_close) / pre_close * 100
            else:
                change = 0
                
            self.market_indices_data[idx_name]["price"] = last_price
            self.market_indices_data[idx_name]["change"] = change
            
        # 更新板块RSI值
        self.calculate_sector_rsi()
        
        # 分析资金流向
        self.analyze_fund_flow()
        
        # 分析大盘趋势
        self.analyze_market_trend()
    
    def normalize_sectors_weights():
        """
        确保每个板块的股票权重总和为1
        """
        for sector_name, stocks in sectors.items():
            total_weight = sum(stock.get("weight", 0.1) for stock in stocks)
            
            if total_weight != 1.0:
                # 归一化权重
                for stock in stocks:
                    if "weight" in stock:
                        stock["weight"] = stock["weight"] / total_weight
                    else:
                        stock["weight"] = 0.1 / total_weight

def display_sector_features():
    """
    显示各板块特征说明
    """
    print("\n" + "="*80)
    print("板块轮动特征说明")
    print("="*80)
    
    for sector_name, feature in sector_features.items():
        print(f"\n【{sector_name}】")
        print(f"{feature}")

# 定义钉钉发送函数
def send_to_dingtalk(content):
    """
    发送消息到钉钉
    :param content: 要发送的消息内容
    :return: 是否发送成功
    """
    try:
        # 钉钉机器人的webhook地址
        webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=fdb4b839ad94718e9f84308a9d699cf563d0ac724680c80d909a2dfc4865ac6c"
        
        # 确保内容包含关键词"股市轮动"以通过安全设置
        if "股市轮动" not in content:
            content = "【股市轮动】分析报告\n" + content
        
        # 构建消息数据
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        # 发送POST请求
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get("errcode") == 0:
                print("钉钉消息发送成功")
                return True
            else:
                print(f"钉钉消息发送失败: {result.get('errmsg')}")
                return False
        else:
            print(f"钉钉消息发送失败: HTTP状态码 {response.status_code}")
            return False
    except Exception as e:
        print(f"钉钉消息发送异常: {e}")
        return False

if __name__ == "__main__":  
    # 控制是否处于测试模式（只分析两个板块）
    TEST_MODE = False  # 设为False以分析所有板块
    # 控制是否只进行一次性分析
    ONE_TIME_ANALYSIS = False  # 设为False以启用循环分析
    # 控制是否启用钉钉通知
    ENABLE_DINGTALK = True
    
    print("\n" + "="*80)
    print("板块分析程序 - 实时监控模式")
    print("="*80)
    
    if ENABLE_DINGTALK:
        print("已启用钉钉通知功能，分析结果将发送至钉钉群")
    
    # 在测试模式下备份和修改sectors
    original_sectors = None
    if TEST_MODE:
        print("⚠️ 测试模式：仅分析两个板块")
        # 备份原始sectors数据
        original_sectors = sectors.copy()
        # 修改全局sectors为只包含两个板块的版本
        sectors_temp = {
            "银行保险板块": original_sectors["银行保险板块"],
            "电子半导体板块": original_sectors["电子半导体板块"]
        }
        # 替换sectors为测试数据
        sectors = sectors_temp
    else:
        print("完整模式：分析所有板块")
    
    # 统计板块数量和股票数量
    total_sectors = len(sectors)
    total_stocks = sum(len(stocks) for stocks in sectors.values())
    print(f"加载了 {total_sectors} 个板块，共 {total_stocks} 只股票")
    
    api = None
    analyzer = None
    
    try:
        # 使用用户名密码登录
        api = TqApi(auth=TqAuth("ringo", "Shinny456"))
        # 创建板块分析器实例
        analyzer = AdvancedSectorAnalysis(auth=TqAuth("ringo", "Shinny456"))
        
        # 循环执行分析
        last_analysis_time = 0
        interval = 60  # 1分钟 = 60秒，原来是300秒（5分钟）
        
        print("\n初始化行情数据...")
        analyzer.init_quotes()
        print("初始化完成！开始分析循环...\n")
        
        while True:
            current_time = time.time()
            # 判断是否需要执行分析
            if current_time - last_analysis_time >= interval or last_analysis_time == 0:
                print(f"\n{'-'*60}")
                print(f"开始新一轮分析... (当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                print(f"{'-'*60}")
                
                # 执行核心分析
                print("1. 更新股票价格...")
                analyzer.update_stock_prices()
                
                print("2. 计算板块指数...")
                analyzer.calculate_sector_indices()
                
                print("3. 计算板块RSI...")
                analyzer.calculate_sector_rsi()
                
                print("4. 分析市场趋势...")
                analyzer.analyze_market_trend()
                
                print("5. 识别强势板块...")
                strong_sectors = analyzer.get_strong_sectors_by_rsi(top_n=5)
                
                # 打印强势板块
                print("\n【强势板块】")
                for i, sector_data in enumerate(strong_sectors):
                    print(f"{i+1}. {sector_data['name']}: RSI={sector_data['rsi']:.2f}, 资金流向={sector_data['fund_flow']:>+6.2f}%")
                
                # 为最强板块找出强势股票
                if strong_sectors:
                    top_sector = strong_sectors[0]['name']
                    print(f"\n【{top_sector}】中的强势股票")
                    strong_stocks = analyzer.get_strong_stocks_by_sector(top_sector, top_n=3)
                    # 修复遍历方式，strong_stocks是字典列表而不是元组对
                    for i, stock in enumerate(strong_stocks, 1):
                        print(f"{i}. {stock['name']}({stock['code']}): 价格={stock['price']:.2f}, RSI={stock['rsi']:.2f}, 涨跌幅={stock['change']:.2f}%")
                
                # 打印市场趋势
                market_trend = analyzer.market_trend
                print(f"\n【市场趋势】: {market_trend['trend']}")
                print(f"市场RSI: {market_trend['rsi']:.2f}")
                print(f"平均涨跌幅: {market_trend['change']:.2f}%")
                
                # 打印主要指数
                print("\n【主要指数】")
                for idx_name, idx_data in analyzer.market_indices_data.items():
                    print(f"{idx_name}: {idx_data['price']:.2f}, 涨跌幅: {idx_data['change']:.2f}%")
                
                print(f"\n分析完成！下次更新时间: {datetime.fromtimestamp(current_time + interval).strftime('%H:%M:%S')}")
                
                # 构建钉钉消息内容
                dingtalk_msg = f"【股市轮动】分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                # 添加市场趋势
                dingtalk_msg += f"市场趋势: {market_trend['trend']}\n"
                dingtalk_msg += f"市场RSI: {market_trend['rsi']:.2f}\n"
                dingtalk_msg += f"平均涨跌幅: {market_trend['change']:.2f}%\n\n"
                
                # 添加强势板块
                dingtalk_msg += "【强势板块】\n"
                for i, sector_data in enumerate(strong_sectors[:3], 1):
                    dingtalk_msg += f"{i}. {sector_data['name']}: RSI={sector_data['rsi']:.2f}, 资金流向={sector_data['fund_flow']:>+6.2f}%\n"
                
                # 添加最强板块的强势股票
                if strong_sectors:
                    top_sector = strong_sectors[0]['name']
                    dingtalk_msg += f"\n【{top_sector}】中的强势股票\n"
                    strong_stocks = analyzer.get_strong_stocks_by_sector(top_sector, top_n=3)
                    for i, stock in enumerate(strong_stocks, 1):
                        dingtalk_msg += f"{i}. {stock['name']}({stock['code']}): 价格={stock['price']:.2f}, 涨跌幅={stock['change']:.2f}%\n"
                
                # 添加主要指数
                dingtalk_msg += "\n【主要指数】\n"
                for idx_name in ["上证指数", "深证成指", "创业板指", "沪深300"]:
                    if idx_name in analyzer.market_indices_data:
                        idx_data = analyzer.market_indices_data[idx_name]
                        dingtalk_msg += f"{idx_name}: {idx_data['price']:.2f}, 涨跌幅: {idx_data['change']:.2f}%\n"
                
                # 发送钉钉消息
                if ENABLE_DINGTALK:
                    send_to_dingtalk(dingtalk_msg)
                
                # 更新最后分析时间
                last_analysis_time = current_time
                
                # 如果是一次性分析模式，执行完一次就退出循环
                if ONE_TIME_ANALYSIS:
                    print("\n一次性分析模式已完成，程序即将退出...")
                    break
                
            # 短暂休眠，避免CPU占用过高
            # time.sleep(1)  # 移除这行，使用wait_update代替
            # 使用wait_update等待行情更新，避免使用time.sleep阻塞事件循环
            try:
                api.wait_update(deadline=time.time() + 1)  # 最多等待1秒
            except Exception as e:
                print(f"等待行情更新时出错: {e}", end="\r")
                
    except KeyboardInterrupt:
        print("\n\n检测到用户中断，正在安全退出程序...")
    except Exception as e:
        import traceback
        print(f"\n程序发生错误: {e}")
        print(traceback.format_exc())
    finally:
        # 如果是测试模式，恢复原始sectors数据
        if TEST_MODE and original_sectors:
            sectors = original_sectors
        
        print("\n正在关闭连接...")
        # 确保API资源被正确释放
        if api:
            try:
                # 首先关闭分析器持有的API
                if analyzer and hasattr(analyzer, 'api') and analyzer.api:
                    try:
                        analyzer.api.close()
                        print("已关闭分析器API连接")
                    except Exception as e:
                        print(f"关闭分析器API连接时发生错误: {e}")
                
                # 然后关闭主API连接
                api.close()
                print("已关闭主API连接")
            except Exception as e:
                print(f"关闭API连接时发生错误: {e}")
            
        print("程序已安全退出")