
import yfinance as yf
import numpy as np
import pandas as pd
import talib
import copy
import datetime as dt
import matplotlib.pyplot as plt
import time
from stocktrends import Renko
import statsmodels.api as sm

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

def renko_DF(DF):
    df = DF.copy()
    df.reset_index(inplace=True)
    df.drop("Close", axis=1, inplace=True)
    df.iloc[:,[0,1,2,3,4,5]]
    df.columns = ["date", "open", "high", "low", "close", "volume"] # Making columns stocktrends compatible
    df2 = Renko(df)
    df2.brick_size = max(0.5,round(ATR(DF,120).iloc[-1], 0))
    renko_df = df2.get_ohlc_data()
    renko_df["bar_num"] = np.where(renko_df["uptrend"]==True,1,np.where(renko_df["uptrend"]==False,-1,0))
    for i in range(1,len(renko_df["bar_num"])):
        if renko_df["bar_num"][i] >0 and renko_df["bar_num"][i-1]>0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
        elif renko_df["bar_num"][i]<0 and renko_df["bar_num"][i-1]<0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
    renko_df.drop_duplicates(subset="date",keep="last",inplace=True)
    return renko_df



def slope(ser,n):
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)

def OBV(DF):
    df = DF.copy()
    df["daily_ret"] = df["Adj Close"].pct_change()
    df["direction"] = np.where(df["daily_ret"]>=0,1,-1)
    df["direction"][0] = 0
    df["vol_adj"] = df["Volume"] = df["direction"]
    df["obv"] = df["vol_adj"].cumsum()
    return df["obv"]


# Download Data

for ticker in stocks:
    temp = yf.download(ticker, period='7d', interval='5m')
    temp.dropna(how="any", inplace=True)
    temp = temp.between_time("09:35", "16:00")
    clhv[ticker] = temp


 ############################ BACKTESTING ###############################
 
# Merging renko df with original df
ohlc_renko = {}
df = copy.deepcopy(clhv)
tickers_signal = {}
tickers_ret = {}
for ticker in stocks:
    print("merging for ", ticker)
    renko = renko_DF(df[ticker])
    df[ticker]["date"] = df[ticker].index
    ohlc_renko[ticker] = df[ticker].merge(renko.loc[:,["date", "bar_num"]], how="outer", on="date")
    ohlc_renko[ticker]["bar_num"].fillna(method="ffill", inplace=True)
    ohlc_renko[ticker]["obv"] = OBV(ohlc_renko[ticker])
    ohlc_renko[ticker]["obv_slope"] = slope(ohlc_renko[ticker]["obv"],5)
    tickers_signal[ticker] = ""
    tickers_ret[ticker] = []
 
    
#Identifying signals and calculating daily return
for ticker in stocks:
    print("calculating returns for ", ticker)
    for i in range(len(clhv[ticker])):
        if tickers_signal[ticker] == "":
            tickers_ret[ticker].append(0)
            if ohlc_renko[ticker]["bar_num"][i]>=2 and ohlc_renko[ticker]["obv_slope"][i]>30:
                tickers_signal[ticker] = "Buy"
            elif ohlc_renko[ticker]["bar_num"][i]<=2 and ohlc_renko[ticker]["obv_slope"][i]<-30:
                tickers_signal[ticker] = "Sell"
        
        elif tickers_signal[ticker] == "Buy":
            tickers_ret[ticker].append((ohlc_renko[ticker]["Adj Close"][i]/ohlc_renko[ticker]["Adj Close"][i-1])-1)
            if ohlc_renko[ticker]["bar_num"][i]<=-2 and ohlc_renko[ticker]["obv_slope"][i]<-30:
                tickers_signal[ticker] = "Sell"
            elif ohlc_renko[ticker]["bar_num"][i] <2:
                tickers_signal[ticker] = ""
        
        elif tickers_signal[ticker] == "Sell":
            tickers_ret[ticker].append((ohlc_renko[ticker]["Adj Close"][i-1]/ohlc_renko[ticker]["Adj Close"][i])-1)
            if ohlc_renko[ticker]["bar_num"][i]>=2 and ohlc_renko[ticker]["obv_slope"][i]>30:
                tickers_signal[ticker] = "Buy"
            elif ohlc_renko[ticker]["bar_num"][i] >-2:
                tickers_signal[ticker] = ""
    ohlc_renko[ticker]["ret"] = np.array(tickers_ret[ticker])
    

#calculating overall strategy's KPIs
strategy_df = pd.DataFrame()
for ticker in stocks:
    strategy_df[ticker] = ohlc_renko[ticker]["ret"]
strategy_df["ret"] = strategy_df.mean(axis=1)
CAGR(strategy_df)
Sharpe(strategy_df,0.025)
maximum_drawdown(strategy_df)  

#visualizing strategy returns
(1+strategy_df["ret"]).cumprod().plot()

#calculating individual stock's KPIs
cagr = {}
sharpe_ratios = {}
max_drawdown = {}
for ticker in stocks:
    print("calculating KPIs for ",ticker)      
    cagr[ticker] =  CAGR(ohlc_renko[ticker])
    sharpe_ratios[ticker] =  Sharpe(ohlc_renko[ticker],0.025)
    max_drawdown[ticker] =  maximum_drawdown(ohlc_renko[ticker])

KPI_df = pd.DataFrame([cagr,sharpe_ratios,max_drawdown],index=["Return","Sharpe Ratio","Max Drawdown"])      
KPI_df.T

            
                
            
            

 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 











    
    