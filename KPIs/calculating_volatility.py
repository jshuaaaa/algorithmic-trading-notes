
import yfinance as yf
import numpy as np
import talib
import copy

stocks = ["AMZN", "META", "GOOG"]
clhv = {}


for ticker in stocks:
    temp = yf.download(ticker, period='7mo', interval='1d')
    temp.dropna(how="any", inplace=True)
    clhv[ticker] = temp
    
def volatility(DF):
    df = DF.copy()
    df["return"] =  df["Adj Close"].pct_change()
    vol = df["return"].std() * np.sqrt(252) # annualized volatility
    return vol

for ticker in clhv:
    print("Volatility of {} = {}".format(ticker, volatility(clhv[ticker])))

# Calculating volatility of given stock data









    
    