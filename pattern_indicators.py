
import yfinance as yf
import numpy as np
import talib
import copy

stocks = ["AMZN", "META", "GOOG"]
clhv = {}


for ticker in stocks:
    temp = yf.download(ticker, period='1y', interval='1d')
    temp.dropna(how="any", inplace=True)
    clhv[ticker] = temp



tech_copy =  copy.deepcopy(clhv)

for ticker in stocks:
    tech_copy[ticker]["3Inside"] = talib.CDL3INSIDE(tech_copy[ticker]["Open"],
                                                    tech_copy[ticker]["High"],
                                                    tech_copy[ticker]["Low"],
                                                    tech_copy[ticker]["Adj Close"])



    
    