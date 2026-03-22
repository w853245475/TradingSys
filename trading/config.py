import os

# Discord Webhook
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')

# 监控标的配置
A_SHARE_WATCHLIST = [
    '510300.SS', # 沪深300 ETF
    '510500.SS', # 中证500 ETF
    '513100.SS', # 纳指100 ETF (A股基金)
    '159915.SZ', # 创业板 ETF
]

US_SHARE_WATCHLIST = [
    'SPY',   # 标普500 ETF
    'QQQ',   # 纳斯达克100 ETF
    'AAPL',  # 苹果
    'NVDA',  # 英伟达
    'TSLA',  # 特斯拉
]

# 期权监控基础设定 - 监控最近到期且成交量异常的合约
OPTIONS_WATCHLIST = [
    'SPY', 
    'QQQ'
]
