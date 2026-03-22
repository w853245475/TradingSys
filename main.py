import argparse
from trading.config import A_SHARE_WATCHLIST, US_SHARE_WATCHLIST
from trading.data_fetcher import fetch_historical_data
from trading.indicators import calculate_indicators, evaluate_signals
from trading.notifier import send_discord_alert
from trading.scanner import run_global_scan

def process_watchlist(category: str, watchlist: list):
    """处理并分析给定列表的证券"""
    print(f"开始处理 {category} 监控列表...")
    for ticker in watchlist:
        print(f"正在分析: {ticker}")
        df = fetch_historical_data(ticker)
        
        if df is None or len(df) < 50:
            continue
            
        df = calculate_indicators(df)
        signals = evaluate_signals(df)
        
        latest_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        data_info = {
            'price': float(latest_row['Close']),
            'prev_close': float(prev_row['Close']),
            'volume': float(latest_row['Volume'])
        }
        
        send_discord_alert(category, ticker, data_info, signals)
        
def main():
    parser = argparse.ArgumentParser(description="Multi-Market Trading Monitor & Scanner (ChatOps V2)")
    parser.add_argument('--mode', type=str, choices=['monitor', 'scan'], default='monitor',
                        help='选择运行模式: monitor (监控列表) 或 scan (全局扫描520战法)')
    parser.add_argument('--market', type=str, choices=['a-share', 'us-share', 'all'], required=True, 
                        help='选择要处理的市场: a-share, us-share 或 all')
    
    args = parser.parse_args()
    
    if args.mode == 'monitor':
        if args.market in ['a-share', 'all']:
            process_watchlist("A股/ETF", A_SHARE_WATCHLIST)
            
        if args.market in ['us-share', 'all']:
            process_watchlist("美股/ETF", US_SHARE_WATCHLIST)
            
    elif args.mode == 'scan':
        run_global_scan(args.market)

if __name__ == "__main__":
    main()
