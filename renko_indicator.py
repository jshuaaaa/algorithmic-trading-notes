
import yfinance as yf
import numpy as np
from stocktrends import Renko


stocks = ["AMZN", "META", "GOOG"]
clhv = {}
hour_data = {}
renko_data = {}

for ticker in stocks:
    temp = yf.download(ticker, period='1mo', interval='15m')
    temp.dropna(how="any", inplace=True)
    clhv[ticker] = temp
    temp = yf.download(ticker, period='1y', interval='1h')
    temp.dropna(how="any", inplace=True)
    hour_data[ticker] = temp
# For loop to get our data

# ATR implementation
def ATR(DF, n=14):
    df = DF.copy()
    df["H-L"] = df["High"] - df["Low"]
    df["H-PC"] = df["High"] - df["Adj Close"].shift(1)
    df["L-PC"] = df["Low"] - df["Adj Close"].shift(1)
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df["ATR"] = df["TR"].ewm(com=n, min_periods=n).mean() # Use com for atr instead of span as it makes data more accurate
    return df["ATR"]


# Renko charting implementation

def renko_DF(DF, hourly_df):
    df = DF.copy()
    df.drop("Close", axis=1, inplace=True)
    df.reset_index(inplace=True)
    df.columns = ["date", "open", "high", "low", "close", "volume"] # Making columns stocktrends compatible
    df2 = Renko(df)
    df2.brick_size = 3 * round(ATR(hourly_df,120).iloc[-1], 0)
    renko_df = df2.get_ohlc_data() # Using stocktrends library to implement renko charting data
    return renko_df

for ticker in clhv:
    renko_data[ticker] = renko_DF(clhv[ticker], hour_data[ticker])    


    
    