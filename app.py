import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_fetcher import fetch_stock_data, get_company_info
from src.indicators import add_all_indicators

st.set_page_config(page_title="Stock Trend Analyzer", layout="wide")

st.title("📈 Stock Market Trend Analyzer")

ticker = st.text_input("Enter a stock ticker", value="AAPL").upper().strip()
period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

if ticker:
    with st.spinner(f"Fetching data for {ticker}..."):
        df = fetch_stock_data(ticker, period=period)
        info = get_company_info(ticker)

    if df.empty:
        st.error(f"No data found for '{ticker}'. Check the symbol (e.g. RELIANCE.NS for NSE).")
    else:
        df = add_all_indicators(df)

        st.subheader(info["name"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", info["current_price"])
        col2.metric("Sector", info["sector"])
        col3.metric("Currency", info["currency"])

        # --- Indicator toggles ---
        st.markdown("#### Chart Options")
        show_sma = st.checkbox("Show SMA (20, 50)", value=True)
        show_ema = st.checkbox("Show EMA (20)", value=True)
        show_bb = st.checkbox("Show Bollinger Bands", value=True)

        # --- Price chart with overlays, RSI as a subplot below ---
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            row_heights=[0.75, 0.25],
            vertical_spacing=0.05,
            subplot_titles=(f"{ticker} Price", "RSI (14)")
        )

        # Candlestick price
        fig.add_trace(
            go.Candlestick(
                x=df["Date"], open=df["Open"], high=df["High"],
                low=df["Low"], close=df["Close"], name="Price"
            ),
            row=1, col=1
        )

        if show_sma:
            fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA_20"], name="SMA 20",
                                      line=dict(width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA_50"], name="SMA 50",
                                      line=dict(width=1.5)), row=1, col=1)

        if show_ema:
            fig.add_trace(go.Scatter(x=df["Date"], y=df["EMA_20"], name="EMA 20",
                                      line=dict(width=1.5, dash="dot")), row=1, col=1)

        if show_bb:
            fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Upper"], name="BB Upper",
                                      line=dict(width=1, color="gray"), opacity=0.6), row=1, col=1)
            fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Lower"], name="BB Lower",
                                      line=dict(width=1, color="gray"), opacity=0.6,
                                      fill="tonexty", fillcolor="rgba(128,128,128,0.1)"), row=1, col=1)

        # RSI subplot with overbought/oversold reference lines
        fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], name="RSI",
                                  line=dict(width=1.5, color="purple")), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)

        fig.update_layout(
            height=700,
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(t=40, b=20)
        )
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            df[["Date", "Close", "SMA_20", "EMA_20", "RSI", "BB_Upper", "BB_Lower"]].tail(10),
            use_container_width=True
        )

        st.caption("Hour 3 will add Prophet-based 30-day forecasting.")