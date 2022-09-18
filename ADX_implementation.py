
import yfinance as yf
import numpy as np


stocks = ["AMZN", "META", "GOOG"]
clhv = {}

for ticker in stocks:
    temp = yf.download(ticker, period='1mo', interval='15m')
    temp.dropna(how="any", inplace=True)
    clhv[ticker] = temp
# For loop to get our data

def ATR(DF, n=14):
    df = DF.copy()
    df["H-L"] = df["High"] - df["Low"]
    df["H-PC"] = df["High"] - df["Adj Close"].shift(1)
    df["L-PC"] = df["Low"] - df["Adj Close"].shift(1)
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df["ATR"] = df["TR"].ewm(com=n, min_periods=n).mean() # Use com for atr instead of span as it makes data more accurate
    return df["ATR"]


# ADX (Average Directional Index) - Calculates strength of the trend

def ADX(DF, n=20):
    df = DF.copy()
    df["ATR"] = ATR(df, n)
    df["upmove"] = df["High"] - df["High"].shift(1)
    df["downmove"] = df["Low"].shift(1) - df["Low"]
    df["+dm"] = np.where((df["upmove"]>df["downmove"]) & (df["upmove"] > 0),df['upmove'],0)
    df["-dm"] = np.where((df["upmove"]<df["downmove"]) & (df["downmove"] > 0),df['downmove'],0)
    df["+di"] = 100 * (df["+dm"]/df["ATR"]).ewm(span=n, min_periods=n).mean()
    df["-di"] = 100 * (df["-dm"]/df["ATR"]).ewm(span=n, min_periods=n).mean()
    df["ADX"] = 100 * abs((df["+di"] - df["-di"]) / (df["+di"] + df["-di"])).ewm(span=n, min_periods=n).mean()
    return df["ADX"]

for ticker in clhv:
    clhv[ticker]["ADX"] = ADX(clhv[ticker])
    
    