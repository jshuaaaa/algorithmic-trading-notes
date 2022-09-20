

# importing libraries
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import time
ts = TimeSeries(key="API_KEY", output_format="pandas")

data = ts.get_daily(symbol="MSFT", outputsize="full")[0]
data.columns = ["open", "high", "low", "close", "volume"]

all_tickers = ["GOOG", "MSFT", "AMZN"]
close_prices = pd.DataFrame()
api_call_count = 0
# Setting tickers and creatign dataframe

for ticker in all_tickers: 
    starttime=time.time()
    # Sets current time
    ts = TimeSeries(key="API_KEY", output_format="pandas")
    data = ts.get_intraday(symbol=ticker, interval='15min', outputsize='full')[0]
    api_call_count+=1
    data.columns = ["open", "high", "low", "close", "volume"]
    close_prices[ticker] = data["close"]
    # Adds to close price to the dataframe for each ticker
    if api_call_count==5:
        api_call_count = 0
        time.sleep(60 - (time.time()-start_time))
        #AlphaVantage has a timelimit this if statement allows our program to wait for the api call to be available again