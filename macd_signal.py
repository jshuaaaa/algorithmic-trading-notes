
import yfinance as yf


stocks = ["AMZN", "META", "GOOG"]
clhv = {}

for ticker in stocks:
    temp = yf.download(ticker, period='1mo', interval='15m')
    temp.dropna(how="any", inplace=True)
    clhv[ticker] = temp
# For loop to get our data
    

# MACD Calculations
# MACD Line: (12-day EMA - 26-day EMA)
# Signal Line: 9-day EMA of MACD Line
# MACD Histogram: MACD Line - Signal Line

# Function to create MACD Column and Signal line
def MACD(DF,a=12,b=26,c=9):
    df = DF.copy()
    df["ma_fast"] = df["Adj Close"].ewm(span=a, min_periods=a).mean()
    df["ma_slow"] = df["Adj Close"].ewm(span=b, min_periods=b).mean()
    df["macd"] = df["ma_fast"] - df["ma_slow"]
    df["signal"] = df["macd"].ewm(span=c, min_periods=c).mean()
    
    return df.loc[:,["macd", "signal"]]
 
# Adding the MACD and SIGNAL column to our dataframe   
for ticker in clhv:
    clhv[ticker][["MACD", "SIGNAL"]] = MACD(clhv[ticker])