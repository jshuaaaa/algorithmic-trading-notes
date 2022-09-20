
import yfinance as yf
import numpy as np
import pandas as pd
import talib
import copy

stocks = ["AMZN", "META", "GOOG"]
clhv = {}


for ticker in stocks:
    temp = yf.download(ticker, period='7mo', interval='1d')
    temp.dropna(how="any", inplace=True)
    clhv[ticker] = temp
    
# CAGR Implementation
def CAGR(DF):
    df = DF.copy()
    df["return"] = df["Adj Close"].pct_change() 
    df["cum_return"] = (1+df["return"]).cumprod()
    n = len(df)/252
    CAGR = (df["cum_return"][-1])**(1/n) - 1
    return CAGR
    
# Implementing Max Drawdown

def maximum_drawdown(DF):
    df = DF.copy()
    df["return"] = df["Adj Close"].pct_change()
    df["cum_return"] = (1+df["return"]).cumprod()
    df["cum_rolling_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_rolling_max"] - df["cum_return"]
    return (df["drawdown"]/df["cum_rolling_max"]).max()


# Implementing Calmar Ratio    


def Calmar(DF):
    df = DF.copy()
    cagr = CAGR(df)
    drawdown = maximum_drawdown(df)
    return cagr / drawdown
    

for ticker in clhv:
    print("max drawdown of {} = {}".format(ticker,maximum_drawdown(clhv[ticker])))
    print("Calmar of {} = {}".format(ticker,Calmar(clhv[ticker])))



    
    
    
    