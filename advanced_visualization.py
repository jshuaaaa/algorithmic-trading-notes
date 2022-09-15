import datetime as dt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

stocks = ["AMZN", "META", "GOOG"]

start = dt.datetime.today()-dt.timedelta(4500)
end = dt.datetime.today()
cl_price = pd.DataFrame()
clhv = {}

for ticker in stocks:
    cl_price[ticker] = yf.download(ticker,start,end)["Adj Close"]
    
    
cl_price.dropna(axis=0,how="any", inplace=True)

daily_return = cl_price.pct_change() # returns percentage for each return from day to day

cumulative_return = (daily_return+1).cumprod()

fig, ax = plt.subplots()
ax.set(title="Mean Daily Return", xlabel = "Stocks", ylabel="Mean Return")
plt.style.available
plt.style.use("ggplot")

plt.bar(x=cumulative_return.columns, height=cumulative_return.mean())
