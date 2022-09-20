
import yfinance as yf


stocks = ["AMZN", "META", "GOOG"]
clhv = {}

for ticker in stocks:
    temp = yf.download(ticker, period='1mo', interval='15m')
    temp.dropna(how="any", inplace=True)
    clhv[ticker] = temp
# For loop to get our data

#Bolinger Bands Calculatiosn
# Middle Band - 20 Day Simple Moving Average
# Upper Band - 20 Day Simple Moving Average +  (Standard Deviation x 2)
# Lower Band - 20 Day Simple Moving Average -  (Standard Deviation x 2)


   
def Bollinger_Band(DF, n=14):
    df = DF.copy()
    df["mid-band"] = df["Adj Close"].rolling(n).mean()
    df["up-band"] = df["mid-band"] + 2 * df["Adj Close"].rolling(n).std(ddof=0)
    df["low-band"] = df["mid-band"] - 2 * df["Adj Close"].rolling(n).std(ddof=0)
    df["BB_WIDTH"] = df["up-band"] - df["low-band"]
    return df[["mid-band", "up-band", "low-band", "BB_WIDTH"]]
    
    
for ticker in clhv:
    clhv[ticker][["mid-band", "up-band", "low-band", "BB_WIDTH"]] = Bollinger_Band(clhv[ticker],20)