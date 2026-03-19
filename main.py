import argparse
from config import A_SHARE_WATCHLIST, US_SHARE_WATCHLIST
from data_fetcher import fetch_historical_data
from indicators import calculate_indicators, evaluate_signals
from notifier import send_discord_alert

def process_watchlist(category: str, watchlist: list):
    """处理并分析给定列表的证券"""
    print(f"开始处理 {category}...")
    for ticker in watchlist:
        print(f"正在分析: {ticker}")
        df = fetch_historical_data(ticker)
        
        if df is None or len(df) < 50:
            continue
            
        # 计算指标
        df = calculate_indicators(df)
        
        # 评估信号
        signals = evaluate_signals(df)
        
        # 获取最新价格和成交量
        latest_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        data_info = {
            'price': float(latest_row['Close']),
            'prev_close': float(prev_row['Close']),
            'volume': float(latest_row['Volume'])
        }
        
        # 始终发送播报，或者只有信号时才发送（可通过参数配置）
        # 目前先全盘播报并附带信号
        send_discord_alert(category, ticker, data_info, signals)
        
def main():
    parser = argparse.ArgumentParser(description="Multi-Market Trading Monitor")
    parser.add_argument('--market', type=str, choices=['a-share', 'us-share', 'all'], required=True, 
                        help='选择要监控的市场: a-share, us-share 或 all')
    
    args = parser.parse_args()
    
    if args.market in ['a-share', 'all']:
        process_watchlist("A股/ETF", A_SHARE_WATCHLIST)
        
    if args.market in ['us-share', 'all']:
        process_watchlist("美股/ETF", US_SHARE_WATCHLIST)

if __name__ == "__main__":
    main()
