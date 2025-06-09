import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io

def get_stock_prediction(ticker: str):
    data = yf.Ticker(ticker)
    data = data.history(period="max")

    data = data.drop(["Dividends", "Stock Splits"], axis=1)

    data["Target"] = (data["Close"].shift(-1) > data["Close"]).astype(int)

    data = data.loc["1990-01-01":].copy()

    horizons = [2, 5, 60, 250, 1000]
    predictors = []
    for horizon in horizons:
        rolling_averages = data.rolling(horizon).mean()

        ratio_column = f"Close_Ratio_{horizon}"
        data[ratio_column] = data["Close"] / rolling_averages["Close"]

        trend_column = f"Trend_{horizon}"
        data[trend_column] = data.shift(1).rolling(horizon).sum()["Target"]

        predictors += [ratio_column, trend_column]

    data = data.dropna()

    model = RandomForestClassifier(n_estimators=200, min_samples_split=50, random_state=1)

    train = data.iloc[:-1].copy()
    test = data.iloc[-1:].copy()

    model.fit(train[predictors], train["Target"])
    prob = model.predict_proba(test[predictors])[:, 1][0]
    prediction = int(prob >= 0.5)
    prob *= 100
    
    return {
        "Date": test.index[0],
        "Prediction": prediction,
        "Increase_Prob": f"{prob:.2f}"
    }

def get_chart(ticker: str, time_pd: str):
    data = yf.Ticker(ticker)
    data = data.history(period=time_pd)

    if time_pd == "1wk":
        title_time_pd = "1 Week"
    elif time_pd == "1mo":
        title_time_pd = "1 Month"
    elif time_pd == "6mo":
        title_time_pd = "6 Months"
    elif time_pd == "1y":
        title_time_pd = "1 Year"
    elif time_pd == "5y":
        title_time_pd = "5 Years"
    else:
        title_time_pd = "All Time"

    plt.figure()
    plt.plot(data.index, data['Close'])
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.title(f"{ticker} Close Price ({title_time_pd})")

    ax = plt.gca()

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d-%Y'))

    if time_pd == "1wk":
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    else:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.gcf().autofmt_xdate()
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close()
    img_buf.seek(0)
    return img_buf


