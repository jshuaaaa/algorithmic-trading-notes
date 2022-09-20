
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
    
def volatility(DF):
    df = DF.copy()
    df["return"] =  df["Adj Close"].pct_change()
    vol = df["return"].std() * np.sqrt(252) # annualized volatility
    return vol   


def CAGR(DF):
    df = DF.copy()
    df["return"] = df["Adj Close"].pct_change() 
    df["cum_return"] = (1+df["return"]).cumprod()
    n = len(df)/252
    CAGR = (df["cum_return"][-1])**(1/n) - 1
    return CAGR

def Sharpe(DF, rf):
    df = DF.copy()
    sharpe = (CAGR(df) - rf) / volatility(df)
    return sharpe

def Sortino(DF, rf):
    df = DF.copy()
    df["return"] = df["Adj Close"].pct_change()
    negative_return = np.where(df["return"]>0,0,df["return"]) # NumPy if statement syntax
    neg_vol = pd.Series(negative_return[negative_return!=0]).std() * np.sqrt(252)# using panda series to ignore zeros and find std ignoring NaN values
    return (CAGR(df) - rf) / neg_vol

for ticker in clhv:
    print("Sharpe for {} = {}".format(ticker,Sharpe(clhv[ticker],0.03)))
    print("Sortino for {} = {}".format(ticker,Sortino(clhv[ticker],0.03)))
    
    
    
    
    