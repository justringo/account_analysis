# 股市板块轮动分析工具

这个工具可以实时监控股票市场中各行业板块的相对强弱，帮助投资者发现市场强势板块和个股，优化交易策略和择时。

## 主要功能

- **板块强弱分析**: 通过RSI等技术指标分析各板块的相对强弱
- **资金流向检测**: 分析主力资金流入流出情况
- **强势个股识别**: 从强势板块中筛选出高潜力个股
- **技术突破提醒**: 检测股票均线突破和成交量放大信号
- **市场趋势判断**: 分析大盘整体趋势方向和强度
- **综合报告生成**: 一键生成市场全面分析报告
- **钉钉通知**: 重要信号可通过钉钉机器人推送

## 技术特点

- 基于天勤量化(TqSdk)接口获取实时行情
- 使用技术指标(RSI、均线等)进行量化分析
- 多维度评分系统筛选强势板块和个股
- 支持定时分析和数据可视化

## 安装要求

```bash
pip install -r requirements.txt
```

## 使用方法

1. 配置天勤API账号:
```python
api = TqApi(auth=TqAuth("your_username", "your_password"))
```

2. 运行主程序:
```bash
python account_analysis.py
```

3. 参数设置:
- `TEST_MODE`: 测试模式，仅分析部分板块
- `ONE_TIME_ANALYSIS`: 是否只执行一次分析
- `ENABLE_DINGTALK`: 是否启用钉钉通知

## 数据结构

本工具包含以下主要数据:
- 18个主流行业板块，每个板块包含10只代表性股票
- 6个主要市场指数(上证/深证/创业板/科创50等)
- 每个板块包含详细的特征说明

## 注意事项

- 本工具仅供学习研究使用，不构成任何投资建议
- 使用前请确保已安装所有依赖包
- 钉钉通知功能需配置正确的机器人webhook

## 许可证

MIT
