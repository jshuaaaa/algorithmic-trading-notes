
import yfinance as yf


stocks = ["AMZN", "META", "GOOG"]
clhv = {}

for ticker in stocks:
    temp = yf.download(ticker, period='1mo', interval='15m')
    temp.dropna(how="any", inplace=True)
    clhv[ticker] = temp
# For loop to get our data
    
# Function adding ATR to our dataframe
def ATR(DF, n=14):
    df = DF.copy()
    df["H-L"] = df["High"] - df["Low"]
    df["H-PC"] = df["High"] - df["Adj Close"].shift(1)
    df["L-PC"] = df["Low"] - df["Adj Close"].shift(1)
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df["ATR"] = df["TR"].ewm(com=n, min_periods=n).mean() # Use com for atr instead of span as it makes data more accurate
    return df["ATR"]

for ticker in clhv:
    clhv[ticker]["ATR"] = ATR(clhv[ticker])