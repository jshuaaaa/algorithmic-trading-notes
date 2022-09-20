
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

    # n is needed for cum return, n is the length of our data divided by the trading year
    # Note that if using smaller time data needed to divide further to get accurate n
# CAGR Implementation
def CAGR(DF):
    df = DF.copy()
    df["return"] = df["Adj Close"].pct_change() 
    df["cum_return"] = (1+df["return"]).cumprod()
    n = len(df)/252
    CAGR = (df["cum_return"][-1])**(1/n) - 1
    return CAGR

for ticker in clhv:
    print("CAGR for {} = {}".format(ticker, CAGR(clhv[ticker])))









    
    