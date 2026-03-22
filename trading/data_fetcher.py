import yfinance as yf
import pandas as pd
import akshare as ak
from concurrent.futures import ThreadPoolExecutor

def fetch_historical_data(ticker: str, period: str = '6mo') -> pd.DataFrame:
    """获取美股/ETF单标的日线历史数据"""
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period)
        if df.empty or len(df) < 50: 
            return None
        return df
    except Exception as e:
        return None

def fetch_ashare_hist(symbol: str) -> pd.DataFrame:
    """获取A股单标的日线历史数据 (使用akshare)"""
    try:
        # 兼容性处理，AKShare 的代码一般不需要后缀
        clean_symbol = symbol.replace('.SS', '').replace('.SZ', '')
        # 如果是指数或是带后缀的，可以在这里做特殊处理，但这里为了简便直接拉A股个股
        df = ak.stock_zh_a_hist(symbol=clean_symbol, period="daily", start_date="20230101", adjust="qfq")
        if df.empty or len(df) < 50:
            return None
        # 统一格式以复用 yfinance 的 indicators 逻辑
        df.rename(columns={'收盘': 'Close', '成交量': 'Volume', '日期': 'Date'}, inplace=True)
        # 将最新的放在最后
        df.set_index('Date', inplace=True)
        return df
    except Exception as e:
        return None

import requests
import io
from .config import A_SHARE_WATCHLIST

def get_us_universe() -> list:
    """获取美国全市场(以S&P 500和纳斯达克100作为高流动性代表)"""
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        
        # 规避 pd.read_html() 直接读 URL 导致的 403 阻断
        sp500 = pd.read_html(io.StringIO(resp.text))[0]
        sp500_tickers = sp500['Symbol'].tolist()
        
        # 将 BRK.B 替换为 BRK-B，以适应 yfinance 的格式
        sp500_tickers = [t.replace('.', '-') for t in sp500_tickers]
        return list(set(sp500_tickers))
    except Exception as e:
        print(f"获取美股名录失败: {e}")
        return ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA'] # Fallback

def get_ashare_universe(top_n=500) -> list:
    """使用 akshare 获取A股今日成交额最高的前N只股票作为分析池(提升效率且保证流动性)"""
    try:
        df = ak.stock_zh_a_spot_em()
        # 降序排列成交额
        df = df.sort_values(by="成交额", ascending=False).head(top_n)
        return df['代码'].tolist()
    except Exception as e:
        print(f"获取A股现货市场失败: {e}")
        print("降级使用默认 Config 中的 A_SHARE_WATCHLIST。")
        # 如果获取失败，则返回精简版的默认 watchlist，防止扫描数量为0
        return [t.replace('.SS', '').replace('.SZ', '') for t in A_SHARE_WATCHLIST]


def fetch_options_activity(ticker: str) -> list:
    """获取近期到期的期权链异动情况 (Cross-border Data Fusion)"""
    try:
        t = yf.Ticker(ticker)
        dates = t.options
        if not dates:
            return []
            
        near_term_date = dates[0] 
        opt_chain = t.option_chain(near_term_date)
        
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        # 寻找较高成交量的合约：成交量大于未平仓量，且单日成交大于1000手
        unusual_calls = calls[(calls['volume'] > 1000) & (calls['volume'] > calls['openInterest'])]
        unusual_puts = puts[(puts['volume'] > 1000) & (puts['volume'] > puts['openInterest'])]
        
        results = []
        for _, row in unusual_calls.iterrows():
            results.append(f"🟢 异动CALL: Strike {row['strike']} (Vol: {row['volume']:.0f}, OI: {row['openInterest']:.0f}, IV: {row['impliedVolatility']:.2%})")
        for _, row in unusual_puts.iterrows():
            results.append(f"🔴 异动PUT: Strike {row['strike']} (Vol: {row['volume']:.0f}, OI: {row['openInterest']:.0f}, IV: {row['impliedVolatility']:.2%})")
            
        return results
    except Exception as e:
        return []
