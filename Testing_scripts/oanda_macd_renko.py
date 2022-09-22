
import oandapyV20
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trade
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
import numpy as np
from stocktrends import Renko
import statsmodels.api as sm
import time
import copy

token_path = "D:\My Apps\API-KEYS\oanda.txt"
client = oandapyV20.API(access_token=open(token_path, "r").read(),environment="practice")
account_id = "101-001-23303695-001"

# define strategy parameters
pairs = ['EUR_NZD', 'EUR_NOK','NZD_JPY', 'USD_CAD', 'GBP_USD', 'AUD_USD']
pos_size = 100



# indicators
def ATR(DF, n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['h']-df['l'])
    df['H-PC']=abs(df['h']-df['c'].shift(1))
    df['L-PC']=abs(df['l']-df['c'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2

def renko_DF(DF):
    df = DF.copy()
    df.reset_index(inplace=True)
    df.iloc[:,[0,1,2,3,4,5]]
    df.columns = ["date", "open", "high", "low", "close", "volume"] # Making columns stocktrends compatible
    df2 = Renko(df)
    df2.brick_size = round(ATR(DF,120)["ATR"][-1],4)
    renko_df = df2.get_ohlc_data()
    renko_df["bar_num"] = np.where(renko_df["uptrend"]==True,1,np.where(renko_df["uptrend"]==False,-1,0))
    for i in range(1,len(renko_df["bar_num"])):
        if renko_df["bar_num"][i] >0 and renko_df["bar_num"][i-1]>0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
        elif renko_df["bar_num"][i]<0 and renko_df["bar_num"][i-1]<0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
    renko_df.drop_duplicates(subset="date",keep="last",inplace=True)
    return renko_df


def MACD(DF,a=12,b=26,c=9):
    df = DF.copy()
    df["ma_fast"] = df["c"].ewm(span=a, min_periods=a).mean()
    df["ma_slow"] = df["c"].ewm(span=b, min_periods=b).mean()
    df["macd"] = df["ma_fast"] - df["ma_slow"]
    df["signal"] = df["macd"].ewm(span=c, min_periods=c).mean()
    return (df["macd"],df["signal"])

def slope(ser,n):
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)


def renko_merge(DF):
    df = copy.deepcopy(DF)
    renko = renko_DF(df)
    df["date"] = df.index
    ohlc_renko = df.merge(renko.loc[:,["date", "bar_num"]], how="outer", on="date")
    ohlc_renko["bar_num"].fillna(method="ffill", inplace=True)
    ohlc_renko["macd"] = MACD(ohlc_renko)[0]
    ohlc_renko["macd_sig"] = MACD(ohlc_renko)[1]
    ohlc_renko["macd_slope"] = slope(ohlc_renko["macd"], 5)
    ohlc_renko["macd_sig_slope"] = slope(ohlc_renko["macd_sig"], 5)
    return ohlc_renko
    

def trade_signal(MERGED_DF,l_s):
    signal = ""
    df = copy.deepcopy(MERGED_DF)
    if l_s == "":
        if df["bar_num"].tolist()[-1]>=2 and df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
            signal = "Buy"
        elif df["bar_num"].tolist()[-1]<=-2 and df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
            signal = "Sell"
        
    elif l_s == "long":
        if df["bar_num"].tolist()[-1]<=-2 and df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
            signal = "Close_Sell"
        elif df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
            signal = "Close"
        
    elif l_s == "short":
            if df["bar_num"].tolist()[-1]>=2 and df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
                signal = "Close_Buy"
            elif df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
                signal = "Close"
    return signal


def market_order(instrument,units,sl):
    """units can be positive or negative, stop loss (in pips) added/subtracted to price """  
    account_id = "101-001-23303695-001"
    data = {
            "order": {
            "price": "",
            "stopLossOnFill": {
            "trailingStopLossOnFill": "GTC",
            "distance": str(sl)
                              },
            "timeInForce": "FOK",
            "instrument": str(instrument),
            "units": str(units),
            "type": "MARKET",
            "positionFill": "DEFAULT"
                    }
            }
    r = orders.OrderCreate(accountID=account_id, data=data)
    client.request(r)


def main():
    try:
        for currency in pairs:
            print("Looking for trades for", currency)
            params = {"instrument": currency}
            r = trade.TradesList(accountID=account_id,params=params)
            open_pos = client.request(r)
            long_short = ""
            if len(open_pos["trades"])>0:
                if int(open_pos['trades'][0]['initialUnits']) > 0:
                    long_short = "long"
                else:
                    long_short='short'
                
            params = {"count":250,"granularity": "M5"}
            candles = instruments.InstrumentsCandles(instrument=currency, params=params)
            client.request(candles)
            ohlc_dict = candles.response["candles"]
            temp = pd.DataFrame(ohlc_dict)
            ohlc_df = temp.mid.dropna().apply(pd.Series)
            ohlc_df["volume"] = temp["volume"]
            ohlc_df.index = temp["time"]
            ohlc_df = ohlc_df.apply(pd.to_numeric)
            
            
            signal = trade_signal(renko_merge(ohlc_df),long_short)
            
            if signal == "Buy":
                market_order(currency,pos_size,3*ATR(ohlc_df,120))
                print("New long position initiated for ", currency)
            
            elif signal == "Sell":
                market_order(currency,-1*pos_size,3*ATR(ohlc_df,120))
                print("New short position initiated for ", currency)
                
                
            elif signal == "Close_Buy":
                market_order(currency,pos_size,3*ATR(ohlc_df,120))
                market_order(currency,pos_size,3*ATR(ohlc_df,120))
                print("New long position initiated for ", currency)
            
            elif signal == "Close":
                cl = trade.TradeClose(accountID=account_id, tradeID=open_pos['trades'][0]['id'])
                client.request(cl)
                print('position closed')
            
            elif signal == "Close_Sell":
                market_order(currency,-1*pos_size,3*ATR(ohlc_df,120))
                market_order(currency,-1*pos_size,3*ATR(ohlc_df,120))
                print("New short position initiated for ", currency)
            

    except:
        print("error encountered....skipping this iteration")


starttime=time.time()
timeout = time.time() + 60*60*8  # 60 seconds times 60 times 8 meaning the script will run for 8 hrs
while time.time() <= timeout:
    try:
        print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        main()
        time.sleep(300 - ((time.time() - starttime) % 300.0)) # 5 minute interval between each new execution
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()
                
                
        


























