# 📈 Stock Trend Analyzer

A web app for exploring historical stock price data, calculating common technical indicators, and generating a short-term statistical price forecast — built as a hands-on project to learn time-series data handling, technical analysis concepts, and Streamlit deployment.

**Live app:** https://stocktrdanalyzer.streamlit.app

## What it does

- Look up any stock ticker supported by Yahoo Finance (e.g. `AAPL`, `TSLA`, `RELIANCE.NS`, `INFY.NS`)
- View historical OHLCV price data over a selectable time range
- Overlay standard technical indicators on a candlestick chart:
  - Simple Moving Average (SMA) — 20 and 50 day
  - Exponential Moving Average (EMA) — 20 day
  - Relative Strength Index (RSI) — 14 day
  - Bollinger Bands
- Generate a configurable-horizon (7–60 day) price forecast using Facebook Prophet, shown with an 80% uncertainty interval

## What it is not

This is a data visualization and forecasting **learning project**, not a trading or investment tool. Specifically:

- The forecast is a statistical extrapolation of historical price patterns only. It has no awareness of news, earnings, macroeconomic events, or anything that actually moves markets.
- Technical indicators describe past price behavior; they are not proven predictors of future price movement, and different traders can read the same indicator differently.
- Nothing in this app constitutes financial advice. Don't make investment decisions based on it.

## Tech stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Live data | yfinance (Yahoo Finance API wrapper) |
| Data handling | pandas, numpy |
| Charts | Plotly |
| Forecasting | Prophet (Meta/Facebook's time-series forecasting library) |
| Deployment | Streamlit Community Cloud |

## Running locally

```bash
git clone https://github.com/Samar-774/stock-trend-analyzer.git
cd stock-trend-analyzer
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

**Note for Windows users:** Prophet's Stan backend can fail with a `DLL not found` error (Windows exit code `0xC0000135`) due to missing Intel TBB runtime libraries. If you hit this, install via conda instead (`conda install -c conda-forge prophet`) and ensure the TBB DLLs from the conda environment's `Library/bin` are discoverable on PATH or copied alongside `prophet/stan_model/`.

## Project structure
```text
stock-trend-analyzer/ 
├── app.py                 # Streamlit UI
├── src/
│   ├── data_fetcher.py    # yfinance data pulling
│   ├── indicators.py      # SMA, EMA, RSI, Bollinger Bands
│   └── forecaster.py      # Prophet forecasting
├── requirements.txt
├── runtime.txt
└── README.md
```


## Possible future improvements

- Add more indicators (MACD, volume-weighted average price)
- Compare multiple tickers side by side
- Cache API calls to reduce redundant yfinance requests
- Backtest forecast accuracy against actual historical outcomes to show error metrics, rather than just displaying the projection