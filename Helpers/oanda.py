
import oandapyV20
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.instruments as instruments
import pandas as pd


token_path = "D:\My Apps\API-KEYS\oanda.txt"
client = oandapyV20.API(access_token=open(token_path, "r").read(),environment="practice")


# get historical data
params = {"count":150,"granularity": "M5"}
candles = instruments.InstrumentsCandles(instrument="USD_JPY", params=params)
client.request(candles)
print(candles.response)
ohlc_dict = candles.response["candles"]
ohlc = pd.DataFrame(ohlc_dict)
ohlc_df = ohlc.mid.dropna().apply(pd.Series)
ohlc_df["volume"] = ohlc["volume"]
ohlc_df.index = ohlc["time"]
ohlc_df = ohlc_df.apply(pd.to_numeric)

# streaming data
params = {"instruments": "USD_JPY"}
account_id = "101-001-23303695-001"
r = pricing.PricingInfo(accountID=account_id, params=params)
i=0
while i<=20:
    rv = client.request(r)
    print("Time= ",rv['time'])
    print("Bid= ",rv["prices"][0]["closeoutBid"])
    print("Ask= ",rv["prices"][0]["closeoutAsk"])
    print("*****************************")
    i+=1


# account details

r = accounts.AccountDetails(accountID=account_id)
client.request(r)
print(r.response)


# trading account summary

r = accounts.AccountSummary(accountID=account_id)
client.request(r)
print(r.response)


# orders

data = {
        "order": {
        "price": "1.15",
        "stopLossOnFill": {
        "timeInForce": "GTC",
        "price": "1.2"
                          },
        "timeInForce": "FOK",
        "instrument": "USD_CAD",
        "units": "100",
        "type": "MARKET",
        "positionFill": "DEFAULT"
                }
        }
            
r = orders.OrderCreate(accountID=account_id, data=data)
client.request(r)

# dynamically setting orders

def ATR(DF, n=14):
    df = DF.copy()
    df["H-L"] = df["h"] - df["l"]
    df["H-PC"] = df["h"] - df["c"].shift(1)
    df["L-PC"] = df["l"] - df["c"].shift(1)
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df["ATR"] = df["TR"].ewm(com=n, min_periods=n).mean() # Use com for atr instead of span as it makes data more accurate
    df2 = df.drop(["H-L", 'H-PC', "L-PC"], axis=1)
    return round(df2["ATR"][-1],2)


def market_order(instrument,units,sl):
    params = {"instruments": instrument}
    account_id = "101-001-23303695-001"
    r = pricing.PricingInfo(accountID=account_id, params=params)
    rv = client.request(r)
    if units > 0:
        price = float(rv["prices"][0]["closeoutAsk"])
        st_ls = price - sl
    else:
        price = float(rv["prices"][0]["closeoutBid"])
        st_ls = price + sl
        
    
    data = {
            "order": {
            "price": "1.15",
            "stopLossOnFill": {
            "timeInForce": "GTC",
            "price": str(st_ls)
                              },
            "timeInForce": "FOK",
            "instrument": str(instrument),
            "units": str(units),
            "type": "MARKET",
            "positionFill": "DEFAULT"
                    }
            }
    return data

r = orders.OrderCreate(accountID=account_id, data=market_order("USD_CAD",100,3*ATR(ohlc_df,120)))
client.request(r)


# check trades
r = trades.OpenTrades(accountID=account_id)
client.request(r)





