import pandas as pd
import numpy as np

def calculate_sma(df: pd.DataFrame, column: str = 'Close', length: int = 20) -> pd.Series:
    return df[column].rolling(window=length).mean()

def calculate_rsi(df: pd.DataFrame, column: str = 'Close', length: int = 14) -> pd.Series:
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    
    avg_gain = gain.rolling(window=length).mean()
    avg_loss = loss.rolling(window=length).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(df: pd.DataFrame, column: str = 'Close', fast: int = 12, slow: int = 26, signal: int = 9):
    exp1 = df[column].ewm(span=fast, adjust=False).mean()
    exp2 = df[column].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd, macd_signal

def calculate_bbands(df: pd.DataFrame, column: str = 'Close', length: int = 20, std: float = 2.0):
    sma = calculate_sma(df, column, length)
    rolling_std = df[column].rolling(window=length).std()
    upper_band = sma + (rolling_std * std)
    lower_band = sma - (rolling_std * std)
    return lower_band, upper_band

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算常用的技术指标"""
    # 均线体系 (包括 5日 和 20日 战法)
    df['SMA_5'] = calculate_sma(df, length=5)
    df['SMA_20'] = calculate_sma(df, length=20)
    df['SMA_50'] = calculate_sma(df, length=50)
    df['SMA_200'] = calculate_sma(df, length=200)
    
    # RSI
    df['RSI_14'] = calculate_rsi(df, length=14)
    
    # MACD
    macd, macd_signal = calculate_macd(df)
    df['MACD'] = macd
    df['MACDs'] = macd_signal
    
    # Bollinger Bands
    lower, upper = calculate_bbands(df, length=20, std=2.0)
    df['BBL_20'] = lower
    df['BBU_20'] = upper
    
    # 均量线
    df['VOL_SMA_10'] = calculate_sma(df, column='Volume', length=10)
    
    return df

def check_520_strategy(df: pd.DataFrame) -> str:
    """
    执行 520 战法检查
    返回: 'Golden Cross' (金叉买入), 'Death Cross' (死叉卖出), or None
    """
    if df is None or len(df) < 25:
        return None
        
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    sma5 = last_row.get('SMA_5')
    sma20 = last_row.get('SMA_20')
    prev_sma5 = prev_row.get('SMA_5')
    prev_sma20 = prev_row.get('SMA_20')
    
    if pd.isna(sma5) or pd.isna(sma20) or pd.isna(prev_sma5) or pd.isna(prev_sma20):
        return None
        
    # 金叉：今天 5日线 > 20日线，昨天 5日线 <= 20日线
    if prev_sma5 <= prev_sma20 and sma5 > sma20:
        return 'Golden Cross'
        
    # 死叉：今天 5日线 < 20日线，昨天 5日线 >= 20日线
    elif prev_sma5 >= prev_sma20 and sma5 < sma20:
        return 'Death Cross'
        
    return None

def evaluate_signals(df: pd.DataFrame) -> list:
    """评估技术指标状态并生成常规播报信号文本"""
    # ...与之前一致，用于监控列表...
    if df is None or len(df) < 50:
        return []
        
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    signals = []
    
    rsi = last_row.get('RSI_14', 50)
    if not np.isnan(rsi):
        if rsi < 30: signals.append("🟢 RSI超卖 (近期回调较深，存在反弹预期)")
        elif rsi > 70: signals.append("🔴 RSI超买 (近期涨幅过大，注意回调风险)")
        
    # 520 战法直接融入播报
    strategy_520 = check_520_strategy(df)
    if strategy_520 == 'Golden Cross':
        signals.append("🌟 【520战法触发】: 5日均线刚刚上穿20日均线 (金叉买入信号)")
    elif strategy_520 == 'Death Cross':
        signals.append("⚠️ 【520战法触发】: 5日均线下穿20日均线 (死叉卖出/避险信号)")
            
    # BOLL
    boll_l = last_row.get('BBL_20')
    boll_u = last_row.get('BBU_20')
    close_price = last_row.get('Close')
    if pd.notna(boll_l) and close_price < boll_l:
        signals.append("📉 跌破布林带下轨 (极度弱势或超跌)")
    elif pd.notna(boll_u) and close_price > boll_u:
        signals.append("📈 突破布林带上轨 (极度强势或超买)")
        
    # 成交量异动
    avg_vol = last_row.get('VOL_SMA_10')
    volume = last_row.get('Volume')
    if pd.notna(avg_vol) and volume > (avg_vol * 2.5):
        signals.append("💥 成交量异动 (超10日均量 2.5倍)")
            
    return signals
