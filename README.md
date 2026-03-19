# TradingSystem

This repository is a Trading System Bot primarily used to monitor and analyze A-shares, US-shares, ETFs, and options. It routinely sends alerts and analysis reports to a designated Discord bot.

## Deployment

The system is configured to run automatically using **GitHub Actions**.

### Setup Instructions

1. **Fork or Clone this repository**.
2. Go to your GitHub Repository Settings -> Secrets and variables -> Actions.
3. Add a new Repository Secret named `DISCORD_WEBHOOK` and paste your Discord Webhook URL.
4. The GitHub Action will run automatically on schedule (Mon-Fri) based on trading hours:
   - **A-Share / ETF Close**: 15:10 Beijing Time (07:10 UTC)
   - **US-Share / ETF Close**: 16:30 EST/EDT (20:30 UTC)
5. You can also manually trigger the scan from the `Actions` tab manually.

## Local Execution

To run the bot locally:

```bash
# Set up venv
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run for a specific market (requires DISCORD_WEBHOOK env var for Discord messages)
# DISCORD_WEBHOOK="your_url" python main.py --market all
python main.py --market a-share
python main.py --market us-share
```

## Features
- **Multi-market Monitoring**: Supports Yahoo Finance tickers (A-shares use `.SS` or `.SZ` suffix).
- **Technical Indicators**: 
  - Overbought/Oversold detection (RSI)
  - Trend MA crosses (SMA 20/50 Golden & Death crosses)
  - MACD signals
  - Volatility & Breakout detection (Bollinger Bands)
  - Volume anomaly alerts (2.5x of 10-day average)