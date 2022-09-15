import datetime as dt
import yfinance as yf
import pandas as pd


stocks = ["AMZN", "META", "GOOG"]

start = dt.datetime.today()-dt.timedelta(4500)
end = dt.datetime.today()
cl_price = pd.DataFrame()
clhv = {}

for ticker in stocks:
    cl_price[ticker] = yf.download(ticker,start,end)["Adj Close"]
    
    
cl_price.fillna(method="bfill", axis=0, inplace=True)
# Fills NaN values
#Fillna is best method because it lets you get data of stocks that arent NaN
#Since change will be 0 our backtest wont net a profit so this is most optimal

cl_price.dropna(inplace=True)
# Drops NaN values
