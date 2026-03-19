import yfinance as yf
import pandas as pd

def fetch_historical_data(ticker: str, period: str = '6mo') -> pd.DataFrame:
    """获取标的的日线历史数据"""
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period)
        if df.empty or len(df) < 50: 
            print(f"[{ticker}] 数据不足或获取失败。")
            return None
        return df
    except Exception as e:
        print(f"[{ticker}] 数据获取异常: {e}")
        return None

def fetch_options_activity(ticker: str) -> list:
    """简单获取近期到期的期权链异动情况"""
    try:
        t = yf.Ticker(ticker)
        dates = t.options
        if not dates:
            return []
            
        near_term_date = dates[0] # 取最近的到期日
        opt_chain = t.option_chain(near_term_date)
        
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        # 寻找较高成交量的合约
        unusual_calls = calls[(calls['volume'] > 5000) & (calls['impliedVolatility'] > 0.3)]
        unusual_puts = puts[(puts['volume'] > 5000) & (puts['impliedVolatility'] > 0.3)]
        
        results = []
        for _, row in unusual_calls.iterrows():
            results.append(f"🟢 CALL {row['strike']} (vol: {row['volume']})")
        for _, row in unusual_puts.iterrows():
            results.append(f"🔴 PUT {row['strike']} (vol: {row['volume']})")
            
        return results
    except Exception as e:
        print(f"[{ticker}] 期权数据获取异常: {e}")
        return []
