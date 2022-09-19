
import yfinance as yf
import numpy as np
import pandas as pd
import talib
import copy
import datetime as dt
import matplotlib.pyplot as plt
import time

stocks = ["AMZN", "META", "GOOG",
          "CVX", "CVNA"]
clhv = {}



def CAGR(DF):
    df = DF.copy()
    df["cum_return"] = (1+df["ret"]).cumprod()
    n = len(df)/(252*78)
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR


def volatility(DF):
    df = DF.copy()
    vol = df["ret"].std() * np.sqrt(252*78) # annualized volatility
    return vol


def ATR(DF, n=14):
    df = DF.copy()
    df["H-L"] = df["High"] - df["Low"]
    df["H-PC"] = df["High"] - df["Adj Close"].shift(1)
    df["L-PC"] = df["Low"] - df["Adj Close"].shift(1)
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df["ATR"] = df["TR"].ewm(com=n, min_periods=n).mean() # Use com for atr instead of span as it makes data more accurate
    return df["ATR"]

def Sharpe(DF, rf):
    df = DF.copy()
    sharpe = (CAGR(df) - rf) / volatility(df)
    return sharpe

def maximum_drawdown(DF):
    df = DF.copy()
    df["cum_return"] = (1+df["ret"]).cumprod()
    df["cum_rolling_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_rolling_max"] - df["cum_return"]
    return (df["drawdown"]/df["cum_rolling_max"]).max()

# Download Data

for ticker in stocks:
    temp = yf.download(ticker, period='7d', interval='5m')
    temp.dropna(how="any", inplace=True)
    temp = temp.between_time("09:35", "16:00")
    clhv[ticker] = temp


 ############################ BACKTESTING ###############################
 
 
ohlc_dict = copy.deepcopy(clhv)
tickers_signal = {}
tickers_ret = {}
 
 
for ticker in stocks:
    print("calculating ATR and rolling price for ", ticker)
    ohlc_dict[ticker]["ATR"] = ATR(ohlc_dict[ticker], 20)
    ohlc_dict[ticker]["roll_max_cp"] = ohlc_dict[ticker]["High"].rolling(20).max()
    ohlc_dict[ticker]["roll_min_cp"] = ohlc_dict[ticker]["Low"].rolling(20).min()
    ohlc_dict[ticker]["roll_max_vol"] = ohlc_dict[ticker]["Volume"].rolling(20).max()
    ohlc_dict[ticker].dropna(inplace=True)
    tickers_signal[ticker] = ""
    tickers_ret[ticker] = []

    


# identifying signals and calculating daily return (stop loss is factored in)

for ticker in stocks:
    print("calculating returns for ",ticker)
    for i in range(len(ohlc_dict[ticker])):
        if tickers_signal[ticker] == "":
            tickers_ret[ticker].append(0)
            if ohlc_dict[ticker]["High"][i]>=ohlc_dict[ticker]["roll_max_cp"][i] and \
               ohlc_dict[ticker]["Volume"][i]>=1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]:
                   tickers_signal[ticker] = "Buy"
            elif ohlc_dict[ticker]["Low"][i]<=ohlc_dict[ticker]["roll_min_cp"][i] and \
               ohlc_dict[ticker]["Volume"][i]>=1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]:
                   tickers_signal[ticker] = "Sell"
        
        
        elif tickers_signal[ticker] == "Buy":
            if ohlc_dict[ticker]["Low"][i]<ohlc_dict[ticker]["Close"][i-1] - ohlc_dict[ticker]["ATR"][i-1]:
                tickers_signal[ticker] = ""
                tickers_ret[ticker].append(((ohlc_dict[ticker]["Close"][i-1] - ohlc_dict[ticker]["ATR"][i-1])/ohlc_dict[ticker]["Close"][i-1])-1)
            elif ohlc_dict[ticker]["Low"][i]<=ohlc_dict[ticker]["roll_min_cp"][i] and \
                ohlc_dict[ticker]["Volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]:
                tickers_signal[ticker] = "Sell"
                tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i]/ohlc_dict[ticker]["Close"][i-1])-1)
            else:
                tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i]/ohlc_dict[ticker]["Close"][i-1])-1)
        
        
        elif tickers_signal[ticker] == "Sell":
            if ohlc_dict[ticker]["High"][i]>ohlc_dict[ticker]["Close"][i-1] - ohlc_dict[ticker]["ATR"][i-1]:
                tickers_signal[ticker] = ""
                tickers_ret[ticker].append(((ohlc_dict[ticker]["Close"][i-1] - ohlc_dict[ticker]["ATR"][i-1])/ohlc_dict[ticker]["Close"][i-1])-1)
            elif ohlc_dict[ticker]["High"][i]>=ohlc_dict[ticker]["roll_max_cp"][i] and \
                ohlc_dict[ticker]["Volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]:
                tickers_signal[ticker] = "Buy"
                tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i]/ohlc_dict[ticker]["Close"][i-1])-1)
            else:
                tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i]/ohlc_dict[ticker]["Close"][i-1])-1)
                
    ohlc_dict[ticker]["ret"] = np.array(tickers_ret[ticker])
                
            
strategy_df = pd.DataFrame()
for ticker in stocks:
    strategy_df[ticker] = ohlc_dict[ticker]["ret"]


strategy_df["ret"] = strategy_df.mean(axis=1)
CAGR(strategy_df)
Sharpe(strategy_df,0.025)

# Visualization
(1+strategy_df["ret"]).cumprod().plot()



 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 











    
    