import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_fetcher import fetch_stock_data, get_company_info
from src.indicators import add_all_indicators
from src.forecaster import generate_forecast

st.set_page_config(page_title="Stock Trend Analyzer", page_icon="📈", layout="wide")

# --- Sidebar controls ---
with st.sidebar:
    st.title("📈 Stock Trend Analyzer")
    st.caption("Live data, technical indicators, and forecasting")

    ticker = st.text_input("Ticker Symbol", value="AAPL", help="e.g. AAPL, TSLA, RELIANCE.NS, INFY.NS").upper().strip()
    period = st.selectbox("Historical Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

    st.markdown("---")
    st.markdown("**Chart Overlays**")
    show_sma = st.checkbox("SMA (20, 50)", value=True)
    show_ema = st.checkbox("EMA (20)", value=True)
    show_bb = st.checkbox("Bollinger Bands", value=True)

    st.markdown("---")
    forecast_days = st.slider("Forecast horizon (days)", min_value=7, max_value=60, value=30, step=7)

    st.markdown("---")
    st.caption("Built with Streamlit, yfinance, Prophet & Plotly")

if not ticker:
    st.info("Enter a ticker in the sidebar to get started.")
    st.stop()

with st.spinner(f"Fetching data for {ticker}..."):
    df = fetch_stock_data(ticker, period=period)
    info = get_company_info(ticker)

if df.empty:
    st.error(f"No data found for '{ticker}'. Check the symbol (e.g. RELIANCE.NS for NSE stocks).")
    st.stop()

df = add_all_indicators(df)

# --- Header ---
st.markdown(f"## {info['name']} ({ticker})")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Price", f"{info['current_price']} {info['currency']}")
col2.metric("Sector", info["sector"])
latest_rsi = df["RSI"].iloc[-1]
rsi_label = "Overbought" if latest_rsi > 70 else "Oversold" if latest_rsi < 30 else "Neutral"
col3.metric("RSI (14)", f"{latest_rsi:.1f}", rsi_label)
price_change = df["Close"].iloc[-1] - df["Close"].iloc[-2]
pct_change = (price_change / df["Close"].iloc[-2]) * 100
col4.metric("Last Change", f"{price_change:+.2f}", f"{pct_change:+.2f}%")

st.markdown("---")

# --- Tabs ---
tab_overview, tab_technical, tab_forecast = st.tabs(["📋 Overview", "📊 Technical Analysis", "🔮 Forecast"])

with tab_overview:
    st.markdown("#### Recent Price Data")
    st.dataframe(
        df[["Date", "Open", "High", "Low", "Close", "Volume"]].tail(15).sort_values("Date", ascending=False),
        use_container_width=True, hide_index=True
    )

with tab_technical:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.75, 0.25], vertical_spacing=0.05,
        subplot_titles=(f"{ticker} Price", "RSI (14)")
    )

    fig.add_trace(go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Price"
    ), row=1, col=1)

    if show_sma:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA_20"], name="SMA 20", line=dict(width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA_50"], name="SMA 50", line=dict(width=1.5)), row=1, col=1)

    if show_ema:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["EMA_20"], name="EMA 20",
                                  line=dict(width=1.5, dash="dot")), row=1, col=1)

    if show_bb:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Upper"], name="BB Upper",
                                  line=dict(width=1, color="gray"), opacity=0.6), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Lower"], name="BB Lower",
                                  line=dict(width=1, color="gray"), opacity=0.6,
                                  fill="tonexty", fillcolor="rgba(128,128,128,0.1)"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], name="RSI",
                              line=dict(width=1.5, color="purple")), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)

    fig.update_layout(
        height=650, xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=40, b=20)
    )
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("ℹ️ What do these indicators mean?"):
        st.markdown("""
        - **SMA (Simple Moving Average):** Average closing price over N days — smooths noise to show the trend.
        - **EMA (Exponential Moving Average):** Like SMA but weights recent prices more — reacts faster to changes.
        - **RSI (Relative Strength Index):** Momentum score 0-100. Above 70 = overbought, below 30 = oversold.
        - **Bollinger Bands:** Bands around a moving average based on volatility (standard deviation). Widening bands = rising volatility.
        """)

with tab_forecast:
    with st.spinner(f"Running {forecast_days}-day Prophet forecast..."):
        forecast = generate_forecast(df, periods=forecast_days)

    forecast_fig = go.Figure()
    forecast_fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Historical Close",
                                       line=dict(color="royalblue")))

    last_hist_date = df["Date"].max()
    future_forecast = forecast[forecast["ds"] > last_hist_date]

    forecast_fig.add_trace(go.Scatter(x=future_forecast["ds"], y=future_forecast["yhat"], name="Forecast",
                                       line=dict(color="orange", dash="dash")))
    forecast_fig.add_trace(go.Scatter(x=future_forecast["ds"], y=future_forecast["yhat_upper"],
                                       line=dict(width=0), showlegend=False, hoverinfo="skip"))
    forecast_fig.add_trace(go.Scatter(x=future_forecast["ds"], y=future_forecast["yhat_lower"],
                                       line=dict(width=0), fill="tonexty", fillcolor="rgba(255,165,0,0.2)",
                                       name="80% Confidence Interval", hoverinfo="skip"))

    forecast_fig.update_layout(
        height=500, legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=40, b=20), yaxis_title="Price"
    )
    st.plotly_chart(forecast_fig, use_container_width=True)

    forecast_end_price = future_forecast["yhat"].iloc[-1]
    current_price = df["Close"].iloc[-1]
    forecast_pct = ((forecast_end_price - current_price) / current_price) * 100
    st.metric(f"Projected price in {forecast_days} days", f"{forecast_end_price:.2f}", f"{forecast_pct:+.2f}%")

    st.caption(
        "⚠️ This forecast is a statistical projection based on historical trends only. "
        "It does not account for news, earnings, or market events, and should not be used as financial advice."
    )