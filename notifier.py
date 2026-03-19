import requests
import json
from datetime import datetime
from config import DISCORD_WEBHOOK

def send_discord_alert(category: str, ticker: str, data: dict, signals: list):
    """
    发送 Discord 消息通知
    """
    if not DISCORD_WEBHOOK:
        print("未配置 DISCORD_WEBHOOK, 跳过通知。")
        return
        
    price = data['price']
    prev_close = data['prev_close']
    volume = data['volume']
    
    change_pct = ((price - prev_close) / prev_close) * 100
    
    # 根据涨跌设置颜色
    color = 65280 if change_pct >= 0 else 16711680 # 绿色或红色
    trend_emoji = "📈" if change_pct >= 0 else "📉"
    
    # 构造信号文本
    signal_text = "\n".join(signals) if signals else "无明显技术信号"
    
    embed = {
        "title": f"📊 {category} 监控播报: {ticker}",
        "color": color,
        "fields": [
            {
                "name": "当前价格",
                "value": f"{price:.2f}",
                "inline": True
            },
            {
                "name": "今日涨跌",
                "value": f"{change_pct:.2f}% {trend_emoji}",
                "inline": True
            },
            {
                "name": "成交量",
                "value": f"{int(volume):,}",
                "inline": False
            },
            {
                "name": "技术指标信号",
                "value": signal_text,
                "inline": False
            }
        ],
        "footer": {
            "text": f"云端全自动监控 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }
    
    payload = {
        "embeds": [embed]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        if response.status_code == 204:
            print(f"[{ticker}] 通知已成功发送到 Discord")
        else:
            print(f"[{ticker}] 发送失败: HTTP {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[{ticker}] 发送异常: {e}")
