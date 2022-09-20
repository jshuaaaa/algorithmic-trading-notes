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


cl_price.mean()
cl_price.std()
cl_price.median()
cl_price.describe()
cl_price.head() # Prints first 5 rows, you can provide an argument to change the amount
cl_price.tail() # Prints last 5 rows, works same way as head

daily_return = cl_price.pct_change() # returns percentage for each return from day to day
cl_price/cl_price.shift(1) - 1 # divides cl_price index by previous index and finds returns manually

daily_return.mean() # Calculates daily return mean

daily_return.std() # Calculates standard deviation of stocks based on daily return