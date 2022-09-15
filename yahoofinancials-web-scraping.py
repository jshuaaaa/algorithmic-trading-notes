import pandas as pd
from yahoofinancials import YahooFinancials
import datetime

all_tickers = ["GOOG", 'AAPL', "AMZN"]
# array of tickers

close_prices = pd.DataFrame()
end_date = (datetime.date.today()).strftime('%Y-%m-%d')
beg_date = (datetime.date.today()-datetime.timedelta(60)).strftime('%Y-%m-%d')
#Date Formatting

for ticker in all_tickers:
    yahoo_financials = YahooFinancials(ticker)
    # Creates the yahoo finance data
    json_obj = yahoo_financials.get_historical_price_data(beg_date, end_date, "daily")
    # Creates a JSON of the data parsed based on the dates we created
    ohlv = json_obj[ticker]["prices"]
    # parses through the JSON to only get prices column for each ticker
    temp = pd.DataFrame(ohlv)[["formatted_date", "adjclose"]]
    # Creates a DataFrame with only those two values
    temp.set_index("formatted_date", inplace=True)
    # Makes the index column "formatted_date"
    temp.dropna(inplace=True)
    # If stock ticker has a NaN value for the price, this will drop that value
    close_prices[ticker] = temp["adjclose"]
    # Updates are data frame