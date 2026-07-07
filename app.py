import streamlit as st
from src.data_fetcher import fetch_stock_data, get_company_info

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
        st.subheader(info["name"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", info["current_price"])
        col2.metric("Sector", info["sector"])
        col3.metric("Currency", info["currency"])

        st.dataframe(df.tail(10), use_container_width=True)
        st.caption(f"{len(df)} rows fetched | Hour 2 will add SMA/EMA/RSI/Bollinger Bands here.")