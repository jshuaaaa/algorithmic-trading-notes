
import yfinance as yf
import numpy as np
import pandas as pd
import talib
import copy
import datetime as dt
import matplotlib.pyplot as plt

stocks = ["AMZN", "META", "GOOG", "MMM", "AXP", "BA",
          "CAT", "CVX", "CSCO", "3988.HK", "CVNA"]
clhv = {}


for ticker in stocks:
    temp = yf.download(ticker, period='5y', interval='1mo')
    temp.dropna(how="any", inplace=True)
    clhv[ticker] = temp
    

def CAGR(DF):
    df = DF.copy()
    df["cum_return"] = (1+df["mon_ret"]).cumprod()
    n = len(df)/252
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    df = DF.copy()
    vol = df["mon_ret"].std() * np.sqrt(252) # annualized volatility
    return vol



def Sharpe(DF, rf):
    df = DF.copy()
    sharpe = (CAGR(df) - rf) / volatility(df)
    return sharpe


def maximum_drawdown(DF):
    df = DF.copy()
    df["cum_return"] = (1+df["mon_ret"]).cumprod()
    df["cum_rolling_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_rolling_max"] - df["cum_return"]
    return (df["drawdown"]/df["cum_rolling_max"]).max()
    
 ############################ BACKTESTING ###############################
 
clhv_dct = copy.deepcopy(clhv)
return_df = pd.DataFrame()
 
for ticker in stocks:
     print("Calculating monthly return for ", ticker)
     clhv_dct[ticker]["return"] = clhv_dct[ticker]["Adj Close"].pct_change()
     return_df[ticker] = clhv_dct[ticker]["return"]




def pflio(DF,m,x):
    # DF = dataframe with return information
    # m = number of stocks in the portfolio
    # x = number of underperforming stocks to be removed monthly
    df = DF.copy()
    portfolio = []
    monthly_ret = [0]
    
    for i  in range(1,len(df)):
        if len(portfolio) > 0:
            monthly_ret.append(df[portfolio].iloc[i,:].mean())
            bad_stocks = df[portfolio].iloc[i,:].sort_values(ascending=True)[:x].index.values.tolist()
            portfolio = [t for t in portfolio if t not in bad_stocks]
        fill = m - len(portfolio)
        new_picks = df.iloc[i,:].sort_values(ascending=False)[:fill].index.values.tolist()
        portfolio = portfolio + new_picks
        print(portfolio)
    monthly_ret_df = pd.DataFrame(np.array(monthly_ret), columns=["mon_ret"])
    return monthly_ret_df


CAGR(pflio(return_df,6,3))
Sharpe(pflio(return_df,6,3), 0.025)    
maximum_drawdown(pflio(return_df,6,3))  

DJI = yf.download("^DJI", period='5y', interval='1mo')
DJI["mon_ret"] = DJI["Adj Close"].pct_change()

# visualization comparing our select stocks vs Dao Jones Index

fig, ax = plt.subplots()
plt.plot((1+pflio(return_df, 6, 3)).cumprod())
plt.plot((1+DJI["mon_ret"])[2:].reset_index(drop=True).cumprod())
ax.legend(["Strategy Return", "DJI Return"])





















    
    