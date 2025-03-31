#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
板块股票数据和特征说明
包含18个主要板块及其成分股，以及板块特征描述
"""

# 定义板块数据 - 主要行业板块及其成分股
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

if __name__ == "__main__":
    # 显示所有板块特征说明
    display_sector_features() 