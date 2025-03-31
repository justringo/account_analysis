#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件示例
用户可以复制该文件为 credentials.py 并填入自己的配置信息
"""

# 天勤量化API登录凭据
TQ_USERNAME = "your_username"  # 需要替换
TQ_PASSWORD = "your_password"  # 需要替换

# 钉钉机器人配置
DINGTALK_ENABLED = False  # 是否启用钉钉通知
DINGTALK_TOKEN = ""      # 钉钉机器人webhook token
DINGTALK_SECRET = ""     # 钉钉机器人加签密钥（可选）

# 程序运行配置
TEST_MODE = False        # 测试模式，仅分析部分板块
ONE_TIME_ANALYSIS = False  # 是否只执行一次分析
UPDATE_INTERVAL = 60     # 数据更新间隔（秒）
PLOT_INTERVAL = 300      # 图表绘制间隔（秒）
REPORT_INTERVAL = 1800   # 报告生成间隔（秒） 