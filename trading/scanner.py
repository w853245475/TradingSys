import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tabulate import tabulate
from datetime import datetime

from data_fetcher import get_ashare_universe, get_us_universe, fetch_ashare_hist, fetch_historical_data, fetch_options_activity
from indicators import calculate_indicators, check_520_strategy
from notifier import send_discord_report

def analyze_ashare_ticker(ticker: str) -> dict:
    df = fetch_ashare_hist(ticker)
    if df is None: return None
    
    df = calculate_indicators(df)
    strategy = check_520_strategy(df)
    
    if strategy:
        latest = df.iloc[-1]
        return {
            'Ticker': ticker,
            'Price': f"{latest['Close']:.2f}",
            'Volume': f"{latest['Volume']:.0f}",
            'Signal': strategy
        }
    return None

def analyze_us_ticker(ticker: str) -> dict:
    df = fetch_historical_data(ticker)
    if df is None: return None
    
    df = calculate_indicators(df)
    strategy = check_520_strategy(df)
    
    if strategy:
        # Cross-border data fusion: Get options activity if there is a strategy flag
        options_alerts = fetch_options_activity(ticker)
        options_text = " | ".join(options_alerts) if options_alerts else "无显著异动"
        
        latest = df.iloc[-1]
        return {
            'Ticker': ticker,
            'Price': f"${latest['Close']:.2f}",
            'Volume': f"{latest['Volume']:.0f}",
            'Signal': strategy,
            'Options Alert': options_text
        }
    return None

def generate_markdown_report(a_results: list, us_results: list) -> str:
    date_str = datetime.now().strftime('%Y-%m-%d')
    report = f"# 全局市场扫描报告 ({date_str})\n\n"
    report += "## 策略说明\n"
    report += "- **520战法**: 5日均线与20日均线的交叉形态验证，结合期权资金流向研判。\n\n"
    
    if a_results:
        report += "## 🇨🇳 A股市场 520战法筛出标的\n"
        headers_a = ["Ticker", "Signal", "Price", "Volume"]
        table_a = [[r['Ticker'], r['Signal'], r['Price'], r['Volume']] for r in a_results]
        report += tabulate(table_a, headers=headers_a, tablefmt="github") + "\n\n"
    else:
        report += "## 🇨🇳 A股市场\n今日无符合 520金叉/死叉 的高流动性标的。\n\n"
        
    if us_results:
        report += "## 🇺🇸 美股市场 520战法 & 期权异动融合\n"
        headers_us = ["Ticker", "Signal", "Price", "Options Unusual Vol"]
        table_us = [[r['Ticker'], r['Signal'], r['Price'], r['Options Alert']] for r in us_results]
        report += tabulate(table_us, headers=headers_us, tablefmt="github") + "\n\n"
    else:
        report += "## 🇺🇸 美股市场\n今日无符合 520金叉/死叉 的高流动性标的。\n\n"
        
    return report

def run_global_scan(market: str = 'all'):
    print(f"=== 启动全局市场并行扫描器 [{market}] ===")
    a_results = []
    us_results = []
    
    # 因为 API 限制，这里设置安全的并发数
    MAX_WORKERS = 10 
    
    if market in ['a-share', 'all']:
        print("正在获取 A股高流动性标的池...")
        a_tickers = get_ashare_universe(top_n=300) # 扫前300高频交易标的
        print(f"A股待扫描数量: {len(a_tickers)}")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_ticker = {executor.submit(analyze_ashare_ticker, t): t for t in a_tickers}
            for future in as_completed(future_to_ticker):
                res = future.result()
                if res: a_results.append(res)
                
    if market in ['us-share', 'all']:
        print("正在获取 美股 S&P 500 标的池...")
        us_tickers = get_us_universe()
        print(f"美股待扫描数量: {len(us_tickers)}")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS*2) as executor:
            future_to_ticker = {executor.submit(analyze_us_ticker, t): t for t in us_tickers}
            for future in as_completed(future_to_ticker):
                res = future.result()
                if res: us_results.append(res)
                
    # 汇总并生成报告
    print("扫描完成，正在生成 Markdown 报告...")
    report_md = generate_markdown_report(a_results, us_results)
    
    filename = f"Market_Scan_Report_{datetime.now().strftime('%Y%m%d')}.md"
    send_discord_report("🔔 全局双向市场 520 策略扫盘报告", report_md, filename)
    print(f"扫描任务完毕，结果已保存至 {filename} 并推送到 Discord。")
