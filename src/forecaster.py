import pandas as pd
from prophet import Prophet


def generate_forecast(df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:

    prophet_df = df[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})
    prophet_df = prophet_df.dropna()

    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.80
    )
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]


if __name__ == "__main__":
    from data_fetcher import fetch_stock_data

    data = fetch_stock_data("AAPL", period="1y")
    result = generate_forecast(data, periods=30)
    print(result.tail(35))