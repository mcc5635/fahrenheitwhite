import pytz
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

def get_sp500_tickers():
    res = requests.get("https://en.wikipedia.org/wiki/List_of_S&P_500_companies")
    soup = BeautifulSoup(res.content,'html')
    table = soup.find_all('table')[0]
    df = pd.read_html(str(table))
    tickers = list(df[0].Symbol)
    return tickers

def get_history(ticker, period_start, period_end, granularity="1d"):
    import yfinance
    df = yfinance.Ticker(ticker).history(
        start=period_start,
        end=period_end,
        interval=granularity,
        auto_adjust=True
    ).reset_index()
    df = df.rename(columns={
        "Date":"datetime",
        "Open":"open",
        "High":"high",
        "Low":"low",
        "Close":"close",
        "Volume":"volume",
    })
    if df.empty:
        return pd.DataFrame()
    
    df["datetime"] = df["datetime"].dt.tz_localize(pytz.utc)
    df = df.drop(columns=["Dividends", "Stock Splits"])
    df = df.set_index("datetime",drop=True)
    return df

import pytz
from datetime import datetime

period_start = datetime(2010,1,1, tzinfo=pytz.utc)
period_end = datetime(2020,1,1, tzinfo=pytz.utc)
tickers = get_sp500_tickers()

import threading
def get_histories(tickers, period_starts, period_ends, granularity="1d"):
    dfs = [None]*len(tickers)
    def _helper(i):
        print(tickers[i])
        df = get_history(
            tickers[i],
            period_starts[i], 
            period_ends[i], 
            granularity=granularity
        )
        dfs[i] = df
    threads = [threading.Thread(target=_helper,args=(i,)) for i in range(len(tickers))]
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
    tickers = [tickers[i] for i in range(len(tickers)) if not dfs[i].empty]
    dfs = [df for df in dfs if not df.empty]
    return tickers, dfs

def get_ticker_dfs(start,end):
    tickers = get_sp500_tickers()
    starts=[start]*len(tickers)
    ends=[end]*len(tickers)
    tickers,dfs = get_histories(tickers,starts,ends,granularity="1d")
    return tickers, {ticker:df for ticker,df in zip(tickers,dfs)}

period_start = datetime(2010,1,1, tzinfo=pytz.utc)
period_end = datetime(2020,1,1, tzinfo=pytz.utc)
#dfs = get_histories(tickers, period_starts=[period_start]*len(tickers), period_ends=[period_end]*len(tickers))
tickers, ticker_dfs = get_ticker_dfs(start=period_start,end=period_end)
print(ticker_dfs)
