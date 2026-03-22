import requests
import json
from datetime import datetime
from .config import DISCORD_WEBHOOK
import os

def send_discord_alert(category: str, ticker: str, data: dict, signals: list):
    """
    发送单个股票的 Discord 卡片通知
    """
    if not DISCORD_WEBHOOK:
        return
        
    price = data['price']
    prev_close = data['prev_close']
    volume = data['volume']
    change_pct = ((price - prev_close) / prev_close) * 100
    
    color = 65280 if change_pct >= 0 else 16711680 
    trend_emoji = "📈" if change_pct >= 0 else "📉"
    
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
    
    try:
        requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]})
    except Exception as e:
        print(f"[{ticker}] 发送异常: {e}")

def send_discord_report(report_title: str, report_content: str, filename: str):
    """
    将扫描报告作为文件发送到 Discord，避免 2000 字符限制
    """
    if not DISCORD_WEBHOOK:
        print("未配置 DISCORD_WEBHOOK, 跳过报告发送。")
        return
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    payload_json = {
        "content": f"**{report_title}**\n扫描已完成，具体符合策略的标的请查看附件报告 👇",
    }
    
    try:
        with open(filename, 'rb') as f:
            response = requests.post(
                DISCORD_WEBHOOK,
                data={"payload_json": json.dumps(payload_json)},
                files={"file": (filename, f, "text/markdown")}
            )
        if response.status_code in [200, 204]:
            print(f"✅ 报告 {filename} 已通过 Discord 发送。")
        else:
            print(f"❌ 报告发送失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"发送报告异常: {e}")
