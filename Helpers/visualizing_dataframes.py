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
    
    
cl_price.dropna(axis=0,how="any", inplace=True)

daily_return = cl_price.pct_change() # returns percentage for each return from day to day

cl_price.plot(subplots=True, title="This is so cool") # Charts the data

daily_return.plot(subplots=True) # graphs daily return

cumulative_return = (1+daily_return).cumprod() # gets cumulative daily return

cumulative_return.plot() # graphs it