import pandas as pd


def add_sma(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    df[f"SMA_{window}"] = df["Close"].rolling(window=window).mean()
    return df


def add_ema(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    df[f"EMA_{window}"] = df["Close"].ewm(span=window, adjust=False).mean()
    return df


def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    delta = df["Close"].diff()

    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def add_bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    sma = df["Close"].rolling(window=window).mean()
    std = df["Close"].rolling(window=window).std()

    df["BB_Middle"] = sma
    df["BB_Upper"] = sma + (num_std * std)
    df["BB_Lower"] = sma - (num_std * std)
    return df


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = add_sma(df, window=20)
    df = add_sma(df, window=50)
    df = add_ema(df, window=20)
    df = add_rsi(df, window=14)
    df = add_bollinger_bands(df, window=20)
    return df


if __name__ == "__main__":
    # Quick manual test
    from data_fetcher import fetch_stock_data

    data = fetch_stock_data("AAPL", period="6mo")
    data = add_all_indicators(data)
    print(data[["Date", "Close", "SMA_20", "EMA_20", "RSI", "BB_Upper", "BB_Lower"]].tail(10))