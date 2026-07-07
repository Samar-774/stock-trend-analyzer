import yfinance as yf
import pandas as pd


def fetch_stock_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)

    if df.empty:
        return df

    # yfinance sometimes returns tz-aware index; strip it for easier merging later
    df.index = df.index.tz_localize(None)
    df = df.reset_index()
    return df


def get_company_info(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "currency": info.get("currency", "N/A"),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
        }
    except Exception:
        return {"name": ticker, "sector": "N/A", "currency": "N/A", "current_price": "N/A"}


if __name__ == "__main__":
    # Quick manual test: run `python src/data_fetcher.py` to sanity-check the fetch works
    data = fetch_stock_data("AAPL", period="6mo")
    print(data.head())
    print(f"\nRows fetched: {len(data)}")
    print(get_company_info("AAPL"))