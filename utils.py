#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import requests
import json
from datetime import datetime
import os

# 禁用代理设置，解决网络连接问题（可选）
def disable_proxy():
    """禁用代理设置，解决网络连接问题"""
    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''
    os.environ['http_proxy'] = ''
    os.environ['https_proxy'] = ''

def calculate_rsi(prices, period=14):
    """
    手动计算RSI指标
    :param prices: 价格序列
    :param period: RSI周期
    :return: RSI值
    """
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

def calculate_ma(prices, period):
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

def normalize_sectors_weights(sectors):
    """
    确保每个板块的股票权重总和为1
    :param sectors: 板块数据结构
    :return: 规范化后的板块
    """
    normalized_sectors = {}
    
    for sector_name, stocks in sectors.items():
        total_weight = sum(stock.get("weight", 0.1) for stock in stocks)
        
        if total_weight != 1.0:
            # 创建新列表以免修改原始数据
            normalized_stocks = []
            for stock in stocks:
                new_stock = stock.copy()
                if "weight" in new_stock:
                    new_stock["weight"] = new_stock["weight"] / total_weight
                else:
                    new_stock["weight"] = 0.1 / total_weight
                normalized_stocks.append(new_stock)
            normalized_sectors[sector_name] = normalized_stocks
        else:
            normalized_sectors[sector_name] = stocks
    
    return normalized_sectors

def send_to_dingtalk(content, webhook_token):
    """
    发送消息到钉钉
    :param content: 要发送的消息内容
    :param webhook_token: 钉钉webhook令牌
    :return: 是否发送成功
    """
    try:
        # 钉钉机器人的webhook地址
        webhook_url = f"https://oapi.dingtalk.com/robot/send?access_token={webhook_token}"
        
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

def get_current_time_str():
    """获取当前时间字符串，格式为YYYY-MM-DD HH:MM:SS"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_filename_timestamp():
    """获取用于文件名的时间戳，格式为YYYYMMDD_HHMMSS"""
    return datetime.now().strftime("%Y%m%d_%H%M%S") 