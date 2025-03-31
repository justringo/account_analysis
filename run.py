#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股市板块轮动分析工具启动脚本
"""

import sys
import os
import time
from datetime import datetime

# 添加本地目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tqsdk import TqApi, TqAuth
    import utils
    from sector_data import display_sector_features, sectors
    from account_analysis import AdvancedSectorAnalysis
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖包: pip install -r requirements.txt")
    sys.exit(1)

# 导入配置
try:
    from credentials import (
        TQ_USERNAME, 
        TQ_PASSWORD, 
        DINGTALK_ENABLED, 
        DINGTALK_TOKEN,
        TEST_MODE,
        ONE_TIME_ANALYSIS,
        UPDATE_INTERVAL,
        PLOT_INTERVAL,
        REPORT_INTERVAL
    )
    has_credentials = True
except ImportError:
    print("未找到credentials.py配置文件，将使用默认配置")
    has_credentials = False
    
    # 默认配置
    TQ_USERNAME = "your_username"  # 需要替换
    TQ_PASSWORD = "your_password"  # 需要替换
    DINGTALK_ENABLED = False
    DINGTALK_TOKEN = ""
    TEST_MODE = False
    ONE_TIME_ANALYSIS = False
    UPDATE_INTERVAL = 60
    PLOT_INTERVAL = 300
    REPORT_INTERVAL = 1800

def main():
    """主函数"""
    print("\n" + "="*80)
    print("股市板块轮动分析程序 - 启动中")
    print("="*80)
    
    # 检查凭据
    if TQ_USERNAME == "your_username" or TQ_PASSWORD == "your_password":
        print("\n⚠️ 警告: 您需要设置自己的天勤账号密码")
        print("请复制sample_config.py为credentials.py，并填入您的账号信息")
        sys.exit(1)
    
    if DINGTALK_ENABLED:
        print("✓ 已启用钉钉通知功能，分析结果将发送至钉钉群")
    
    # 在测试模式下备份和修改sectors
    original_sectors = None
    if TEST_MODE:
        print("⚠️ 测试模式：仅分析两个板块")
        # 备份原始sectors数据
        original_sectors = sectors.copy()
        # 修改为只包含两个板块的版本
        sectors_temp = {
            "银行保险板块": original_sectors["银行保险板块"],
            "电子半导体板块": original_sectors["电子半导体板块"]
        }
        # 替换sectors为测试数据
        sectors = sectors_temp
    else:
        print("✓ 完整模式：分析所有板块")
    
    # 统计板块数量和股票数量
    total_sectors = len(sectors)
    total_stocks = sum(len(stocks) for stocks in sectors.values())
    print(f"✓ 加载了 {total_sectors} 个板块，共 {total_stocks} 只股票")
    
    api = None
    analyzer = None
    
    try:
        print("\n正在连接天勤API...")
        # 使用用户名密码登录
        api = TqApi(auth=TqAuth(TQ_USERNAME, TQ_PASSWORD))
        
        print("连接成功，正在初始化板块分析器...")
        # 创建板块分析器实例
        analyzer = AdvancedSectorAnalysis(auth=TqAuth(TQ_USERNAME, TQ_PASSWORD))
        
        print("\n初始化行情数据...")
        # 初始化行情数据
        analyzer.init_quotes()
        
        print("\n✓ 初始化完成！开始分析...")
        
        # 运行主分析循环
        if ONE_TIME_ANALYSIS:
            print("\n⚠️ 一次性分析模式：将只执行一次完整分析")
            
            # 执行一次性分析
            analyzer.update_stock_prices()
            analyzer.calculate_sector_indices()
            analyzer.calculate_sector_rsi()
            market_trend = analyzer.analyze_market_trend()
            analyzer.print_market_trend()
            analyzer.print_sector_rsi()
            fund_flow = analyzer.analyze_fund_flow()
            analyzer.print_fund_flow()
            
            # 打印强势板块及其强势股票
            strong_sectors = analyzer.get_strong_sectors_by_rsi(top_n=5)
            analyzer.print_strong_sectors_stocks(5, 3)
            
            # 识别突破均线的强势股票
            breakout_stocks = analyzer.identify_breakout_stocks()
            analyzer.print_breakout_stocks(10)
            
            # 生成综合报告
            analyzer.generate_comprehensive_report()
            
            # 检测强信号并通知
            if DINGTALK_ENABLED:
                analyzer.detect_strong_signals_and_notify(
                    market_trend=market_trend,
                    strong_sectors=strong_sectors,
                    breakout_stocks=breakout_stocks,
                    fund_flow=fund_flow
                )
            
            print("\n✓ 一次性分析完成，程序即将退出")
        else:
            print("\n✓ 连续监控模式：将持续分析市场")
            # 运行持续监控
            analyzer.run(
                update_interval=UPDATE_INTERVAL,
                plot_interval=PLOT_INTERVAL,
                report_interval=REPORT_INTERVAL
            )
        
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

if __name__ == "__main__":
    # 显示板块特征说明
    display_features = len(sys.argv) > 1 and sys.argv[1] == "--features"
    
    if display_features:
        display_sector_features()
    else:
        main() 