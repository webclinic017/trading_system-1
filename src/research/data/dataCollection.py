#%%
import yfinance as yf
import pandas as pd

def downloadOhlcvData(ticker, start, end):
    try:
        data = yf.download(ticker, start, end)
        print("Downloading {} ohlcv data".format(ticker))
        return data;
    except Exception as e:
        print("Error downloading {} ohlcv data: {}".format(ticker, e))


def saveData(data, filename):
    try:
        data.to_csv("./data/{}.csv".format(filename))
        print("Saved {} ohlcv data".format(filename))
    except Exception as e:
        print("Error saving {}.csv: {}".format(filename, e))


def openData(filename):
    data = pd.DataFrame()
    try:
        data = pd.read_csv("./data/{}.csv".format(filename), index_col=0)
        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        print("Error opening {}.csv: {}".format(filename, e))
# %%
tickers = ["AAPL", "MSFT"]

start = pd.datetime(2005,1,1)
end = pd.to_datetime("today").normalize()
data = pd.DataFrame()

for ticker in tickers:
    data = downloadOhlcvData(ticker, start, end)
    saveData(data, ticker)
# %%
